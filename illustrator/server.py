import subprocess
import tempfile
import os
import asyncio
import base64
import io
import logging
import time
import json
import sys

import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

try:
    from .prompt import (
        get_system_prompt,
        get_prompt_suggestions,
        get_advanced_templates,
        get_prompting_tips,
        display_help,
        format_advanced_template,
    )
except ImportError:
    from prompt import (
        get_system_prompt,
        get_prompt_suggestions,
        get_advanced_templates,
        get_prompting_tips,
        display_help,
        format_advanced_template,
    )

try:
    from .platform_backend import get_backend
except ImportError:
    from platform_backend import get_backend

from extendscript_library import (
    get_utility_functions,
    get_all_examples,
    list_available_examples,
    SHAPE_EXAMPLES,
    TEXT_EXAMPLES,
    GRADIENT_EXAMPLES,
    LOGO_EXAMPLES,
    ICON_EXAMPLES,
    LAYER_EXAMPLES,
    EXPORT_EXAMPLES
)

from design_guide import (
    get_color_palette,
    get_all_palettes,
    get_typography_guide,
    get_layout_principles,
    get_logo_guidelines,
    get_icon_guidelines,
    get_print_specs,
    get_design_rules,
    get_full_design_guide,
    get_korean_font_database,
    get_korean_fonts_by_category,
    get_korean_font_info,
    recommend_korean_fonts,
    get_validation_rules,
    get_margin_rule
)

from design_validator import DesignValidator, generate_fix_script

