"""
Design Validator for Adobe Illustrator MCP Server
Provides automatic design quality validation and issue detection
"""

from typing import List, Dict, Any, Optional
import json


class DesignValidator:
    """Validates design quality by checking alignment, spacing, margins, and more."""

    # Validation thresholds
    ALIGNMENT_TOLERANCE_PT = 2.0  # Points tolerance for alignment
    SPACING_VARIANCE_THRESHOLD = 0.15  # 15% variance allowed
    MIN_MARGIN_MM = 3.0  # Minimum safe margin in mm

    # Points to mm conversion
    PT_TO_MM = 0.352778
    MM_TO_PT = 2.834645669

    def __init__(self, document_info: Dict[str, Any]):
        """
        Initialize validator with document information.

        Args:
            document_info: Document info from get_document_info tool
        """
        self.doc_info = document_info
        self.issues: List[Dict[str, Any]] = []
        self.score = 100

    def _get_elements(self) -> List[Dict[str, Any]]:
        """Extract all elements from document info."""
        elements = []
        for layer in self.doc_info.get("layers", []):
            for obj in layer.get("objects", []):
                obj["layer_name"] = layer.get("name", "")
                elements.append(obj)
        return elements

    def _pt_to_mm(self, pt: float) -> float:
        """Convert points to millimeters."""
        return pt * self.PT_TO_MM

    def _mm_to_pt(self, mm: float) -> float:
        """Convert millimeters to points."""
        return mm * self.MM_TO_PT

    def check_alignment(self, tolerance_pt: float = None) -> List[Dict[str, Any]]:
        """
        Check for alignment issues between elements.

        Detects:
        - Near-aligned elements that should be exactly aligned
        - Elements with similar positions that could be grouped

        Args:
            tolerance_pt: Custom tolerance in points

        Returns:
            List of alignment issues found
        """
        tolerance = tolerance_pt or self.ALIGNMENT_TOLERANCE_PT
        elements = self._get_elements()
        issues = []

        # Group elements by approximate positions
        left_positions = {}
        top_positions = {}
        right_positions = {}
        center_x_positions = {}

        for elem in elements:
            if not elem.get("visible", True):
                continue

            left = elem.get("left", 0)
            top = elem.get("top", 0)
            width = elem.get("width", 0)
            height = elem.get("height", 0)

            right = left + width
            center_x = left + width / 2

            # Round to tolerance for grouping
            left_key = round(left / tolerance) * tolerance
            top_key = round(top / tolerance) * tolerance
            right_key = round(right / tolerance) * tolerance
            center_key = round(center_x / tolerance) * tolerance

            left_positions.setdefault(left_key, []).append((elem, left))
            top_positions.setdefault(top_key, []).append((elem, top))
            right_positions.setdefault(right_key, []).append((elem, right))
            center_x_positions.setdefault(center_key, []).append((elem, center_x))

        # Check for near-alignments that should be exact
        def check_near_alignment(positions: Dict, alignment_type: str):
            for key, items in positions.items():
                if len(items) >= 2:
                    values = [v for _, v in items]
                    min_val, max_val = min(values), max(values)
                    diff = max_val - min_val

                    if 0 < diff <= tolerance * 3:  # Nearly aligned but not exact
                        elem_names = [e.get("name", f"element_{e.get('index', '?')}")
                                     for e, _ in items]
                        issues.append({
                            "type": "alignment",
                            "severity": "warning" if diff <= tolerance * 2 else "info",
                            "alignment_type": alignment_type,
                            "elements": elem_names,
                            "difference_pt": round(diff, 2),
                            "difference_mm": round(self._pt_to_mm(diff), 2),
                            "message": f"Elements nearly {alignment_type}-aligned (off by {round(diff, 1)}pt)",
                            "suggestion": f"Align {alignment_type} edges of these elements"
                        })

        check_near_alignment(left_positions, "left")
        check_near_alignment(top_positions, "top")
        check_near_alignment(right_positions, "right")
        check_near_alignment(center_x_positions, "center")

        self.issues.extend(issues)
        return issues

    def check_spacing(self, expected_spacing_pt: float = None) -> List[Dict[str, Any]]:
        """
        Check spacing consistency between elements.

        Args:
            expected_spacing_pt: Expected spacing value in points

        Returns:
            List of spacing issues found
        """
        elements = self._get_elements()
        issues = []

        # Sort elements by position for spacing analysis
        visible_elements = [e for e in elements if e.get("visible", True)]

        if len(visible_elements) < 2:
            return issues

        # Calculate horizontal spacing between adjacent elements
        sorted_by_left = sorted(visible_elements, key=lambda e: e.get("left", 0))
        h_spacings = []

        for i in range(len(sorted_by_left) - 1):
            curr = sorted_by_left[i]
            next_elem = sorted_by_left[i + 1]

            curr_right = curr.get("left", 0) + curr.get("width", 0)
            next_left = next_elem.get("left", 0)
            spacing = next_left - curr_right

            if spacing > 0:  # Only consider non-overlapping elements
                h_spacings.append({
                    "elements": [
                        curr.get("name", f"element_{curr.get('index', '?')}"),
                        next_elem.get("name", f"element_{next_elem.get('index', '?')}")
                    ],
                    "spacing": spacing
                })

        # Check for inconsistent spacing
        if h_spacings:
            spacing_values = [s["spacing"] for s in h_spacings]
            avg_spacing = sum(spacing_values) / len(spacing_values)

            for s in h_spacings:
                variance = abs(s["spacing"] - avg_spacing) / avg_spacing if avg_spacing > 0 else 0

                if variance > self.SPACING_VARIANCE_THRESHOLD:
                    issues.append({
                        "type": "spacing",
                        "severity": "warning" if variance > 0.3 else "info",
                        "elements": s["elements"],
                        "actual_spacing_pt": round(s["spacing"], 2),
                        "expected_spacing_pt": round(avg_spacing, 2),
                        "variance_percent": round(variance * 100, 1),
                        "message": f"Inconsistent horizontal spacing ({round(variance * 100)}% variance)",
                        "suggestion": f"Adjust spacing to approximately {round(avg_spacing, 1)}pt"
                    })

        # Calculate vertical spacing
        sorted_by_top = sorted(visible_elements, key=lambda e: -e.get("top", 0))  # Top is negative in AI
        v_spacings = []

        for i in range(len(sorted_by_top) - 1):
            curr = sorted_by_top[i]
            next_elem = sorted_by_top[i + 1]

            curr_bottom = curr.get("top", 0) - curr.get("height", 0)
            next_top = next_elem.get("top", 0)
            spacing = curr_bottom - next_top

            if spacing > 0:
                v_spacings.append({
                    "elements": [
                        curr.get("name", f"element_{curr.get('index', '?')}"),
                        next_elem.get("name", f"element_{next_elem.get('index', '?')}")
                    ],
                    "spacing": spacing
                })

        # Check vertical spacing consistency
        if v_spacings:
            spacing_values = [s["spacing"] for s in v_spacings]
            avg_spacing = sum(spacing_values) / len(spacing_values)

            for s in v_spacings:
                variance = abs(s["spacing"] - avg_spacing) / avg_spacing if avg_spacing > 0 else 0

                if variance > self.SPACING_VARIANCE_THRESHOLD:
                    issues.append({
                        "type": "spacing",
                        "severity": "warning" if variance > 0.3 else "info",
                        "direction": "vertical",
                        "elements": s["elements"],
                        "actual_spacing_pt": round(s["spacing"], 2),
                        "expected_spacing_pt": round(avg_spacing, 2),
                        "variance_percent": round(variance * 100, 1),
                        "message": f"Inconsistent vertical spacing ({round(variance * 100)}% variance)",
                        "suggestion": f"Adjust spacing to approximately {round(avg_spacing, 1)}pt"
                    })

        self.issues.extend(issues)
        return issues

    def check_margins(self, min_margin_mm: float = None, artboard_index: int = 0) -> List[Dict[str, Any]]:
        """
        Check if elements respect safe margins from artboard edges.

        Args:
            min_margin_mm: Minimum margin in millimeters
            artboard_index: Index of artboard to check

        Returns:
            List of margin issues found
        """
        min_margin = self._mm_to_pt(min_margin_mm or self.MIN_MARGIN_MM)
        issues = []

        # Get artboard bounds
        artboards = self.doc_info.get("artboards", [])
        if not artboards or artboard_index >= len(artboards):
            return issues

        ab = artboards[artboard_index]
        ab_left = ab.get("left", 0)
        ab_top = ab.get("top", 0)
        ab_right = ab.get("right", ab_left + ab.get("width", 0))
        ab_bottom = ab.get("bottom", ab_top - ab.get("height", 0))

        elements = self._get_elements()

        for elem in elements:
            if not elem.get("visible", True):
                continue

            elem_left = elem.get("left", 0)
            elem_top = elem.get("top", 0)
            elem_width = elem.get("width", 0)
            elem_height = elem.get("height", 0)

            elem_right = elem_left + elem_width
            elem_bottom = elem_top - elem_height

            elem_name = elem.get("name", f"element_{elem.get('index', '?')}")

            # Check each edge
            margin_issues = []

            left_margin = elem_left - ab_left
            if left_margin < min_margin and left_margin >= 0:
                margin_issues.append(("left", left_margin))

            right_margin = ab_right - elem_right
            if right_margin < min_margin and right_margin >= 0:
                margin_issues.append(("right", right_margin))

            top_margin = ab_top - elem_top
            if top_margin < min_margin and top_margin >= 0:
                margin_issues.append(("top", top_margin))

            bottom_margin = elem_bottom - ab_bottom
            if bottom_margin < min_margin and bottom_margin >= 0:
                margin_issues.append(("bottom", bottom_margin))

            for edge, margin in margin_issues:
                issues.append({
                    "type": "margin",
                    "severity": "error" if margin < min_margin / 2 else "warning",
                    "element": elem_name,
                    "edge": edge,
                    "actual_margin_pt": round(margin, 2),
                    "actual_margin_mm": round(self._pt_to_mm(margin), 2),
                    "required_margin_mm": round(self._pt_to_mm(min_margin), 2),
                    "message": f"'{elem_name}' too close to {edge} edge ({round(self._pt_to_mm(margin), 1)}mm)",
                    "suggestion": f"Move element at least {round(self._pt_to_mm(min_margin - margin), 1)}mm away from {edge} edge"
                })

        self.issues.extend(issues)
        return issues

    def check_text_issues(self) -> List[Dict[str, Any]]:
        """
        Check for common text-related issues.

        Returns:
            List of text issues found
        """
        elements = self._get_elements()
        issues = []

        text_elements = [e for e in elements if e.get("type") == "TextFrame"]

        for elem in text_elements:
            elem_name = elem.get("name", f"text_{elem.get('index', '?')}")
            font_size = elem.get("fontSize", 0)

            # Check for very small text
            if font_size and font_size < 6:
                issues.append({
                    "type": "text",
                    "severity": "error",
                    "element": elem_name,
                    "issue": "text_too_small",
                    "font_size": font_size,
                    "message": f"Text '{elem_name}' is too small ({font_size}pt)",
                    "suggestion": "Increase font size to at least 6pt for readability"
                })
            elif font_size and font_size < 8:
                issues.append({
                    "type": "text",
                    "severity": "warning",
                    "element": elem_name,
                    "issue": "text_small",
                    "font_size": font_size,
                    "message": f"Text '{elem_name}' may be hard to read ({font_size}pt)",
                    "suggestion": "Consider increasing font size for better readability"
                })

        self.issues.extend(issues)
        return issues

    def check_expected_layout(self, expected_layout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if elements match expected positions.

        Args:
            expected_layout: Dictionary with expected element positions

        Returns:
            List of layout deviation issues
        """
        issues = []
        elements = self._get_elements()
        expected_elements = expected_layout.get("elements", [])

        # Create lookup by name
        element_map = {e.get("name", ""): e for e in elements if e.get("name")}

        for expected in expected_elements:
            name = expected.get("name")
            if not name or name not in element_map:
                issues.append({
                    "type": "layout",
                    "severity": "error",
                    "element": name,
                    "message": f"Expected element '{name}' not found",
                    "suggestion": "Create or rename the element"
                })
                continue

            actual = element_map[name]
            tolerance_mm = expected.get("tolerance_mm", 1)
            tolerance_pt = self._mm_to_pt(tolerance_mm)

            # Check position
            if "expected_x_mm" in expected:
                expected_x = self._mm_to_pt(expected["expected_x_mm"])
                actual_x = actual.get("left", 0)
                diff = abs(actual_x - expected_x)

                if diff > tolerance_pt:
                    issues.append({
                        "type": "layout",
                        "severity": "warning",
                        "element": name,
                        "property": "x_position",
                        "expected_mm": expected["expected_x_mm"],
                        "actual_mm": round(self._pt_to_mm(actual_x), 2),
                        "difference_mm": round(self._pt_to_mm(diff), 2),
                        "message": f"'{name}' X position off by {round(self._pt_to_mm(diff), 1)}mm",
                        "suggestion": f"Move to X={expected['expected_x_mm']}mm"
                    })

            if "expected_y_mm" in expected:
                expected_y = -self._mm_to_pt(expected["expected_y_mm"])  # Negative for AI coords
                actual_y = actual.get("top", 0)
                diff = abs(actual_y - expected_y)

                if diff > tolerance_pt:
                    issues.append({
                        "type": "layout",
                        "severity": "warning",
                        "element": name,
                        "property": "y_position",
                        "expected_mm": expected["expected_y_mm"],
                        "actual_mm": round(self._pt_to_mm(-actual_y), 2),
                        "difference_mm": round(self._pt_to_mm(diff), 2),
                        "message": f"'{name}' Y position off by {round(self._pt_to_mm(diff), 1)}mm",
                        "suggestion": f"Move to Y={expected['expected_y_mm']}mm"
                    })

        self.issues.extend(issues)
        return issues

    def validate(self, check_rules: List[str] = None,
                 expected_layout: Dict[str, Any] = None,
                 artboard_index: int = 0) -> Dict[str, Any]:
        """
        Run full validation and return results with score.

        Args:
            check_rules: List of rules to check ["alignment", "spacing", "margins", "text"]
            expected_layout: Optional expected layout specification
            artboard_index: Artboard index to validate

        Returns:
            Validation result with score and issues
        """
        self.issues = []
        self.score = 100

        rules = check_rules or ["alignment", "spacing", "margins", "text"]

        if "alignment" in rules:
            self.check_alignment()

        if "spacing" in rules:
            self.check_spacing()

        if "margins" in rules:
            self.check_margins(artboard_index=artboard_index)

        if "text" in rules:
            self.check_text_issues()

        if expected_layout:
            self.check_expected_layout(expected_layout)

        # Calculate score
        for issue in self.issues:
            severity = issue.get("severity", "info")
            if severity == "error":
                self.score -= 10
            elif severity == "warning":
                self.score -= 5
            elif severity == "info":
                self.score -= 2

        self.score = max(0, self.score)

        # Determine pass/fail
        error_count = sum(1 for i in self.issues if i.get("severity") == "error")
        warning_count = sum(1 for i in self.issues if i.get("severity") == "warning")

        passed = self.score >= 70 and error_count == 0

        return {
            "score": self.score,
            "passed": passed,
            "total_issues": len(self.issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": len(self.issues) - error_count - warning_count,
            "issues": self.issues,
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> str:
        """Generate human-readable summary of validation results."""
        if not self.issues:
            return "No issues found. Design passes all checks."

        error_count = sum(1 for i in self.issues if i.get("severity") == "error")
        warning_count = sum(1 for i in self.issues if i.get("severity") == "warning")

        summary_parts = []

        if error_count:
            summary_parts.append(f"{error_count} error(s)")
        if warning_count:
            summary_parts.append(f"{warning_count} warning(s)")

        summary = f"Found {', '.join(summary_parts)}. "

        # Add most critical issues
        errors = [i for i in self.issues if i.get("severity") == "error"]
        if errors:
            summary += "Critical: " + "; ".join(e.get("message", "") for e in errors[:3])

        return summary


def generate_fix_script(issues: List[Dict[str, Any]]) -> str:
    """
    Generate ExtendScript code to fix detected issues.

    Args:
        issues: List of issues from validation

    Returns:
        ExtendScript code to fix issues
    """
    scripts = []
    scripts.append("// Auto-generated fix script")
    scripts.append("var doc = app.activeDocument;")
    scripts.append("")

    # Group issues by type
    alignment_issues = [i for i in issues if i.get("type") == "alignment"]
    margin_issues = [i for i in issues if i.get("type") == "margin"]

    # Generate alignment fixes
    if alignment_issues:
        scripts.append("// Fix alignment issues")
        for issue in alignment_issues:
            elements = issue.get("elements", [])
            align_type = issue.get("alignment_type", "left")

            if len(elements) >= 2:
                scripts.append(f"// Align {', '.join(elements)} to {align_type}")
                # This is a simplified fix - actual implementation would need element lookup
                scripts.append(f"// TODO: Implement {align_type} alignment for these elements")
        scripts.append("")

    # Generate margin fixes
    if margin_issues:
        scripts.append("// Fix margin issues")
        for issue in margin_issues:
            element = issue.get("element", "")
            edge = issue.get("edge", "")
            required = issue.get("required_margin_mm", 3)

            scripts.append(f"// Move '{element}' away from {edge} edge")
            scripts.append(f"// Required margin: {required}mm")
        scripts.append("")

    scripts.append("// End of fix script")

    return "\n".join(scripts)
