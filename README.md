# Illustrator MCP Server (Windows)

AI-powered Adobe Illustrator automation through Claude Desktop.

> Describe what you want — like *"draw a minimalist coffee shop logo"* — and Illustrator brings it to life!

## Features

### Core Tools
- **view** - Screenshot of Illustrator window
- **run** - Execute ExtendScript code directly
- **get_document_info** - Get document structure (layers, artboards, objects) as JSON
- **render_artboard** - Export specific artboard as PNG (independent of user view)

### Design Assistance
- **get_code_example** - Ready-to-use ExtendScript patterns
- **get_design_guide** - Typography, layout, logo/icon design principles
- **get_color_palette** - Curated color palettes (corporate, creative, minimal, etc.)

### MCP Prompts (Auto-context for Claude)
- **illustrator-expert** - General Illustrator expertise
- **logo-designer** - Logo design specialization
- **icon-designer** - Icon set design
- **print-designer** - Print design (business cards, flyers, etc.)

---

## Quick Install (Windows)

### Option 1: One-Click Install
```batch
# Double-click install.bat
# Or run in terminal:
.\install.bat
```

### Option 2: Manual Install

1. **Requirements**
   - Python 3.11+
   - Adobe Illustrator
   - Claude Desktop

2. **Install**
   ```bash
   cd illustrator-mcp
   python -m venv .venv
   .venv\Scripts\pip install -e .
   ```

3. **Configure Claude Desktop**

   Edit `%APPDATA%\Claude\claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "illustrator": {
         "command": "C:/path/to/illustrator-mcp/.venv/Scripts/python.exe",
         "args": ["C:/path/to/illustrator-mcp/illustrator/server.py"]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

---

## Usage Examples

### Basic Commands
```
"Show me the current Illustrator document"
→ Uses get_document_info

"Render the first artboard"
→ Uses render_artboard

"Create a blue rectangle 200x100 pixels"
→ Uses run with ExtendScript
```

### Design Tasks
```
"Design a minimal logo for TechStart"
→ Uses logo-designer prompt + design guides

"Create a set of 5 navigation icons in outline style"
→ Uses icon-designer prompt + icon guidelines

"Design a business card for John Smith, CEO"
→ Uses print-designer prompt + print specs
```

### Getting Help
```
"Show me ExtendScript examples for gradients"
→ Uses get_code_example

"What are the typography guidelines?"
→ Uses get_design_guide

"Give me a tech color palette"
→ Uses get_color_palette
```

---

## Available Resources

### Color Palettes
| Name | Description |
|------|-------------|
| corporate | Professional business colors |
| creative | Bold, vibrant agency colors |
| minimal | Clean black/white/gray |
| nature | Organic, earthy tones |
| tech | Modern tech company colors |
| warm | Sunset, coral, golden |
| cool | Ocean, mint, lavender |

### Code Example Categories
- **shapes** - rectangle, circle, polygon, star, line, bezier
- **text** - simple_text, styled_heading, paragraph_text, text_on_path
- **gradients** - linear, radial, multi-stop
- **logos** - circle_logo, text_logo, monogram_logo
- **icons** - home_icon, settings_icon, user_icon
- **layers** - create_layers, move_to_layer
- **export** - PNG, SVG, PDF

### Design Guides
- Typography (hierarchy, font pairings, spacing)
- Layout (grids, white space, alignment)
- Logo design (principles, types, sizing)
- Icon design (styles, grid sizes, consistency)
- Print specs (business card, flyer, poster)

---

## Architecture

```
Claude Desktop
    ↓ MCP Protocol
Illustrator MCP Server (Python)
    ↓ Windows COM (pywin32)
Adobe Illustrator
    ↓ ExtendScript Engine
Vector Graphics
```

### Key Components
- `server.py` - MCP server with tools and prompts
- `extendscript_library.py` - Code examples and utilities
- `design_guide.py` - Design principles and color palettes
- `prompt.py` - Prompt templates and suggestions

---

## For Developers

### Adding New Code Examples
Edit `extendscript_library.py`:
```python
SHAPE_EXAMPLES["my_shape"] = '''
var doc = app.activeDocument;
// Your ExtendScript code
'''
```

### Adding New Color Palettes
Edit `design_guide.py`:
```python
COLOR_PALETTES["my_palette"] = {
    "description": "My custom palette",
    "colors": {
        "primary": {"rgb": [255, 0, 0], "hex": "#FF0000", "usage": "Main color"}
    }
}
```

### Testing
```bash
# Test get_document_info
.venv\Scripts\python -c "from illustrator.server import get_document_info; print(get_document_info())"

# Test render_artboard
.venv\Scripts\python -c "from illustrator.server import render_artboard; print(render_artboard())"
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'mcp'"
```bash
.venv\Scripts\pip install -e .
```

### "Win32 COM not available"
```bash
.venv\Scripts\pip install pywin32
```

### "No document open"
Make sure Adobe Illustrator is running with a document open.

### Claude can't connect
1. Check `claude_desktop_config.json` paths use forward slashes
2. Restart Claude Desktop after config changes
3. Check MCP server logs in Claude Desktop developer tools

---

## License

MIT License - See LICENSE file

## Contributing

Pull requests welcome! Please open an issue first for major changes.
