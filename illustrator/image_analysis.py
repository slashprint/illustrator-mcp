"""
Image Analysis for Adobe Illustrator MCP Server
Provides image color extraction, layout analysis, and OCR capabilities
"""

from typing import List, Dict, Any, Tuple, Optional
import os
import io
import base64
from collections import Counter


# Check for optional dependencies
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True

    # Configure Tesseract path for Windows
    import os
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Set tessdata path to user directory (for Korean support)
    user_tessdata = os.path.expanduser("~/tessdata")
    if os.path.exists(user_tessdata):
        os.environ["TESSDATA_PREFIX"] = user_tessdata
except ImportError:
    TESSERACT_AVAILABLE = False


def _ensure_pil():
    """Ensure PIL is available."""
    if not PIL_AVAILABLE:
        raise ImportError("PIL/Pillow is required for image analysis. Install with: pip install Pillow")


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def _color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Calculate Euclidean distance between two colors."""
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def _cluster_colors(colors: List[Tuple[int, int, int]], threshold: float = 30) -> List[Tuple[int, int, int]]:
    """Cluster similar colors together."""
    if not colors:
        return []

    clusters = []
    for color in colors:
        found_cluster = False
        for i, cluster in enumerate(clusters):
            if _color_distance(color, cluster[0]) < threshold:
                # Add to existing cluster
                clusters[i] = (
                    ((cluster[0][0] * cluster[1] + color[0]) // (cluster[1] + 1),
                     (cluster[0][1] * cluster[1] + color[1]) // (cluster[1] + 1),
                     (cluster[0][2] * cluster[1] + color[2]) // (cluster[1] + 1)),
                    cluster[1] + 1
                )
                found_cluster = True
                break

        if not found_cluster:
            clusters.append((color, 1))

    # Sort by count and return colors
    clusters.sort(key=lambda x: x[1], reverse=True)
    return [c[0] for c in clusters]


def analyze_image_colors(image_path: str = None,
                        image_data: str = None,
                        num_colors: int = 5,
                        sample_size: int = 10000) -> Dict[str, Any]:
    """
    Extract dominant color palette from an image.

    Args:
        image_path: Path to image file
        image_data: Base64 encoded image data (alternative to path)
        num_colors: Number of colors to extract
        sample_size: Number of pixels to sample for analysis

    Returns:
        Dictionary with extracted color palette
    """
    _ensure_pil()

    try:
        # Load image
        if image_data:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
        elif image_path:
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            img = Image.open(image_path)
        else:
            return {"error": "Either image_path or image_data must be provided"}

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Get image dimensions
        width, height = img.size
        total_pixels = width * height

        # Sample pixels
        pixels = list(img.getdata())

        # If image is large, sample randomly
        if len(pixels) > sample_size:
            import random
            pixels = random.sample(pixels, sample_size)

        # Filter out pure white, pure black, and very similar colors
        filtered_pixels = []
        for p in pixels:
            # Skip near-white and near-black
            if sum(p) > 720 or sum(p) < 30:
                continue
            filtered_pixels.append(p)

        if not filtered_pixels:
            filtered_pixels = pixels

        # Cluster similar colors
        clustered = _cluster_colors(filtered_pixels, threshold=25)

        # Get top colors
        top_colors = clustered[:num_colors]

        # Format results
        palette = []
        for i, color in enumerate(top_colors):
            r, g, b = color
            palette.append({
                "index": i,
                "rgb": [r, g, b],
                "hex": _rgb_to_hex(r, g, b),
                "name": _get_color_name(r, g, b),
                "usage_suggestion": _suggest_color_usage(r, g, b, i)
            })

        return {
            "success": True,
            "image_size": {"width": width, "height": height},
            "colors_extracted": len(palette),
            "palette": palette,
            "extendscript_code": _generate_color_code(palette)
        }

    except Exception as e:
        return {"error": str(e)}


def _get_color_name(r: int, g: int, b: int) -> str:
    """Get approximate color name."""
    # Basic color name detection
    if r > 200 and g < 100 and b < 100:
        return "Red"
    elif r > 200 and g > 150 and b < 100:
        return "Orange"
    elif r > 200 and g > 200 and b < 100:
        return "Yellow"
    elif r < 100 and g > 200 and b < 100:
        return "Green"
    elif r < 100 and g > 200 and b > 200:
        return "Cyan"
    elif r < 100 and g < 100 and b > 200:
        return "Blue"
    elif r > 200 and g < 100 and b > 200:
        return "Magenta"
    elif r > 200 and g > 200 and b > 200:
        return "Light Gray"
    elif r < 50 and g < 50 and b < 50:
        return "Dark Gray"
    elif abs(r - g) < 30 and abs(g - b) < 30:
        return "Gray"
    elif r > g and r > b:
        return "Warm Tone"
    elif b > r and b > g:
        return "Cool Tone"
    else:
        return "Mixed"


def _suggest_color_usage(r: int, g: int, b: int, index: int) -> str:
    """Suggest usage for extracted color."""
    brightness = (r + g + b) / 3

    if index == 0:
        return "Primary/Dominant color"
    elif index == 1:
        return "Secondary color"
    elif brightness > 200:
        return "Background/Light accent"
    elif brightness < 80:
        return "Text/Dark accent"
    else:
        return "Accent color"


def _generate_color_code(palette: List[Dict]) -> str:
    """Generate ExtendScript code for the color palette."""
    lines = ["// Extracted color palette"]
    lines.append("var colors = {};")

    for color in palette:
        r, g, b = color["rgb"]
        name = f"color{color['index']}"
        lines.append(f"colors.{name} = new RGBColor();")
        lines.append(f"colors.{name}.red = {r};")
        lines.append(f"colors.{name}.green = {g};")
        lines.append(f"colors.{name}.blue = {b};")
        lines.append(f"// {color['hex']} - {color['name']}")
        lines.append("")

    return "\n".join(lines)


def analyze_image_layout(image_path: str = None,
                         image_data: str = None,
                         detect_regions: bool = True) -> Dict[str, Any]:
    """
    Analyze image layout to detect regions and structure.

    Args:
        image_path: Path to image file
        image_data: Base64 encoded image data
        detect_regions: Whether to detect distinct regions

    Returns:
        Dictionary with layout analysis results
    """
    _ensure_pil()

    try:
        # Load image
        if image_data:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
        elif image_path:
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            img = Image.open(image_path)
        else:
            return {"error": "Either image_path or image_data must be provided"}

        width, height = img.size
        aspect_ratio = width / height

        # Determine layout type
        if aspect_ratio > 1.3:
            layout_type = "landscape"
        elif aspect_ratio < 0.77:
            layout_type = "portrait"
        else:
            layout_type = "square"

        # Analyze brightness distribution
        if img.mode != "L":
            gray = img.convert("L")
        else:
            gray = img

        # Divide into regions and analyze
        regions = []
        grid_size = 3  # 3x3 grid

        region_width = width // grid_size
        region_height = height // grid_size

        for row in range(grid_size):
            for col in range(grid_size):
                left = col * region_width
                top = row * region_height
                right = min(left + region_width, width)
                bottom = min(top + region_height, height)

                region = gray.crop((left, top, right, bottom))
                pixels = list(region.getdata())
                avg_brightness = sum(pixels) / len(pixels) if pixels else 128

                region_name = _get_region_name(row, col)

                regions.append({
                    "position": region_name,
                    "row": row,
                    "col": col,
                    "bounds": {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom
                    },
                    "brightness": round(avg_brightness, 1),
                    "content_hint": _guess_content(avg_brightness)
                })

        # Detect visual weight distribution
        top_brightness = sum(r["brightness"] for r in regions if r["row"] == 0) / grid_size
        bottom_brightness = sum(r["brightness"] for r in regions if r["row"] == grid_size - 1) / grid_size
        left_brightness = sum(r["brightness"] for r in regions if r["col"] == 0) / grid_size
        right_brightness = sum(r["brightness"] for r in regions if r["col"] == grid_size - 1) / grid_size

        balance = {
            "vertical": "top-heavy" if top_brightness < bottom_brightness - 20 else
                       "bottom-heavy" if bottom_brightness < top_brightness - 20 else "balanced",
            "horizontal": "left-heavy" if left_brightness < right_brightness - 20 else
                         "right-heavy" if right_brightness < left_brightness - 20 else "balanced"
        }

        # Suggest focal points (darkest regions often have content)
        sorted_regions = sorted(regions, key=lambda r: r["brightness"])
        focal_points = [r["position"] for r in sorted_regions[:2]]

        return {
            "success": True,
            "image_size": {"width": width, "height": height},
            "aspect_ratio": round(aspect_ratio, 2),
            "layout_type": layout_type,
            "regions": regions,
            "balance": balance,
            "suggested_focal_points": focal_points,
            "recommendations": _generate_layout_recommendations(layout_type, balance, focal_points)
        }

    except Exception as e:
        return {"error": str(e)}


def _get_region_name(row: int, col: int) -> str:
    """Get human-readable region name."""
    vertical = ["top", "middle", "bottom"][row] if row < 3 else f"row{row}"
    horizontal = ["left", "center", "right"][col] if col < 3 else f"col{col}"
    return f"{vertical}-{horizontal}"


def _guess_content(brightness: float) -> str:
    """Guess content type based on brightness."""
    if brightness < 80:
        return "likely_content"  # Dark areas often have content
    elif brightness > 200:
        return "likely_empty"  # Bright areas often empty
    else:
        return "mixed"


def _generate_layout_recommendations(layout_type: str, balance: Dict, focal_points: List[str]) -> List[str]:
    """Generate layout recommendations."""
    recommendations = []

    if layout_type == "landscape":
        recommendations.append("Landscape format - good for banners, headers, social media covers")
    elif layout_type == "portrait":
        recommendations.append("Portrait format - good for posters, mobile screens, stories")
    else:
        recommendations.append("Square format - versatile, good for social media posts")

    if balance["vertical"] != "balanced":
        recommendations.append(f"Visual weight is {balance['vertical']} - consider rebalancing")
    if balance["horizontal"] != "balanced":
        recommendations.append(f"Visual weight is {balance['horizontal']} - consider rebalancing")

    if focal_points:
        recommendations.append(f"Main focal points detected at: {', '.join(focal_points)}")

    return recommendations


def extract_text_ocr(image_path: str = None,
                     image_data: str = None,
                     language: str = "eng+kor") -> Dict[str, Any]:
    """
    Extract text from image using OCR.

    Args:
        image_path: Path to image file
        image_data: Base64 encoded image data
        language: Tesseract language code (e.g., "eng", "kor", "eng+kor")

    Returns:
        Dictionary with extracted text and positions
    """
    _ensure_pil()

    if not TESSERACT_AVAILABLE:
        return {
            "error": "pytesseract is not installed. Install with: pip install pytesseract",
            "note": "Also requires Tesseract OCR engine to be installed on the system"
        }

    try:
        # Load image
        if image_data:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
        elif image_path:
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            img = Image.open(image_path)
        else:
            return {"error": "Either image_path or image_data must be provided"}

        width, height = img.size

        # Get detailed OCR data
        try:
            ocr_data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
        except Exception as e:
            # Fallback to simple text extraction
            text = pytesseract.image_to_string(img, lang=language)
            return {
                "success": True,
                "text": text,
                "detailed": False,
                "note": f"Detailed extraction failed: {str(e)}"
            }

        # Process OCR results
        text_blocks = []
        current_line = []
        current_line_num = -1

        for i in range(len(ocr_data["text"])):
            text = ocr_data["text"][i].strip()
            if not text:
                continue

            confidence = ocr_data["conf"][i]
            if confidence < 0:  # Skip invalid entries
                continue

            line_num = ocr_data["line_num"][i]

            text_block = {
                "text": text,
                "confidence": confidence,
                "position": {
                    "left": ocr_data["left"][i],
                    "top": ocr_data["top"][i],
                    "width": ocr_data["width"][i],
                    "height": ocr_data["height"][i]
                },
                "position_mm": {
                    "left_mm": round(ocr_data["left"][i] * 0.264583, 2),  # px to mm at 96dpi
                    "top_mm": round(ocr_data["top"][i] * 0.264583, 2),
                    "width_mm": round(ocr_data["width"][i] * 0.264583, 2),
                    "height_mm": round(ocr_data["height"][i] * 0.264583, 2)
                },
                "line_number": line_num
            }

            # Estimate font size from height
            font_size_px = ocr_data["height"][i]
            font_size_pt = font_size_px * 0.75  # Approximate conversion
            text_block["estimated_font_size_pt"] = round(font_size_pt, 1)

            text_blocks.append(text_block)

        # Combine into full text
        full_text = " ".join(b["text"] for b in text_blocks)

        return {
            "success": True,
            "image_size": {"width": width, "height": height},
            "language": language,
            "full_text": full_text,
            "text_blocks": text_blocks,
            "total_blocks": len(text_blocks),
            "average_confidence": round(
                sum(b["confidence"] for b in text_blocks) / len(text_blocks), 1
            ) if text_blocks else 0
        }

    except Exception as e:
        return {"error": str(e)}


def create_color_swatches_script(palette: List[Dict]) -> str:
    """
    Generate ExtendScript to create color swatches in Illustrator.

    Args:
        palette: Color palette from analyze_image_colors

    Returns:
        ExtendScript code
    """
    lines = [
        "// Create color swatches from extracted palette",
        "var doc = app.activeDocument;",
        ""
    ]

    for color in palette:
        r, g, b = color["rgb"]
        hex_name = color["hex"].replace("#", "")
        swatch_name = f"Extracted_{hex_name}"

        lines.append(f"// {color['name']} - {color['hex']}")
        lines.append("(function() {")
        lines.append(f"    var color = new RGBColor();")
        lines.append(f"    color.red = {r};")
        lines.append(f"    color.green = {g};")
        lines.append(f"    color.blue = {b};")
        lines.append(f"    ")
        lines.append(f"    var spot = doc.spots.add();")
        lines.append(f"    spot.name = '{swatch_name}';")
        lines.append(f"    spot.color = color;")
        lines.append("})();")
        lines.append("")

    lines.append("// Swatches created successfully")

    return "\n".join(lines)