from image_analysis import (
    analyze_image_colors,
    analyze_image_layout,
    extract_text_ocr
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

server = Server("illustrator")

# Initialise the platform-specific backend (Windows COM or macOS AppleScript).
_backend = None


def _get_backend():
    global _backend
    if _backend is None:
        _backend = get_backend()
    return _backend


def _print_client_config_hint() -> None:
    """Print a ready-to-copy config snippet for MCP clients."""
    python_path = sys.executable.replace("\\", "\\\\")
    server_path = os.path.abspath(__file__).replace("\\", "\\\\")
    hint = f"""
Add this MCP config in your client settings (Claude Desktop / Claude Code / Cursor / VS Code Copilot / JetBrains Copilot):
{{
  "mcpServers": {{
    "illustrator": {{
      "command": "{python_path}",
      "args": [
        "{server_path}"
      ]
    }}
  }}
}}
"""
    print(hint, file=sys.stderr)
    sys.stderr.flush()


# ===== MCP PROMPTS =====
# Prompts provide context and guidance to Claude for design tasks

ILLUSTRATOR_SYSTEM_PROMPT = """You are an expert Adobe Illustrator designer and ExtendScript developer.
You have deep knowledge of:
- Vector graphics design principles
- Color theory and typography
- Logo, icon, and illustration design
- ExtendScript/JavaScript for Illustrator automation

When creating designs:
1. First use get_document_info to understand the current document state
2. Use get_design_guide and get_color_palette for professional design decisions
3. Use get_code_example to reference working ExtendScript patterns
4. Execute code with the run tool
5. Verify results with render_artboard (independent of user's screen)

ExtendScript Tips:
- Coordinates: top-left origin, Y increases downward (negative for below origin)
- Colors: Use RGBColor or CMYKColor objects
- No native JSON - use provided toJSON function for complex data
- Always check app.documents.length before accessing activeDocument

Design Principles:
- Keep it simple - less is more
- Use consistent spacing and alignment
- Limit color palette to 3-5 colors
- Establish clear visual hierarchy
- Test at multiple sizes
"""


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts for Illustrator design tasks."""
    return [
        types.Prompt(
            name="illustrator-expert",
            description="Expert Illustrator designer and ExtendScript developer context",
            arguments=[]
        ),
        types.Prompt(
            name="logo-designer",
            description="Specialized context for logo design projects",
            arguments=[
                types.PromptArgument(
                    name="company_name",
                    description="Name of the company for the logo",
                    required=False
                ),
                types.PromptArgument(
                    name="style",
                    description="Logo style (modern, vintage, minimal, etc.)",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="icon-designer",
            description="Specialized context for icon set design",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Icon style (outline, filled, flat, etc.)",
                    required=False
                ),
                types.PromptArgument(
                    name="size",
                    description="Target icon size in pixels",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="print-designer",
            description="Context for print design (business cards, flyers, posters)",
            arguments=[
                types.PromptArgument(
                    name="item_type",
                    description="Type of print item (business_card, flyer_a4, poster_a3, letterhead)",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    """Get a specific prompt with context for design tasks."""

    if name == "illustrator-expert":
        return types.GetPromptResult(
            description="Expert Illustrator designer context",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=ILLUSTRATOR_SYSTEM_PROMPT
                    )
                )
            ]
        )

    elif name == "logo-designer":
        company = arguments.get("company_name", "[Company Name]") if arguments else "[Company Name]"
        style = arguments.get("style", "modern and professional") if arguments else "modern and professional"

        logo_context = f"""{ILLUSTRATOR_SYSTEM_PROMPT}

CURRENT TASK: Logo Design for {company}
Style: {style}

Logo Design Guidelines:
- Simple: Easy to recognize at any size
- Memorable: Distinctive and unique
- Timeless: Avoid trendy elements
- Versatile: Works in color and black/white
- Appropriate: Reflects brand personality

Logo Types:
1. Wordmark - Company name as logo (Google, Coca-Cola)
2. Lettermark - Initials (IBM, HBO)
3. Symbol - Icon only (Apple, Nike)
4. Combination - Symbol + text (Adidas, Lacoste)
5. Emblem - Text inside symbol (Starbucks, NFL)

Process:
1. Get current document info
2. Choose appropriate logo type
3. Select color palette (use get_color_palette)
4. Create base shapes
5. Add typography if needed
6. Verify with render_artboard
"""
        return types.GetPromptResult(
            description=f"Logo design context for {company}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=logo_context)
                )
            ]
        )

    elif name == "icon-designer":
        style = arguments.get("style", "outline") if arguments else "outline"
        size = arguments.get("size", "24") if arguments else "24"

        icon_context = f"""{ILLUSTRATOR_SYSTEM_PROMPT}

CURRENT TASK: Icon Design
Style: {style}
Target Size: {size}px

Icon Design Guidelines:
- Align to pixel grid for crisp rendering
- Use consistent stroke width across set
- Maintain same corner radius
- Keep similar visual weight/density
- Test at target size and smaller

Style Guidelines for {style}:
{"- Stroke-based, no fill" if style == "outline" else ""}
{"- Stroke width: 1.5-2px at 24px" if style == "outline" else ""}
{"- Solid filled shapes" if style == "filled" else ""}
{"- No gradients, solid colors only" if style == "flat" else ""}

Grid Sizes:
- 16px: Smallest usable
- 24px: Standard UI
- 32px: Medium emphasis
- 48px: Large/featured

Process:
1. Set up {size}x{size} artboard
2. Create icon using simple shapes
3. Ensure consistent stroke/fill
4. Verify at actual size
"""
        return types.GetPromptResult(
            description=f"Icon design context ({style}, {size}px)",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=icon_context)
                )
            ]
        )

    elif name == "print-designer":
        item_type = arguments.get("item_type", "business_card") if arguments else "business_card"
        specs = get_print_specs(item_type) or get_print_specs("business_card")

        print_context = f"""{ILLUSTRATOR_SYSTEM_PROMPT}

CURRENT TASK: Print Design - {item_type.replace('_', ' ').title()}

Specifications:
{json.dumps(specs, indent=2)}

Print Design Rules:
- Always use CMYK color mode
- Set up proper bleed (usually 3mm)
- Keep important content in safe zone
- Use 300 DPI for images
- Convert text to outlines before final export
- Avoid pure black - use rich black (C:40 M:30 Y:30 K:100)

Process:
1. Set up document with correct size and bleed
2. Create layout with safe margins
3. Add design elements
4. Use CMYK colors
5. Export as PDF for print
"""
        return types.GetPromptResult(
            description=f"Print design context for {item_type}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=print_context)
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    logging.info("Listing available tools.")
    return [
        types.Tool(
            name="view",
            description="View a screenshot of the Adobe Illustrator window",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="run",
            description="Run ExtendScript code in Illustrator and return the result. The last expression's value is returned. Use include_utils=true to include helper functions like toJSON(), makeRGBColor(), etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "ExtendScript code to execute. The value of the last expression is returned."
                    },
                    "include_utils": {
                        "type": "boolean",
                        "description": "Include utility functions (toJSON, makeRGBColor, etc.). Default: false",
                        "default": False
                    }
                },
                "required": ["code"],
            },
        ),
        types.Tool(
            name="get_document_info",
            description="Get detailed information about the current Illustrator document including layers, artboards, and objects. Returns structured JSON data independent of user's view.",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_objects": {
                        "type": "boolean",
                        "description": "Include detailed object information (paths, text, etc.). Default: true",
                        "default": True
                    },
                    "max_objects_per_layer": {
                        "type": "integer",
                        "description": "Maximum number of objects to return per layer. Default: 50",
                        "default": 50
                    }
                }
            },
        ),
        types.Tool(
            name="render_artboard",
            description="Render a specific artboard to PNG image. Independent of user's current view - returns the actual artboard content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "artboard_index": {
                        "type": "integer",
                        "description": "Index of the artboard to render (0-based). Default: 0 (first artboard)",
                        "default": 0
                    },
                    "scale": {
                        "type": "number",
                        "description": "Scale factor for export. 1.0 = 100%, 0.5 = 50%, 2.0 = 200%. Default: 1.0",
                        "default": 1.0
                    }
                }
            },
        ),
        types.Tool(
            name="get_prompt_suggestions",
            description="Get categorized prompt suggestions for creating content in Illustrator",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter by category (e.g., 'logos', 'illustrations', 'icons')",
                        "enum": [
                            "basic_shapes",
                            "typography",
                            "logos",
                            "illustrations", 
                            "icons",
                            "artistic",
                            "charts",
                            "print"
                        ]
                    }
                }
            },
        ),
        types.Tool(
            name="get_system_prompt",
            description="Get the system prompt template for better AI guidance when working with Illustrator",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_prompting_tips",
            description="Get tips for creating better prompts when working with Illustrator",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_advanced_template",
            description="Get an advanced prompt template for complex design tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_type": {
                        "type": "string",
                        "description": "Type of template to get",
                        "enum": ["logo_design", "illustration", "infographic", "icon_set"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameters to fill in the template (varies by template type)"
                    }
                },
                "required": ["template_type"]
            },
        ),
        types.Tool(
            name="help",
            description="Display comprehensive help information for using the Illustrator MCP server",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_code_example",
            description="Get ready-to-use ExtendScript code examples for common design tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category of code example",
                        "enum": ["shapes", "text", "gradients", "logos", "icons", "layers", "export", "layout", "text_style"]
                    },
                    "example_name": {
                        "type": "string",
                        "description": "Specific example name (optional - omit to list available examples)"
                    }
                },
                "required": ["category"]
            },
        ),
        types.Tool(
            name="get_design_guide",
            description="Get professional design guidelines and principles",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Design topic to get guidance on",
                        "enum": ["colors", "typography", "layout", "logo", "icon", "print", "rules", "all"]
                    },
                    "detail": {
                        "type": "string",
                        "description": "Specific detail within topic (e.g., palette name for colors, spec name for print)"
                    }
                },
                "required": ["topic"]
            },
        ),
        types.Tool(
            name="get_color_palette",
            description="Get curated color palettes for different design purposes",
            inputSchema={
                "type": "object",
                "properties": {
                    "palette_name": {
                        "type": "string",
                        "description": "Name of the color palette",
                        "enum": ["corporate", "creative", "minimal", "nature", "tech", "warm", "cool"]
                    }
                }
            },
        ),
        # ===== NEW PRECISION LAYOUT TOOLS =====
        types.Tool(
            name="position_element",
            description="Position an element at exact mm coordinates. Use element name or index to identify the element.",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_name": {
                        "type": "string",
                        "description": "Name of the element to position (or use element_index)"
                    },
                    "element_index": {
                        "type": "integer",
                        "description": "Index of the element in pageItems (0-based, alternative to element_name)"
                    },
                    "x_mm": {
                        "type": "number",
                        "description": "X position in millimeters from left edge of artboard"
                    },
                    "y_mm": {
                        "type": "number",
                        "description": "Y position in millimeters from top edge of artboard"
                    },
                    "width_mm": {
                        "type": "number",
                        "description": "Optional: Resize width in millimeters"
                    },
                    "height_mm": {
                        "type": "number",
                        "description": "Optional: Resize height in millimeters"
                    },
                    "artboard_index": {
                        "type": "integer",
                        "description": "Artboard index (default: 0)",
                        "default": 0
                    }
                },
                "required": ["x_mm", "y_mm"]
            },
        ),
        types.Tool(
            name="align_elements",
            description="Align multiple elements (left/center/right/top/middle/bottom) or distribute them evenly",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of elements to align (or use 'selection' to use current selection)"
                    },
                    "alignment": {
                        "type": "string",
                        "enum": ["left", "center", "right", "top", "middle", "bottom"],
                        "description": "Alignment type"
                    },
                    "distribute": {
                        "type": "string",
                        "enum": ["horizontal", "vertical"],
                        "description": "Optional: Distribute elements evenly (horizontal or vertical)"
                    },
                    "use_selection": {
                        "type": "boolean",
                        "description": "Use currently selected elements instead of element_names",
                        "default": False
                    }
                },
                "required": ["alignment"]
            },
        ),
        types.Tool(
            name="measure_elements",
            description="Measure distances and sizes of elements in mm",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of elements to measure (1-2 elements)"
                    },
                    "use_selection": {
                        "type": "boolean",
                        "description": "Use currently selected elements",
                        "default": False
                    }
                }
            },
        ),
        types.Tool(
            name="create_layout_grid",
            description="Create a visual layout grid with guides",
            inputSchema={
                "type": "object",
                "properties": {
                    "columns": {
                        "type": "integer",
                        "description": "Number of columns",
                        "default": 4
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of rows",
                        "default": 4
                    },
                    "gutter_mm": {
                        "type": "number",
                        "description": "Gutter size in mm",
                        "default": 5
                    },
                    "margin_mm": {
                        "type": "number",
                        "description": "Outer margin in mm",
                        "default": 10
                    },
                    "artboard_index": {
                        "type": "integer",
                        "description": "Artboard index",
                        "default": 0
                    }
                }
            },
        ),
        # ===== FONT MANAGEMENT TOOLS =====
        types.Tool(
            name="list_fonts",
            description="List available system fonts, with optional Korean font filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_korean": {
                        "type": "boolean",
                        "description": "Only show Korean fonts",
                        "default": False
                    },
                    "search": {
                        "type": "string",
                        "description": "Search fonts by name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of fonts to return",
                        "default": 50
                    }
                }
            },
        ),
        types.Tool(
            name="get_font_info",
            description="Get detailed information about a specific font",
            inputSchema={
                "type": "object",
                "properties": {
                    "font_name": {
                        "type": "string",
                        "description": "Name of the font to get info for"
                    }
                },
                "required": ["font_name"]
            },
        ),
        types.Tool(
            name="apply_text_style",
            description="Apply detailed text styling to a text element",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_name": {
                        "type": "string",
                        "description": "Name of the text element"
                    },
                    "element_index": {
                        "type": "integer",
                        "description": "Index of text frame (alternative to name)"
                    },
                    "font_name": {
                        "type": "string",
                        "description": "Font name (Illustrator internal name)"
                    },
                    "font_size_pt": {
                        "type": "number",
                        "description": "Font size in points"
                    },
                    "tracking": {
                        "type": "number",
                        "description": "Letter spacing (tracking) in 1/1000 em"
                    },
                    "leading_pt": {
                        "type": "number",
                        "description": "Line height (leading) in points"
                    },
                    "color_rgb": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "RGB color as [r, g, b]"
                    },
                    "alignment": {
                        "type": "string",
                        "enum": ["left", "center", "right", "justify"],
                        "description": "Text alignment"
                    }
                }
            },
        ),
        types.Tool(
            name="recommend_korean_fonts",
            description="Get Korean font recommendations based on purpose",
            inputSchema={
                "type": "object",
                "properties": {
                    "purpose": {
                        "type": "string",
                        "enum": ["heading", "body", "logo", "ui", "traditional", "casual", "children", "formal"],
                        "description": "Purpose of the font usage"
                    }
                },
                "required": ["purpose"]
            },
        ),
        # ===== DESIGN VALIDATION TOOLS =====
        types.Tool(
            name="verify_design",
            description="Verify design quality by checking alignment, spacing, margins, and other rules. Returns score and issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "artboard_index": {
                        "type": "integer",
                        "description": "Index of artboard to verify",
                        "default": 0
                    },
                    "check_rules": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["alignment", "spacing", "margins", "text"]
                        },
                        "description": "Which rules to check (default: all)"
                    },
                    "expected_layout": {
                        "type": "object",
                        "description": "Optional expected layout specification with element positions"
                    },
                    "min_margin_mm": {
                        "type": "number",
                        "description": "Minimum margin in mm (default: 3)",
                        "default": 3
                    }
                }
            },
        ),
        types.Tool(
            name="auto_fix_issues",
            description="Automatically fix detected design issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "issues": {
                        "type": "array",
                        "description": "List of issues from verify_design to fix"
                    },
                    "fix_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["alignment", "spacing", "margins"]
                        },
                        "description": "Types of issues to fix"
                    }
                }
            },
        ),
        types.Tool(
            name="design_iteration",
            description="Run a complete design iteration: render → verify → return results. Optionally auto-fix issues.",
            inputSchema={
                "type": "object",
                "properties": {
                    "artboard_index": {
                        "type": "integer",
                        "description": "Artboard to iterate on",
                        "default": 0
                    },
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Automatically fix detected issues",
                        "default": False
                    },
                    "min_score": {
                        "type": "integer",
                        "description": "Minimum acceptable score (0-100)",
                        "default": 70
                    },
                    "include_render": {
                        "type": "boolean",
                        "description": "Include rendered image in response",
                        "default": True
                    }
                }
            },
        ),
        # ===== IMAGE ANALYSIS TOOLS =====
        types.Tool(
            name="analyze_image_colors",
            description="Extract color palette from a reference image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file"
                    },
                    "num_colors": {
                        "type": "integer",
                        "description": "Number of colors to extract",
                        "default": 5
                    }
                },
                "required": ["image_path"]
            },
        ),
        types.Tool(
            name="analyze_image_layout",
            description="Analyze layout structure of a reference image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file"
                    }
                },
                "required": ["image_path"]
            },
        ),
        types.Tool(
            name="extract_text_from_image",
            description="Extract text from image using OCR (requires pytesseract)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file"
                    },
                    "language": {
                        "type": "string",
                        "description": "OCR language code (e.g., 'eng', 'kor', 'eng+kor')",
                        "default": "eng+kor"
                    }
                },
                "required": ["image_path"]
            },
        ),
    ]

def capture_illustrator() -> list[types.TextContent | types.ImageContent]:
    logging.info("Starting screenshot capture for Illustrator.")
    try:
        backend = _get_backend()
        screenshot_data = backend.capture_screenshot()
        logging.info("Screenshot captured successfully.")
        return [types.ImageContent(type="image", mimeType="image/jpeg", data=screenshot_data)]
    except Exception as e:
        logging.error(f"Failed to capture screenshot: {str(e)}")
        return [types.TextContent(type="text", text=f"Failed to capture screenshot: {str(e)}")]

def run_illustrator_script(code: str) -> list[types.TextContent]:
    logging.info("Running ExtendScript code in Illustrator.")
    try:
        backend = _get_backend()
        result = backend.run_script(code)
        logging.info("ExtendScript executed successfully.")
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logging.error(f"Failed to execute script: {str(e)}")
        return [types.TextContent(type="text", text=f"Failed to execute script: {str(e)}")]


def get_document_info(include_objects: bool = True, max_objects_per_layer: int = 50) -> list[types.TextContent]:
    """Get detailed document information using ExtendScript and return as JSON."""
    logging.info("Getting document info from Illustrator.")

    try:
        script = f'''
        (function() {{
            function toJSON(obj, indent) {{
                indent = indent || 0;
                if (obj === null) return "null";
                if (obj === undefined) return "null";
                var type = typeof obj;
                if (type === "number" || type === "boolean") return String(obj);
                if (type === "string") {{
                    return '"' + obj.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"').replace(/\\n/g, '\\\\n').replace(/\\r/g, '\\\\r') + '"';
                }}
                if (obj instanceof Array) {{
                    var items = [];
                    for (var i = 0; i < obj.length; i++) items.push(toJSON(obj[i], indent + 1));
                    return "[" + items.join(", ") + "]";
                }}
                if (type === "object") {{
                    var pairs = [];
                    for (var k in obj) {{
                        if (obj.hasOwnProperty(k)) pairs.push('"' + k + '": ' + toJSON(obj[k], indent + 1));
                    }}
                    return "{{" + pairs.join(", ") + "}}";
                }}
                return "null";
            }}

            if (app.documents.length === 0) {{
                return toJSON({{error: "No document open"}});
            }}

            var doc = app.activeDocument;
            var info = {{
                name: doc.name,
                path: doc.path ? doc.path.fsName : "Not saved",
                width: doc.width,
                height: doc.height,
                colorSpace: doc.documentColorSpace == DocumentColorSpace.RGB ? "RGB" : "CMYK",
                rulerUnits: doc.rulerUnits.toString(),
                artboards: [],
                layers: [],
                selection: []
            }};

            for (var i = 0; i < doc.artboards.length; i++) {{
                var ab = doc.artboards[i];
                var rect = ab.artboardRect;
                info.artboards.push({{
                    index: i, name: ab.name,
                    left: rect[0], top: rect[1], right: rect[2], bottom: rect[3],
                    width: rect[2] - rect[0], height: rect[1] - rect[3]
                }});
            }}

            for (var i = 0; i < doc.layers.length; i++) {{
                var layer = doc.layers[i];
                var layerInfo = {{
                    index: i, name: layer.name, visible: layer.visible,
                    locked: layer.locked, objectCount: layer.pageItems.length, objects: []
                }};

                if ({'true' if include_objects else 'false'}) {{
                    var maxItems = Math.min(layer.pageItems.length, {max_objects_per_layer});
                    for (var j = 0; j < maxItems; j++) {{
                        var item = layer.pageItems[j];
                        var objInfo = {{
                            index: j, name: item.name || "(unnamed)", type: item.typename,
                            left: item.left, top: item.top, width: item.width, height: item.height,
                            visible: !item.hidden, locked: item.locked
                        }};
                        if (item.typename === "TextFrame") {{
                            objInfo.contents = item.contents.substring(0, 100);
                            objInfo.fontSize = item.textRange.characterAttributes.size;
                        }} else if (item.typename === "PathItem") {{
                            objInfo.closed = item.closed;
                            objInfo.filled = item.filled;
                            objInfo.stroked = item.stroked;
                            if (item.filled && item.fillColor) {{
                                try {{
                                    if (item.fillColor.typename === "RGBColor") {{
                                        objInfo.fillColor = {{
                                            r: Math.round(item.fillColor.red),
                                            g: Math.round(item.fillColor.green),
                                            b: Math.round(item.fillColor.blue)
                                        }};
                                    }}
                                }} catch(e) {{}}
                            }}
                        }}
                        layerInfo.objects.push(objInfo);
                    }}
                    if (layer.pageItems.length > {max_objects_per_layer}) {{
                        layerInfo.truncated = true;
                        layerInfo.totalObjects = layer.pageItems.length;
                    }}
                }}
                info.layers.push(layerInfo);
            }}

            for (var i = 0; i < doc.selection.length && i < 20; i++) {{
                var sel = doc.selection[i];
                info.selection.push({{
                    index: i, name: sel.name || "(unnamed)", type: sel.typename,
                    left: sel.left, top: sel.top, width: sel.width, height: sel.height
                }});
            }}

            return toJSON(info);
        }})();
        '''

        backend = _get_backend()
        result = backend.run_script(script)
        logging.info("Document info retrieved successfully.")
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logging.error(f"Failed to get document info: {str(e)}")
        return [types.TextContent(type="text", text=f"Failed to get document info: {str(e)}")]


def render_artboard(artboard_index: int = 0, scale: float = 1.0) -> list[types.TextContent | types.ImageContent]:
    """Render a specific artboard to PNG and return as base64 image."""
    logging.info(f"Rendering artboard {artboard_index} at scale {scale}.")

    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"illustrator_render_{int(time.time())}.png")
        temp_file_escaped = temp_file.replace("\\", "/")

        script = f'''
        (function() {{
            if (app.documents.length === 0) {{
                return "ERROR: No document open";
            }}

            var doc = app.activeDocument;
            var artboardIndex = {artboard_index};

            if (artboardIndex >= doc.artboards.length) {{
                return "ERROR: Artboard index " + artboardIndex + " out of range. Document has " + doc.artboards.length + " artboards.";
            }}

            doc.artboards.setActiveArtboardIndex(artboardIndex);

            var exportOptions = new ExportOptionsPNG24();
            exportOptions.antiAliasing = true;
            exportOptions.transparency = true;
            exportOptions.artBoardClipping = true;
            exportOptions.horizontalScale = {scale * 100};
            exportOptions.verticalScale = {scale * 100};

            var exportFile = new File("{temp_file_escaped}");
            doc.exportFile(exportFile, ExportType.PNG24, exportOptions);

            return "SUCCESS:" + exportFile.fsName;
        }})();
        '''

        backend = _get_backend()
        result = backend.run_script(script)

        if result.startswith("ERROR:"):
            return [types.TextContent(type="text", text=result)]

        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            os.unlink(temp_file)
            logging.info("Artboard rendered successfully.")
            return [types.ImageContent(type="image", mimeType="image/png", data=image_data)]
        else:
            return [types.TextContent(type="text", text=f"Export completed but file not found: {temp_file}")]

    except Exception as e:
        logging.error(f"Failed to render artboard: {str(e)}")
        return [types.TextContent(type="text", text=f"Failed to render artboard: {str(e)}")]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    logging.info(f"Received tool call: {name} with arguments: {arguments}")
    
    if name == "view":
        return capture_illustrator()
    
    elif name == "run":
        if not arguments or "code" not in arguments:
            logging.warning("No code provided for run tool.")
            return [types.TextContent(type="text", text="No code provided")]
        return run_illustrator_script(arguments["code"])

    elif name == "get_document_info":
        include_objects = arguments.get("include_objects", True) if arguments else True
        max_objects = arguments.get("max_objects_per_layer", 50) if arguments else 50
        return get_document_info(include_objects, max_objects)

    elif name == "render_artboard":
        artboard_index = arguments.get("artboard_index", 0) if arguments else 0
        scale = arguments.get("scale", 1.0) if arguments else 1.0
        return render_artboard(artboard_index, scale)

    elif name == "get_prompt_suggestions":
        try:
            suggestions = get_prompt_suggestions()
            category = arguments.get("category") if arguments else None
            
            if category:
                # Filter by category
                category_map = {
                    "basic_shapes": "🎨 Basic Shapes & Geometry",
                    "typography": "📝 Typography & Text", 
                    "logos": "🏢 Logos & Branding",
                    "illustrations": "🌆 Illustrations & Scenes",
                    "icons": "🎭 Icons & UI Elements",
                    "artistic": "🎨 Artistic & Creative",
                    "charts": "📊 Charts & Infographics",
                    "print": "🏷️ Print & Layout"
                }
                
                full_category = category_map.get(category)
                if full_category and full_category in suggestions:
                    filtered_suggestions = {full_category: suggestions[full_category]}
                    result_text = f"**{full_category}**\n\n"
                    for suggestion in suggestions[full_category]:
                        result_text += f"• {suggestion}\n"
                else:
                    result_text = f"Category '{category}' not found. Available categories: {list(category_map.keys())}"
            else:
                # Return all suggestions
                result_text = "# 🎨 Illustrator Prompt Suggestions\n\n"
                for category, prompts in suggestions.items():
                    result_text += f"## {category}\n\n"
                    for prompt in prompts:
                        result_text += f"• {prompt}\n"
                    result_text += "\n"
            
            return [types.TextContent(type="text", text=result_text)]
        except Exception as e:
            logging.error(f"Error getting prompt suggestions: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_system_prompt":
        try:
            system_prompt = get_system_prompt()
            return [types.TextContent(type="text", text=system_prompt)]
        except Exception as e:
            logging.error(f"Error getting system prompt: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_prompting_tips":
        try:
            tips = get_prompting_tips()
            result_text = "# 💡 Prompting Tips for Adobe Illustrator\n\n"
            for tip in tips:
                result_text += f"{tip}\n"
            return [types.TextContent(type="text", text=result_text)]
        except Exception as e:
            logging.error(f"Error getting prompting tips: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_advanced_template":
        try:
            template_type = arguments.get("template_type") if arguments else None
            parameters = arguments.get("parameters", {}) if arguments else {}
            
            if not template_type:
                return [types.TextContent(type="text", text="Template type is required")]
            
            templates = get_advanced_templates()
            if template_type in templates:
                if parameters:
                    # Try to format with parameters
                    try:
                        formatted_template = format_advanced_template(template_type, **parameters)
                        return [types.TextContent(type="text", text=formatted_template)]
                    except KeyError as e:
                        # Missing parameters, return template with placeholders
                        template = templates[template_type]
                        result_text = f"**{template_type.replace('_', ' ').title()} Template:**\n\n{template}\n\n"
                        result_text += f"**Missing parameter:** {str(e)}\n"
                        result_text += "Please provide the required parameters to fill in the template."
                        return [types.TextContent(type="text", text=result_text)]
                else:
                    # Return template with placeholders
                    template = templates[template_type]
                    result_text = f"**{template_type.replace('_', ' ').title()} Template:**\n\n{template}"
                    return [types.TextContent(type="text", text=result_text)]
            else:
                available_templates = list(templates.keys())
                return [types.TextContent(type="text", text=f"Template '{template_type}' not found. Available templates: {available_templates}")]
        except Exception as e:
            logging.error(f"Error getting advanced template: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "help":
        try:
            help_text = display_help()
            return [types.TextContent(type="text", text=help_text)]
        except Exception as e:
            logging.error(f"Error displaying help: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "get_code_example":
        try:
            category = arguments.get("category") if arguments else None
            example_name = arguments.get("example_name") if arguments else None

            if not category:
                return [types.TextContent(type="text", text="Category is required")]

            all_examples = get_all_examples()
            if category not in all_examples:
                return [types.TextContent(type="text", text=f"Category '{category}' not found. Available: {list(all_examples.keys())}")]

            if example_name:
                # Return specific example
                examples = all_examples[category]
                if example_name in examples:
                    code = examples[example_name]
                    result = f"# {category.title()} - {example_name}\n\n```javascript\n{code}\n```"
                    return [types.TextContent(type="text", text=result)]
                else:
                    return [types.TextContent(type="text", text=f"Example '{example_name}' not found. Available in {category}: {list(examples.keys())}")]
            else:
                # List available examples in category
                available = list_available_examples()
                result = f"# Available {category.title()} Examples\n\n"
                for ex in available[category]:
                    result += f"- {ex}\n"
                result += f"\nUse get_code_example with example_name to get the code."
                return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logging.error(f"Error getting code example: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "get_design_guide":
        try:
            topic = arguments.get("topic") if arguments else None
            detail = arguments.get("detail") if arguments else None

            if not topic:
                return [types.TextContent(type="text", text="Topic is required")]

            if topic == "all":
                guide = get_full_design_guide()
                return [types.TextContent(type="text", text=json.dumps(guide, indent=2))]
            elif topic == "colors":
                if detail:
                    palette = get_color_palette(detail)
                    if palette:
                        return [types.TextContent(type="text", text=json.dumps(palette, indent=2))]
                    else:
                        palettes = list(get_all_palettes().keys())
                        return [types.TextContent(type="text", text=f"Palette '{detail}' not found. Available: {palettes}")]
                else:
                    palettes = get_all_palettes()
                    return [types.TextContent(type="text", text=json.dumps(palettes, indent=2))]
            elif topic == "typography":
                return [types.TextContent(type="text", text=json.dumps(get_typography_guide(), indent=2))]
            elif topic == "layout":
                return [types.TextContent(type="text", text=json.dumps(get_layout_principles(), indent=2))]
            elif topic == "logo":
                return [types.TextContent(type="text", text=json.dumps(get_logo_guidelines(), indent=2))]
            elif topic == "icon":
                return [types.TextContent(type="text", text=json.dumps(get_icon_guidelines(), indent=2))]
            elif topic == "print":
                if detail:
                    spec = get_print_specs(detail)
                    if spec:
                        return [types.TextContent(type="text", text=json.dumps(spec, indent=2))]
                    else:
                        specs = list(get_print_specs().keys())
                        return [types.TextContent(type="text", text=f"Print spec '{detail}' not found. Available: {specs}")]
                else:
                    return [types.TextContent(type="text", text=json.dumps(get_print_specs(), indent=2))]
            elif topic == "rules":
                return [types.TextContent(type="text", text=json.dumps(get_design_rules(), indent=2))]
            else:
                return [types.TextContent(type="text", text=f"Unknown topic: {topic}")]
        except Exception as e:
            logging.error(f"Error getting design guide: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "get_color_palette":
        try:
            palette_name = arguments.get("palette_name") if arguments else None

            if palette_name:
                palette = get_color_palette(palette_name)
                if palette:
                    result = f"# {palette_name.title()} Color Palette\n\n"
                    result += f"**{palette['description']}**\n\n"
                    for name, info in palette['colors'].items():
                        rgb = info['rgb']
                        result += f"- **{name}**: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) | {info['hex']} | {info['usage']}\n"
                    return [types.TextContent(type="text", text=result)]
                else:
                    palettes = list(get_all_palettes().keys())
                    return [types.TextContent(type="text", text=f"Palette '{palette_name}' not found. Available: {palettes}")]
            else:
                # List all palettes
                all_palettes = get_all_palettes()
                result = "# Available Color Palettes\n\n"
                for name, palette in all_palettes.items():
                    result += f"- **{name}**: {palette['description']}\n"
                result += "\nUse get_color_palette with palette_name to get colors."
                return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logging.error(f"Error getting color palette: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # ===== PRECISION LAYOUT TOOLS =====
    elif name == "position_element":
        try:
            x_mm = arguments.get("x_mm", 0)
            y_mm = arguments.get("y_mm", 0)
            width_mm = arguments.get("width_mm")
            height_mm = arguments.get("height_mm")
            element_name = arguments.get("element_name")
            element_index = arguments.get("element_index")
            artboard_index = arguments.get("artboard_index", 0)

            script = f'''
            (function() {{
                var ptPerMm = 2.834645669;
                var doc = app.activeDocument;
                var ab = doc.artboards[{artboard_index}];
                var abRect = ab.artboardRect;

                var item = null;
                {"var item = doc.pageItems.getByName('" + element_name + "');" if element_name else ""}
                {"var item = doc.pageItems[" + str(element_index) + "];" if element_index is not None and not element_name else ""}

                if (!item) {{
                    return "ERROR: Element not found";
                }}

                // Calculate position relative to artboard
                var targetX = abRect[0] + {x_mm} * ptPerMm;
                var targetY = abRect[1] - {y_mm} * ptPerMm;

                item.position = [targetX, targetY];

                {"// Resize if dimensions specified" if width_mm or height_mm else ""}
                {f"var scaleX = ({width_mm} * ptPerMm) / item.width * 100; item.resize(scaleX, scaleX);" if width_mm and not height_mm else ""}
                {f"var scaleY = ({height_mm} * ptPerMm) / item.height * 100; item.resize(scaleY, scaleY);" if height_mm and not width_mm else ""}
                {f"var scaleX = ({width_mm} * ptPerMm) / item.width * 100; var scaleY = ({height_mm} * ptPerMm) / item.height * 100; item.resize(scaleX, scaleY);" if width_mm and height_mm else ""}

                return "SUCCESS: Positioned at " + {x_mm} + "mm, " + {y_mm} + "mm";
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "align_elements":
        try:
            alignment = arguments.get("alignment", "left")
            distribute = arguments.get("distribute")
            use_selection = arguments.get("use_selection", True)
            element_names = arguments.get("element_names", [])

            script = f'''
            (function() {{
                var doc = app.activeDocument;
                var items = [];

                {"items = doc.selection;" if use_selection else ""}
                {"for (var i = 0; i < " + str(len(element_names)) + "; i++) { try { items.push(doc.pageItems.getByName(['" + "','".join(element_names) + "'][i])); } catch(e) {} }" if element_names and not use_selection else ""}

                if (items.length < 2) {{
                    return "ERROR: Need at least 2 elements to align";
                }}

                // Find bounds
                var minLeft = items[0].position[0];
                var maxRight = items[0].position[0] + items[0].width;
                var maxTop = items[0].position[1];
                var minBottom = items[0].position[1] - items[0].height;

                for (var i = 1; i < items.length; i++) {{
                    var item = items[i];
                    if (item.position[0] < minLeft) minLeft = item.position[0];
                    if (item.position[0] + item.width > maxRight) maxRight = item.position[0] + item.width;
                    if (item.position[1] > maxTop) maxTop = item.position[1];
                    if (item.position[1] - item.height < minBottom) minBottom = item.position[1] - item.height;
                }}

                var centerX = (minLeft + maxRight) / 2;
                var centerY = (maxTop + minBottom) / 2;

                // Apply alignment
                for (var i = 0; i < items.length; i++) {{
                    var item = items[i];
                    var pos = item.position;

                    {"""
                    if ('""" + alignment + """' === 'left') {
                        item.position = [minLeft, pos[1]];
                    } else if ('""" + alignment + """' === 'right') {
                        item.position = [maxRight - item.width, pos[1]];
                    } else if ('""" + alignment + """' === 'center') {
                        item.position = [centerX - item.width / 2, pos[1]];
                    } else if ('""" + alignment + """' === 'top') {
                        item.position = [pos[0], maxTop];
                    } else if ('""" + alignment + """' === 'bottom') {
                        item.position = [pos[0], minBottom + item.height];
                    } else if ('""" + alignment + """' === 'middle') {
                        item.position = [pos[0], centerY + item.height / 2];
                    }
                    """}
                }}

                {"// Distribute evenly" if distribute else ""}
                {"""
                if ('""" + (distribute or '') + """' === 'horizontal') {
                    items.sort(function(a, b) { return a.position[0] - b.position[0]; });
                    var totalWidth = 0;
                    for (var i = 0; i < items.length; i++) totalWidth += items[i].width;
                    var gap = (maxRight - minLeft - totalWidth) / (items.length - 1);
                    var currentX = minLeft;
                    for (var i = 0; i < items.length; i++) {
                        items[i].position = [currentX, items[i].position[1]];
                        currentX += items[i].width + gap;
                    }
                } else if ('""" + (distribute or '') + """' === 'vertical') {
                    items.sort(function(a, b) { return b.position[1] - a.position[1]; });
                    var totalHeight = 0;
                    for (var i = 0; i < items.length; i++) totalHeight += items[i].height;
                    var gap = (maxTop - minBottom - totalHeight) / (items.length - 1);
                    var currentY = maxTop;
                    for (var i = 0; i < items.length; i++) {
                        items[i].position = [items[i].position[0], currentY];
                        currentY -= items[i].height + gap;
                    }
                }
                """ if distribute else ""}

                return "SUCCESS: Aligned " + items.length + " elements";
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "measure_elements":
        try:
            use_selection = arguments.get("use_selection", True)
            element_names = arguments.get("element_names", [])

            script = f'''
            (function() {{
                var ptToMm = 0.352778;
                var doc = app.activeDocument;
                var items = [];

                {"items = doc.selection;" if use_selection else ""}
                {"for (var i = 0; i < " + str(len(element_names)) + "; i++) { try { items.push(doc.pageItems.getByName(['" + "','".join(element_names) + "'][i])); } catch(e) {} }" if element_names and not use_selection else ""}

                if (items.length === 0) {{
                    return '{{"error": "No elements to measure"}}';
                }}

                var result = {{
                    elements: []
                }};

                for (var i = 0; i < items.length; i++) {{
                    var item = items[i];
                    result.elements.push({{
                        name: item.name || "(unnamed)",
                        index: i,
                        x_mm: Math.round(item.position[0] * ptToMm * 100) / 100,
                        y_mm: Math.round(-item.position[1] * ptToMm * 100) / 100,
                        width_mm: Math.round(item.width * ptToMm * 100) / 100,
                        height_mm: Math.round(item.height * ptToMm * 100) / 100
                    }});
                }}

                if (items.length >= 2) {{
                    var item1 = items[0];
                    var item2 = items[1];

                    var center1X = item1.position[0] + item1.width / 2;
                    var center1Y = item1.position[1] - item1.height / 2;
                    var center2X = item2.position[0] + item2.width / 2;
                    var center2Y = item2.position[1] - item2.height / 2;

                    var distX = Math.abs(center2X - center1X) * ptToMm;
                    var distY = Math.abs(center2Y - center1Y) * ptToMm;
                    var diagonal = Math.sqrt(distX * distX + distY * distY);

                    result.distance = {{
                        horizontal_mm: Math.round(distX * 100) / 100,
                        vertical_mm: Math.round(distY * 100) / 100,
                        diagonal_mm: Math.round(diagonal * 100) / 100
                    }};

                    // Gap between elements
                    var gapH = Math.abs(item2.position[0] - (item1.position[0] + item1.width)) * ptToMm;
                    var gapV = Math.abs((item1.position[1] - item1.height) - item2.position[1]) * ptToMm;

                    result.gap = {{
                        horizontal_mm: Math.round(gapH * 100) / 100,
                        vertical_mm: Math.round(gapV * 100) / 100
                    }};
                }}

                // toJSON function for ExtendScript
                function toJSON(obj) {{
                    if (obj === null) return "null";
                    if (obj === undefined) return "null";
                    var type = typeof obj;
                    if (type === "number" || type === "boolean") return String(obj);
                    if (type === "string") return '"' + obj.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"') + '"';
                    if (obj instanceof Array) {{
                        var items = [];
                        for (var i = 0; i < obj.length; i++) items.push(toJSON(obj[i]));
                        return "[" + items.join(",") + "]";
                    }}
                    if (type === "object") {{
                        var pairs = [];
                        for (var k in obj) if (obj.hasOwnProperty(k)) pairs.push('"' + k + '":' + toJSON(obj[k]));
                        return "{{" + pairs.join(",") + "}}";
                    }}
                    return "null";
                }}

                return toJSON(result);
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "create_layout_grid":
        try:
            columns = arguments.get("columns", 4) if arguments else 4
            rows = arguments.get("rows", 4) if arguments else 4
            gutter_mm = arguments.get("gutter_mm", 5) if arguments else 5
            margin_mm = arguments.get("margin_mm", 10) if arguments else 10
            artboard_index = arguments.get("artboard_index", 0) if arguments else 0

            script = f'''
            (function() {{
                var ptPerMm = 2.834645669;
                var doc = app.activeDocument;
                var ab = doc.artboards[{artboard_index}];
                var rect = ab.artboardRect;

                var margin = {margin_mm} * ptPerMm;
                var gutter = {gutter_mm} * ptPerMm;

                var abWidth = rect[2] - rect[0] - 2 * margin;
                var abHeight = rect[1] - rect[3] - 2 * margin;

                var colWidth = (abWidth - gutter * ({columns} - 1)) / {columns};
                var rowHeight = (abHeight - gutter * ({rows} - 1)) / {rows};

                // Create or get grid layer
                var gridLayer;
                try {{
                    gridLayer = doc.layers.getByName("_Grid");
                    // Clear existing grid
                    while (gridLayer.pageItems.length > 0) {{
                        gridLayer.pageItems[0].remove();
                    }}
                }} catch(e) {{
                    gridLayer = doc.layers.add();
                    gridLayer.name = "_Grid";
                }}

                // Create grid cells
                var strokeColor = new RGBColor();
                strokeColor.red = 200; strokeColor.green = 200; strokeColor.blue = 255;

                for (var c = 0; c < {columns}; c++) {{
                    for (var r = 0; r < {rows}; r++) {{
                        var x = rect[0] + margin + c * (colWidth + gutter);
                        var y = rect[1] - margin - r * (rowHeight + gutter);

                        var cell = doc.pathItems.rectangle(y, x, colWidth, rowHeight);
                        cell.filled = false;
                        cell.stroked = true;
                        cell.strokeWidth = 0.5;
                        cell.strokeColor = strokeColor;
                        cell.name = "grid_" + c + "_" + r;
                        cell.move(gridLayer, ElementPlacement.PLACEATEND);
                    }}
                }}

                gridLayer.locked = true;
                gridLayer.printable = false;

                return "SUCCESS: Created " + {columns} + "x" + {rows} + " grid with " + {gutter_mm} + "mm gutter and " + {margin_mm} + "mm margin";
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # ===== FONT MANAGEMENT TOOLS =====
    elif name == "list_fonts":
        try:
            filter_korean = arguments.get("filter_korean", False) if arguments else False
            search = arguments.get("search", "") if arguments else ""
            limit = arguments.get("limit", 50) if arguments else 50

            script = f'''
            (function() {{
                var fonts = [];
                var koreanIndicators = ["Gothic", "Myungjo", "Dotum", "Gulim", "Batang",
                                        "Malgun", "NanumGothic", "NanumMyeongjo", "Apple SD",
                                        "KoPub", "Noto Sans KR", "Noto Serif KR", "Spoqa",
                                        "Pretendard", "BlackHanSans", "Jua", "DoHyeon"];

                var count = 0;
                for (var i = 0; i < app.textFonts.length && count < {limit}; i++) {{
                    var font = app.textFonts[i];
                    var include = true;

                    // Korean filter
                    if ({str(filter_korean).lower()}) {{
                        include = false;
                        for (var j = 0; j < koreanIndicators.length; j++) {{
                            if (font.name.indexOf(koreanIndicators[j]) !== -1 ||
                                font.family.indexOf(koreanIndicators[j]) !== -1) {{
                                include = true;
                                break;
                            }}
                        }}
                    }}

                    // Search filter
                    {f'if (include && "{search}") {{ include = font.name.toLowerCase().indexOf("{search.lower()}") !== -1 || font.family.toLowerCase().indexOf("{search.lower()}") !== -1; }}' if search else ''}

                    if (include) {{
                        fonts.push({{
                            name: font.name,
                            family: font.family,
                            style: font.style
                        }});
                        count++;
                    }}
                }}

                // toJSON for ExtendScript
                function toJSON(obj) {{
                    if (obj === null) return "null";
                    var type = typeof obj;
                    if (type === "number" || type === "boolean") return String(obj);
                    if (type === "string") return '"' + obj.replace(/"/g, '\\\\"') + '"';
                    if (obj instanceof Array) {{
                        var items = [];
                        for (var i = 0; i < obj.length; i++) items.push(toJSON(obj[i]));
                        return "[" + items.join(",") + "]";
                    }}
                    if (type === "object") {{
                        var pairs = [];
                        for (var k in obj) if (obj.hasOwnProperty(k)) pairs.push('"' + k + '":' + toJSON(obj[k]));
                        return "{{" + pairs.join(",") + "}}";
                    }}
                    return "null";
                }}

                return toJSON({{total: fonts.length, fonts: fonts}});
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "get_font_info":
        try:
            font_name = arguments.get("font_name", "") if arguments else ""

            script = f'''
            (function() {{
                var targetName = "{font_name}";
                var font = null;

                try {{
                    font = app.textFonts.getByName(targetName);
                }} catch(e) {{
                    // Try partial match
                    for (var i = 0; i < app.textFonts.length; i++) {{
                        if (app.textFonts[i].name.indexOf(targetName) !== -1) {{
                            font = app.textFonts[i];
                            break;
                        }}
                    }}
                }}

                if (!font) {{
                    return '{{"error": "Font not found: {font_name}"}}';
                }}

                var info = {{
                    name: font.name,
                    family: font.family,
                    style: font.style
                }};

                function toJSON(obj) {{
                    if (obj === null) return "null";
                    var type = typeof obj;
                    if (type === "number" || type === "boolean") return String(obj);
                    if (type === "string") return '"' + obj.replace(/"/g, '\\\\"') + '"';
                    if (type === "object") {{
                        var pairs = [];
                        for (var k in obj) if (obj.hasOwnProperty(k)) pairs.push('"' + k + '":' + toJSON(obj[k]));
                        return "{{" + pairs.join(",") + "}}";
                    }}
                    return "null";
                }}

                return toJSON(info);
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "apply_text_style":
        try:
            element_name = arguments.get("element_name") if arguments else None
            element_index = arguments.get("element_index") if arguments else None
            font_name = arguments.get("font_name") if arguments else None
            font_size = arguments.get("font_size_pt") if arguments else None
            tracking = arguments.get("tracking") if arguments else None
            leading = arguments.get("leading_pt") if arguments else None
            color_rgb = arguments.get("color_rgb") if arguments else None
            alignment = arguments.get("alignment") if arguments else None

            # Build script parts
            get_element = ""
            if element_name:
                get_element = f"textFrame = doc.textFrames.getByName('{element_name}');"
            elif element_index is not None:
                get_element = f"textFrame = doc.textFrames[{element_index}];"

            font_code = ""
            if font_name:
                font_code = f'try {{ chars.textFont = app.textFonts.getByName("{font_name}"); }} catch(e) {{ return "ERROR: Font not found: {font_name}"; }}'

            size_code = f"chars.size = {font_size};" if font_size else ""
            tracking_code = f"chars.tracking = {tracking};" if tracking is not None else ""
            leading_code = f"chars.leading = {leading};" if leading else ""

            color_code = ""
            if color_rgb:
                color_code = f"""
                var color = new RGBColor();
                color.red = {color_rgb[0]};
                color.green = {color_rgb[1]};
                color.blue = {color_rgb[2]};
                chars.fillColor = color;
                """

            align_code = ""
            if alignment:
                justification = "LEFT" if alignment == "left" else "CENTER" if alignment == "center" else "RIGHT" if alignment == "right" else "FULLJUSTIFY"
                align_code = f"""
                var para = textFrame.paragraphs[0].paragraphAttributes;
                para.justification = Justification.{justification};
                """

            script = f'''
            (function() {{
                var doc = app.activeDocument;
                var textFrame = null;

                {get_element}

                if (!textFrame) {{
                    return "ERROR: Text element not found";
                }}

                var chars = textFrame.textRange.characterAttributes;

                {font_code}
                {size_code}
                {tracking_code}
                {leading_code}
                {color_code}
                {align_code}

                return "SUCCESS: Applied text style";
            }})();
            '''

            return run_illustrator_script(script)
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "recommend_korean_fonts":
        try:
            purpose = arguments.get("purpose", "body") if arguments else "body"
            recommendations = recommend_korean_fonts(purpose)

            result = f"# Korean Font Recommendations for '{purpose}'\n\n"
            for rec in recommendations:
                result += f"## {rec['name']} ({rec['family']})\n"
                result += f"- **Illustrator name**: `{rec['illustrator_name']}`\n"
                result += f"- **Recommended weights**: {', '.join(rec['recommended_weights'])}\n"
                result += f"- **Best for**: {', '.join(rec['reason']) if isinstance(rec['reason'], list) else rec['reason']}\n\n"

            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # ===== DESIGN VALIDATION TOOLS =====
    elif name == "verify_design":
        try:
            artboard_index = arguments.get("artboard_index", 0) if arguments else 0
            check_rules = arguments.get("check_rules") if arguments else None
            expected_layout = arguments.get("expected_layout") if arguments else None
            min_margin_mm = arguments.get("min_margin_mm", 3) if arguments else 3

            # Get document info first
            doc_info_result = get_document_info(True, 100)
            if not doc_info_result or doc_info_result[0].type != "text":
                return [types.TextContent(type="text", text="Failed to get document info")]

            try:
                doc_info = json.loads(doc_info_result[0].text)
            except:
                return [types.TextContent(type="text", text=f"Failed to parse document info: {doc_info_result[0].text}")]

            if "error" in doc_info:
                return [types.TextContent(type="text", text=f"Document error: {doc_info['error']}")]

            # Run validation
            validator = DesignValidator(doc_info)
            if min_margin_mm:
                validator.MIN_MARGIN_MM = min_margin_mm

            result = validator.validate(
                check_rules=check_rules,
                expected_layout=expected_layout,
                artboard_index=artboard_index
            )

            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            logging.error(f"Error verifying design: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "auto_fix_issues":
        try:
            issues = arguments.get("issues", []) if arguments else []
            fix_types = arguments.get("fix_types", ["alignment", "spacing", "margins"]) if arguments else ["alignment", "spacing", "margins"]

            if not issues:
                return [types.TextContent(type="text", text="No issues provided to fix")]

            # Filter issues by type
            filtered_issues = [i for i in issues if i.get("type") in fix_types]

            if not filtered_issues:
                return [types.TextContent(type="text", text="No matching issues to fix")]

            # Generate fix script
            fix_script = generate_fix_script(filtered_issues)

            return [types.TextContent(type="text", text=f"Generated fix script:\n\n```javascript\n{fix_script}\n```\n\nNote: Run this script using the 'run' tool to apply fixes.")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "design_iteration":
        try:
            artboard_index = arguments.get("artboard_index", 0) if arguments else 0
            auto_fix = arguments.get("auto_fix", False) if arguments else False
            min_score = arguments.get("min_score", 70) if arguments else 70
            include_render = arguments.get("include_render", True) if arguments else True

            results = []

            # 1. Verify design
            doc_info_result = get_document_info(True, 100)
            if not doc_info_result:
                return [types.TextContent(type="text", text="Failed to get document info")]

            try:
                doc_info = json.loads(doc_info_result[0].text)
            except:
                doc_info = {"error": "Failed to parse document info"}

            if "error" in doc_info:
                return [types.TextContent(type="text", text=f"Document error: {doc_info.get('error')}")]

            validator = DesignValidator(doc_info)
            validation_result = validator.validate(artboard_index=artboard_index)

            # 2. Include render if requested
            if include_render:
                render_result = render_artboard(artboard_index, 1.0)
                results.extend(render_result)

            # 3. Build iteration report
            report = {
                "iteration_complete": True,
                "score": validation_result["score"],
                "passed": validation_result["passed"],
                "meets_minimum": validation_result["score"] >= min_score,
                "total_issues": validation_result["total_issues"],
                "errors": validation_result["error_count"],
                "warnings": validation_result["warning_count"],
                "summary": validation_result["summary"],
                "issues": validation_result["issues"][:10]  # Limit to top 10 issues
            }

            if auto_fix and validation_result["issues"]:
                fix_script = generate_fix_script(validation_result["issues"])
                report["fix_script_generated"] = True
                report["fix_script"] = fix_script

            results.append(types.TextContent(type="text", text=json.dumps(report, indent=2)))
            return results
        except Exception as e:
            logging.error(f"Error in design iteration: {str(e)}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # ===== IMAGE ANALYSIS TOOLS =====
    elif name == "analyze_image_colors":
        try:
            image_path = arguments.get("image_path") if arguments else None
            num_colors = arguments.get("num_colors", 5) if arguments else 5

            if not image_path:
                return [types.TextContent(type="text", text="image_path is required")]

            result = analyze_image_colors(image_path=image_path, num_colors=num_colors)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "analyze_image_layout":
        try:
            image_path = arguments.get("image_path") if arguments else None

            if not image_path:
                return [types.TextContent(type="text", text="image_path is required")]

            result = analyze_image_layout(image_path=image_path)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "extract_text_from_image":
        try:
            image_path = arguments.get("image_path") if arguments else None
            language = arguments.get("language", "eng+kor") if arguments else "eng+kor"

            if not image_path:
                return [types.TextContent(type="text", text="image_path is required")]

            result = extract_text_ocr(image_path=image_path, language=language)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    else:
        error_msg = f"Unknown tool: {name}"
        logging.error(error_msg)
        raise ValueError(error_msg)

async def main():
    try:
        print("Initializing MCP server for Illustrator...", file=sys.stderr)
        sys.stderr.flush()
        logging.info("Initializing MCP server for Illustrator.")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("Server streams established, starting server...", file=sys.stderr)
            sys.stderr.flush()
            _print_client_config_hint()
            
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="illustrator",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
            print("Server finished running", file=sys.stderr)
            sys.stderr.flush()
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
        sys.stderr.flush()
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        raise

if __name__ == "__main__":
    try:
        print("Starting the main event loop...", file=sys.stderr)
        logging.info("Starting the main event loop.")
        asyncio.run(main())
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
