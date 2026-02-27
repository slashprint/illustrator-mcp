"""
ExtendScript code library for Adobe Illustrator MCP Server
Provides ready-to-use code patterns and utility functions
"""

# Utility functions that should be included in scripts
UTILITY_FUNCTIONS = '''
// ===== UTILITY FUNCTIONS =====

// Create RGB Color
function makeRGBColor(r, g, b) {
    var color = new RGBColor();
    color.red = r;
    color.green = g;
    color.blue = b;
    return color;
}

// Create CMYK Color
function makeCMYKColor(c, m, y, k) {
    var color = new CMYKColor();
    color.cyan = c;
    color.magenta = m;
    color.yellow = y;
    color.black = k;
    return color;
}

// Create Gradient
function makeGradient(name, colors, positions) {
    var doc = app.activeDocument;
    var gradient = doc.gradients.add();
    gradient.name = name;
    gradient.type = GradientType.LINEAR;

    // Remove default stops
    while (gradient.gradientStops.length > 0) {
        gradient.gradientStops[0].remove();
    }

    for (var i = 0; i < colors.length; i++) {
        var stop = gradient.gradientStops.add();
        stop.rampPoint = positions[i];
        stop.color = colors[i];
    }
    return gradient;
}

// Apply gradient to item
function applyGradient(item, gradient, angle) {
    var gradientColor = new GradientColor();
    gradientColor.gradient = gradient;
    gradientColor.angle = angle || 0;
    item.fillColor = gradientColor;
}

// Center object on artboard
function centerOnArtboard(item, artboardIndex) {
    var doc = app.activeDocument;
    var ab = doc.artboards[artboardIndex || 0];
    var abRect = ab.artboardRect;
    var abCenterX = (abRect[0] + abRect[2]) / 2;
    var abCenterY = (abRect[1] + abRect[3]) / 2;

    item.position = [
        abCenterX - item.width / 2,
        abCenterY + item.height / 2
    ];
}

// Get or create layer by name
function getOrCreateLayer(name) {
    var doc = app.activeDocument;
    try {
        return doc.layers.getByName(name);
    } catch (e) {
        var layer = doc.layers.add();
        layer.name = name;
        return layer;
    }
}

// Convert points to mm
function mmToPoints(mm) {
    return mm * 2.834645669;
}

// Convert mm to points
function pointsToMm(points) {
    return points / 2.834645669;
}

// Create rounded rectangle
function roundedRect(x, y, width, height, radius) {
    var doc = app.activeDocument;
    return doc.pathItems.roundedRectangle(
        y, x, width, height, radius, radius
    );
}

// Create regular polygon
function regularPolygon(centerX, centerY, radius, sides) {
    var doc = app.activeDocument;
    return doc.pathItems.polygon(centerX, centerY, radius, sides);
}

// Create star
function star(centerX, centerY, outerRadius, innerRadius, points) {
    var doc = app.activeDocument;
    return doc.pathItems.star(centerX, centerY, outerRadius, innerRadius, points);
}

// Group items
function groupItems(items, name) {
    var doc = app.activeDocument;
    var group = doc.groupItems.add();
    group.name = name || "Group";
    for (var i = items.length - 1; i >= 0; i--) {
        items[i].move(group, ElementPlacement.PLACEATEND);
    }
    return group;
}

// Duplicate item
function duplicateItem(item, offsetX, offsetY) {
    var dup = item.duplicate();
    dup.position = [item.position[0] + offsetX, item.position[1] + offsetY];
    return dup;
}

// Set drop shadow
function addDropShadow(item, offsetX, offsetY, blur, opacity, color) {
    // Note: Requires creating effect through appearance panel
    // This is a simplified version using a duplicate
    var shadow = item.duplicate();
    shadow.zOrder(ZOrderMethod.SENDTOBACK);
    shadow.position = [item.position[0] + offsetX, item.position[1] - offsetY];
    shadow.opacity = opacity || 50;
    if (color) shadow.fillColor = color;
    return shadow;
}
'''

# Basic shapes code examples
SHAPE_EXAMPLES = {
    "rectangle": '''
var doc = app.activeDocument;
var rect = doc.pathItems.rectangle(-50, 50, 200, 100);  // top, left, width, height
var color = new RGBColor();
color.red = 66; color.green = 133; color.blue = 244;
rect.fillColor = color;
rect.stroked = false;
''',

    "circle": '''
var doc = app.activeDocument;
var circle = doc.pathItems.ellipse(-50, 50, 100, 100);  // top, left, width, height (equal = circle)
var color = new RGBColor();
color.red = 234; color.green = 67; color.blue = 53;
circle.fillColor = color;
circle.stroked = false;
''',

    "rounded_rectangle": '''
var doc = app.activeDocument;
var roundedRect = doc.pathItems.roundedRectangle(
    -50,    // top
    50,     // left
    200,    // width
    100,    // height
    20,     // horizontal radius
    20      // vertical radius
);
var color = new RGBColor();
color.red = 52; color.green = 168; color.blue = 83;
roundedRect.fillColor = color;
''',

    "polygon": '''
var doc = app.activeDocument;
// Regular hexagon
var hexagon = doc.pathItems.polygon(
    200,    // center X
    -150,   // center Y
    50,     // radius
    6       // number of sides
);
var color = new RGBColor();
color.red = 251; color.green = 188; color.blue = 5;
hexagon.fillColor = color;
''',

    "star": '''
var doc = app.activeDocument;
var star = doc.pathItems.star(
    200,    // center X
    -150,   // center Y
    50,     // outer radius
    25,     // inner radius
    5       // number of points
);
var color = new RGBColor();
color.red = 255; color.green = 215; color.blue = 0;
star.fillColor = color;
''',

    "line": '''
var doc = app.activeDocument;
var line = doc.pathItems.add();
line.setEntirePath([[50, -50], [250, -150]]);
line.filled = false;
line.stroked = true;
var strokeColor = new RGBColor();
strokeColor.red = 0; strokeColor.green = 0; strokeColor.blue = 0;
line.strokeColor = strokeColor;
line.strokeWidth = 2;
''',

    "bezier_curve": '''
var doc = app.activeDocument;
var curve = doc.pathItems.add();

// Define anchor points with handles
var points = [
    [50, -100],   // start point
    [150, -50],   // control point 1 (direction)
    [250, -150],  // control point 2
    [350, -100]   // end point
];

curve.setEntirePath(points);
curve.filled = false;
curve.stroked = true;
curve.strokeWidth = 3;
'''
}

# Text and typography examples
TEXT_EXAMPLES = {
    "simple_text": '''
var doc = app.activeDocument;
var textFrame = doc.textFrames.add();
textFrame.contents = "Hello, Illustrator!";
textFrame.position = [50, -50];

// Style the text
var textRange = textFrame.textRange;
textRange.characterAttributes.size = 24;
textRange.characterAttributes.fillColor = makeRGBColor(0, 0, 0);

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "styled_heading": '''
var doc = app.activeDocument;
var heading = doc.textFrames.add();
heading.contents = "BOLD HEADING";
heading.position = [50, -50];

var chars = heading.textRange.characterAttributes;
chars.size = 48;
chars.tracking = 100;  // letter spacing
chars.capitalization = FontCapsOption.ALLCAPS;
chars.fillColor = makeRGBColor(33, 33, 33);

// Try to set font (fallback if not available)
try {
    chars.textFont = app.textFonts.getByName("Helvetica-Bold");
} catch(e) {
    chars.textFont = app.textFonts[0];
}

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "paragraph_text": '''
var doc = app.activeDocument;

// Create area text
var rect = doc.pathItems.rectangle(-50, 50, 300, 200);
var areaText = doc.textFrames.areaText(rect);
areaText.contents = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";

var para = areaText.paragraphs[0].paragraphAttributes;
para.justification = Justification.LEFT;

var chars = areaText.textRange.characterAttributes;
chars.size = 12;
chars.leading = 18;  // line height
''',

    "text_on_path": '''
var doc = app.activeDocument;

// Create a curved path
var path = doc.pathItems.add();
path.setEntirePath([
    [50, -100],
    [150, -50],
    [250, -100],
    [350, -50]
]);
path.filled = false;
path.stroked = false;

// Add text on path
var textPath = doc.textFrames.pathText(path);
textPath.contents = "Text Along a Curved Path";
textPath.textRange.characterAttributes.size = 18;
'''
}

# Gradient examples
GRADIENT_EXAMPLES = {
    "linear_gradient": '''
var doc = app.activeDocument;
var rect = doc.pathItems.rectangle(-50, 50, 200, 100);

// Create gradient
var gradient = doc.gradients.add();
gradient.name = "BlueGradient";
gradient.type = GradientType.LINEAR;

// Set gradient stops
gradient.gradientStops[0].rampPoint = 0;
gradient.gradientStops[0].color = makeRGBColor(66, 133, 244);
gradient.gradientStops[1].rampPoint = 100;
gradient.gradientStops[1].color = makeRGBColor(25, 80, 180);

// Apply gradient
var gradColor = new GradientColor();
gradColor.gradient = gradient;
gradColor.angle = 45;
rect.fillColor = gradColor;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "radial_gradient": '''
var doc = app.activeDocument;
var circle = doc.pathItems.ellipse(-50, 50, 150, 150);

// Create radial gradient
var gradient = doc.gradients.add();
gradient.name = "SunGradient";
gradient.type = GradientType.RADIAL;

gradient.gradientStops[0].rampPoint = 0;
gradient.gradientStops[0].color = makeRGBColor(255, 255, 200);
gradient.gradientStops[1].rampPoint = 100;
gradient.gradientStops[1].color = makeRGBColor(255, 150, 0);

var gradColor = new GradientColor();
gradColor.gradient = gradient;
circle.fillColor = gradColor;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "multi_stop_gradient": '''
var doc = app.activeDocument;
var rect = doc.pathItems.rectangle(-50, 50, 300, 50);

// Create rainbow gradient
var gradient = doc.gradients.add();
gradient.name = "Rainbow";
gradient.type = GradientType.LINEAR;

// Add more stops
var colors = [
    {r: 255, g: 0, b: 0, pos: 0},
    {r: 255, g: 127, b: 0, pos: 20},
    {r: 255, g: 255, b: 0, pos: 40},
    {r: 0, g: 255, b: 0, pos: 60},
    {r: 0, g: 0, b: 255, pos: 80},
    {r: 139, g: 0, b: 255, pos: 100}
];

// Remove default stops and add new ones
while (gradient.gradientStops.length < colors.length) {
    gradient.gradientStops.add();
}

for (var i = 0; i < colors.length; i++) {
    gradient.gradientStops[i].rampPoint = colors[i].pos;
    gradient.gradientStops[i].color = makeRGBColor(colors[i].r, colors[i].g, colors[i].b);
}

var gradColor = new GradientColor();
gradColor.gradient = gradient;
gradColor.angle = 0;
rect.fillColor = gradColor;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
'''
}

# Logo design patterns
LOGO_EXAMPLES = {
    "circle_logo": '''
// Simple circle-based logo
var doc = app.activeDocument;
var layer = doc.layers.add();
layer.name = "Logo";

// Outer circle
var outer = doc.pathItems.ellipse(-50, 50, 100, 100);
outer.fillColor = makeRGBColor(41, 128, 185);
outer.stroked = false;

// Inner circle (cutout effect)
var inner = doc.pathItems.ellipse(-65, 65, 70, 70);
inner.fillColor = makeRGBColor(255, 255, 255);
inner.stroked = false;

// Center icon (simple shape)
var center = doc.pathItems.polygon(100, -100, 20, 3);  // triangle
center.fillColor = makeRGBColor(41, 128, 185);
center.stroked = false;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "text_logo": '''
// Text-based logo with icon
var doc = app.activeDocument;

// Company name
var text = doc.textFrames.add();
text.contents = "COMPANY";
text.position = [80, -90];
var chars = text.textRange.characterAttributes;
chars.size = 36;
chars.tracking = 200;
chars.fillColor = makeRGBColor(44, 62, 80);

// Icon (abstract shape)
var icon = doc.pathItems.rectangle(-50, 50, 60, 60);
icon.fillColor = makeRGBColor(231, 76, 60);

// Accent line
var line = doc.pathItems.add();
line.setEntirePath([[50, -120], [280, -120]]);
line.filled = false;
line.stroked = true;
line.strokeColor = makeRGBColor(231, 76, 60);
line.strokeWidth = 3;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "monogram_logo": '''
// Monogram style logo (overlapping letters)
var doc = app.activeDocument;

// Background circle
var bg = doc.pathItems.ellipse(-30, 30, 140, 140);
bg.fillColor = makeRGBColor(52, 73, 94);
bg.stroked = false;

// Letter A
var letterA = doc.textFrames.add();
letterA.contents = "A";
letterA.position = [50, -60];
var charsA = letterA.textRange.characterAttributes;
charsA.size = 72;
charsA.fillColor = makeRGBColor(255, 255, 255);

// Letter B (overlapping)
var letterB = doc.textFrames.add();
letterB.contents = "B";
letterB.position = [85, -60];
var charsB = letterB.textRange.characterAttributes;
charsB.size = 72;
charsB.fillColor = makeRGBColor(200, 200, 200);
letterB.opacity = 70;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
'''
}

# Icon design patterns
ICON_EXAMPLES = {
    "home_icon": '''
var doc = app.activeDocument;
var color = makeRGBColor(66, 66, 66);

// House body
var body = doc.pathItems.rectangle(-60, 30, 40, 30);
body.fillColor = color;
body.stroked = false;

// Roof (triangle)
var roof = doc.pathItems.add();
roof.setEntirePath([
    [25, -55],   // left
    [50, -30],   // top
    [75, -55]    // right
]);
roof.closed = true;
roof.fillColor = color;
roof.stroked = false;

// Door
var door = doc.pathItems.rectangle(-90, 42, 16, 25);
door.fillColor = makeRGBColor(255, 255, 255);
door.stroked = false;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "settings_icon": '''
var doc = app.activeDocument;
var color = makeRGBColor(66, 66, 66);

// Outer gear (using star shape approximation)
var gear = doc.pathItems.star(100, -100, 40, 30, 8);
gear.fillColor = color;
gear.stroked = false;

// Inner circle (hole)
var hole = doc.pathItems.ellipse(-75, 75, 30, 30);
hole.fillColor = makeRGBColor(255, 255, 255);
hole.stroked = false;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
''',

    "user_icon": '''
var doc = app.activeDocument;
var color = makeRGBColor(66, 66, 66);

// Head (circle)
var head = doc.pathItems.ellipse(-40, 75, 50, 50);
head.fillColor = color;
head.stroked = false;

// Body (rounded shape)
var body = doc.pathItems.ellipse(-100, 60, 80, 50);
body.fillColor = color;
body.stroked = false;

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
'''
}

# Layer management examples
LAYER_EXAMPLES = {
    "create_layers": '''
var doc = app.activeDocument;

// Create organized layer structure
var layers = ["Background", "Graphics", "Text", "Effects"];

for (var i = 0; i < layers.length; i++) {
    var layer = doc.layers.add();
    layer.name = layers[i];
}

// Set background layer to bottom and lock it
var bgLayer = doc.layers.getByName("Background");
bgLayer.zOrder(ZOrderMethod.SENDTOBACK);
bgLayer.locked = true;
''',

    "move_to_layer": '''
var doc = app.activeDocument;

// Create a shape
var rect = doc.pathItems.rectangle(-50, 50, 100, 100);
rect.fillColor = makeRGBColor(255, 0, 0);

// Get or create target layer
var targetLayer;
try {
    targetLayer = doc.layers.getByName("Graphics");
} catch(e) {
    targetLayer = doc.layers.add();
    targetLayer.name = "Graphics";
}

// Move shape to layer
rect.move(targetLayer, ElementPlacement.PLACEATEND);

function makeRGBColor(r, g, b) {
    var c = new RGBColor();
    c.red = r; c.green = g; c.blue = b;
    return c;
}
'''
}

# Layout and positioning examples
LAYOUT_EXAMPLES = {
    "position_element_mm": '''
// Position element at exact mm coordinates
function positionElementMm(element, xMm, yMm) {
    var ptPerMm = 2.834645669;
    element.position = [xMm * ptPerMm, -yMm * ptPerMm];
}

// Usage:
var doc = app.activeDocument;
var item = doc.pageItems[0];  // Get first item
positionElementMm(item, 10, 15);  // Position at 10mm, 15mm from top-left
''',

    "resize_element_mm": '''
// Resize element to exact mm dimensions
function resizeElementMm(element, widthMm, heightMm) {
    var ptPerMm = 2.834645669;
    var currentWidth = element.width;
    var currentHeight = element.height;

    var scaleX = (widthMm * ptPerMm) / currentWidth * 100;
    var scaleY = (heightMm * ptPerMm) / currentHeight * 100;

    element.resize(scaleX, scaleY);
}

var doc = app.activeDocument;
var item = doc.pageItems[0];
resizeElementMm(item, 50, 30);  // Resize to 50mm x 30mm
''',

    "align_elements_left": '''
// Align multiple elements to left edge
function alignLeft(items) {
    if (items.length < 2) return;

    // Find leftmost position
    var minLeft = items[0].position[0];
    for (var i = 1; i < items.length; i++) {
        if (items[i].position[0] < minLeft) {
            minLeft = items[i].position[0];
        }
    }

    // Align all items
    for (var i = 0; i < items.length; i++) {
        items[i].position = [minLeft, items[i].position[1]];
    }
}

var doc = app.activeDocument;
alignLeft(doc.selection);  // Align selected items
''',

    "align_elements_center": '''
// Align multiple elements to center (horizontal)
function alignCenterH(items) {
    if (items.length < 2) return;

    // Calculate center positions
    var centers = [];
    for (var i = 0; i < items.length; i++) {
        centers.push(items[i].position[0] + items[i].width / 2);
    }

    // Find average center
    var avgCenter = 0;
    for (var i = 0; i < centers.length; i++) {
        avgCenter += centers[i];
    }
    avgCenter /= centers.length;

    // Align all items to average center
    for (var i = 0; i < items.length; i++) {
        items[i].position = [avgCenter - items[i].width / 2, items[i].position[1]];
    }
}

var doc = app.activeDocument;
alignCenterH(doc.selection);
''',

    "distribute_evenly_horizontal": '''
// Distribute items evenly (horizontal)
function distributeHorizontal(items) {
    if (items.length < 3) return;

    // Sort by left position
    items.sort(function(a, b) { return a.position[0] - b.position[0]; });

    var firstLeft = items[0].position[0];
    var lastRight = items[items.length - 1].position[0] + items[items.length - 1].width;
    var totalItemWidth = 0;

    for (var i = 0; i < items.length; i++) {
        totalItemWidth += items[i].width;
    }

    var totalSpace = (lastRight - firstLeft) - totalItemWidth;
    var gap = totalSpace / (items.length - 1);

    var currentX = firstLeft;
    for (var i = 0; i < items.length; i++) {
        items[i].position = [currentX, items[i].position[1]];
        currentX += items[i].width + gap;
    }
}

var doc = app.activeDocument;
distributeHorizontal(doc.selection);
''',

    "create_grid": '''
// Create a layout grid with guides
function createGrid(columns, rows, gutterMm) {
    var doc = app.activeDocument;
    var ab = doc.artboards[doc.artboards.getActiveArtboardIndex()];
    var rect = ab.artboardRect;

    var ptPerMm = 2.834645669;
    var gutter = gutterMm * ptPerMm;

    var abWidth = rect[2] - rect[0];
    var abHeight = rect[1] - rect[3];

    var colWidth = (abWidth - gutter * (columns + 1)) / columns;
    var rowHeight = (abHeight - gutter * (rows + 1)) / rows;

    // Create grid layer
    var gridLayer;
    try {
        gridLayer = doc.layers.getByName("Grid");
    } catch(e) {
        gridLayer = doc.layers.add();
        gridLayer.name = "Grid";
    }

    // Create grid cells as rectangles
    for (var c = 0; c < columns; c++) {
        for (var r = 0; r < rows; r++) {
            var x = rect[0] + gutter + c * (colWidth + gutter);
            var y = rect[1] - gutter - r * (rowHeight + gutter);

            var cell = doc.pathItems.rectangle(y, x, colWidth, rowHeight);
            cell.filled = false;
            cell.stroked = true;
            cell.strokeWidth = 0.25;
            var strokeColor = new RGBColor();
            strokeColor.red = 200; strokeColor.green = 200; strokeColor.blue = 200;
            cell.strokeColor = strokeColor;
            cell.move(gridLayer, ElementPlacement.PLACEATEND);
        }
    }

    gridLayer.locked = true;
}

createGrid(4, 3, 5);  // 4 columns, 3 rows, 5mm gutter
''',

    "measure_elements": '''
// Measure distance between two elements
function measureDistance(item1, item2) {
    var ptToMm = 0.352778;

    var center1X = item1.position[0] + item1.width / 2;
    var center1Y = item1.position[1] - item1.height / 2;
    var center2X = item2.position[0] + item2.width / 2;
    var center2Y = item2.position[1] - item2.height / 2;

    var distanceX = Math.abs(center2X - center1X) * ptToMm;
    var distanceY = Math.abs(center2Y - center1Y) * ptToMm;
    var diagonal = Math.sqrt(distanceX * distanceX + distanceY * distanceY);

    return {
        horizontal_mm: Math.round(distanceX * 100) / 100,
        vertical_mm: Math.round(distanceY * 100) / 100,
        diagonal_mm: Math.round(diagonal * 100) / 100
    };
}

// Usage with selection
var doc = app.activeDocument;
if (doc.selection.length >= 2) {
    var result = measureDistance(doc.selection[0], doc.selection[1]);
    alert("Distance: " + result.horizontal_mm + "mm (H) x " + result.vertical_mm + "mm (V)");
}
''',

    "snap_to_grid": '''
// Snap element to nearest grid point
function snapToGrid(item, gridSizeMm) {
    var ptPerMm = 2.834645669;
    var gridSize = gridSizeMm * ptPerMm;

    var currentX = item.position[0];
    var currentY = item.position[1];

    var snappedX = Math.round(currentX / gridSize) * gridSize;
    var snappedY = Math.round(currentY / gridSize) * gridSize;

    item.position = [snappedX, snappedY];
}

var doc = app.activeDocument;
for (var i = 0; i < doc.selection.length; i++) {
    snapToGrid(doc.selection[i], 5);  // Snap to 5mm grid
}
'''
}

# Text styling examples
TEXT_STYLE_EXAMPLES = {
    "apply_text_style": '''
// Apply comprehensive text styling
function applyTextStyle(textFrame, options) {
    var chars = textFrame.textRange.characterAttributes;

    // Font
    if (options.fontName) {
        try {
            chars.textFont = app.textFonts.getByName(options.fontName);
        } catch(e) {
            // Font not found, keep current
        }
    }

    // Size
    if (options.fontSize) {
        chars.size = options.fontSize;
    }

    // Tracking (letter spacing)
    if (options.tracking !== undefined) {
        chars.tracking = options.tracking;  // In 1/1000 em
    }

    // Leading (line height)
    if (options.leading) {
        chars.leading = options.leading;
    }

    // Color
    if (options.color) {
        var color = new RGBColor();
        color.red = options.color[0];
        color.green = options.color[1];
        color.blue = options.color[2];
        chars.fillColor = color;
    }

    // Capitalization
    if (options.caps === "all") {
        chars.capitalization = FontCapsOption.ALLCAPS;
    } else if (options.caps === "small") {
        chars.capitalization = FontCapsOption.SMALLCAPS;
    }
}

var doc = app.activeDocument;
var textFrame = doc.textFrames[0];
applyTextStyle(textFrame, {
    fontName: "Helvetica-Bold",
    fontSize: 24,
    tracking: 50,
    leading: 28,
    color: [33, 33, 33]
});
''',

    "set_paragraph_style": '''
// Set paragraph styling
function setParagraphStyle(textFrame, options) {
    var para = textFrame.paragraphs[0].paragraphAttributes;

    // Justification
    if (options.align === "left") {
        para.justification = Justification.LEFT;
    } else if (options.align === "center") {
        para.justification = Justification.CENTER;
    } else if (options.align === "right") {
        para.justification = Justification.RIGHT;
    } else if (options.align === "justify") {
        para.justification = Justification.FULLJUSTIFY;
    }

    // Indentation
    if (options.firstLineIndent) {
        para.firstLineIndent = options.firstLineIndent;
    }

    // Space before/after
    if (options.spaceBefore) {
        para.spaceBefore = options.spaceBefore;
    }
    if (options.spaceAfter) {
        para.spaceAfter = options.spaceAfter;
    }
}

var doc = app.activeDocument;
var textFrame = doc.textFrames[0];
setParagraphStyle(textFrame, {
    align: "center",
    spaceBefore: 12,
    spaceAfter: 6
});
''',

    "list_system_fonts": '''
// List all available fonts
function listFonts(filterKorean) {
    var fonts = [];
    var koreanIndicators = ["Gothic", "Myungjo", "Dotum", "Gulim", "Batang",
                            "Malgun", "NanumGothic", "NanumMyeongjo", "Apple SD",
                            "KoPub", "Noto Sans KR", "Noto Serif KR", "Spoqa"];

    for (var i = 0; i < app.textFonts.length; i++) {
        var font = app.textFonts[i];
        var fontInfo = {
            name: font.name,
            family: font.family,
            style: font.style
        };

        if (filterKorean) {
            var isKorean = false;
            for (var j = 0; j < koreanIndicators.length; j++) {
                if (font.name.indexOf(koreanIndicators[j]) !== -1 ||
                    font.family.indexOf(koreanIndicators[j]) !== -1) {
                    isKorean = true;
                    break;
                }
            }
            if (isKorean) {
                fonts.push(fontInfo);
            }
        } else {
            fonts.push(fontInfo);
        }
    }

    return fonts;
}

// Get all Korean fonts
var koreanFonts = listFonts(true);
koreanFonts.length;  // Return count
''',

    "create_text_with_style": '''
// Create styled text frame
function createStyledText(content, x, y, style) {
    var doc = app.activeDocument;
    var textFrame = doc.textFrames.add();
    textFrame.contents = content;
    textFrame.position = [x, y];

    var chars = textFrame.textRange.characterAttributes;

    // Apply style
    if (style.fontName) {
        try { chars.textFont = app.textFonts.getByName(style.fontName); } catch(e) {}
    }
    if (style.fontSize) chars.size = style.fontSize;
    if (style.tracking) chars.tracking = style.tracking;
    if (style.color) {
        var c = new RGBColor();
        c.red = style.color[0];
        c.green = style.color[1];
        c.blue = style.color[2];
        chars.fillColor = c;
    }

    return textFrame;
}

var doc = app.activeDocument;
createStyledText("Hello World", 50, -50, {
    fontName: "Helvetica-Bold",
    fontSize: 36,
    tracking: 20,
    color: [0, 102, 204]
});
''',

    "adjust_kerning": '''
// Fine-tune character spacing (kerning)
function adjustKerning(textFrame, pairs) {
    // pairs: array of {position: index, value: kerning}
    var textRange = textFrame.textRange;

    for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i];
        if (pair.position < textRange.characters.length) {
            textRange.characters[pair.position].kerning = pair.value;
        }
    }
}

var doc = app.activeDocument;
var textFrame = doc.textFrames[0];

// Adjust kerning between specific character pairs
adjustKerning(textFrame, [
    {position: 0, value: -50},  // Tighten first pair
    {position: 3, value: 25}    // Loosen fourth pair
]);
'''
}

# Export examples
EXPORT_EXAMPLES = {
    "export_png": '''
var doc = app.activeDocument;
var file = new File("~/Desktop/export.png");

var options = new ExportOptionsPNG24();
options.antiAliasing = true;
options.transparency = true;
options.artBoardClipping = true;
options.horizontalScale = 100;
options.verticalScale = 100;

doc.exportFile(file, ExportType.PNG24, options);
''',

    "export_svg": '''
var doc = app.activeDocument;
var file = new File("~/Desktop/export.svg");

var options = new ExportOptionsSVG();
options.embedRasterImages = true;
options.fontSubsetting = SVGFontSubsetting.None;
options.documentEncoding = SVGDocumentEncoding.UTF8;

doc.exportFile(file, ExportType.SVG, options);
''',

    "export_pdf": '''
var doc = app.activeDocument;
var file = new File("~/Desktop/export.pdf");

var options = new PDFSaveOptions();
options.compatibility = PDFCompatibility.ACROBAT7;
options.preserveEditability = false;

doc.saveAs(file, options);
'''
}


def get_utility_functions() -> str:
    """Get utility functions to include in scripts."""
    return UTILITY_FUNCTIONS


def get_shape_example(shape_type: str) -> str:
    """Get example code for a specific shape."""
    return SHAPE_EXAMPLES.get(shape_type, "Shape type not found")


def get_text_example(text_type: str) -> str:
    """Get example code for text operations."""
    return TEXT_EXAMPLES.get(text_type, "Text type not found")


def get_gradient_example(gradient_type: str) -> str:
    """Get example code for gradients."""
    return GRADIENT_EXAMPLES.get(gradient_type, "Gradient type not found")


def get_logo_example(logo_type: str) -> str:
    """Get example code for logo patterns."""
    return LOGO_EXAMPLES.get(logo_type, "Logo type not found")


def get_icon_example(icon_type: str) -> str:
    """Get example code for icon patterns."""
    return ICON_EXAMPLES.get(icon_type, "Icon type not found")


def get_all_examples() -> dict:
    """Get all code examples organized by category."""
    return {
        "shapes": SHAPE_EXAMPLES,
        "text": TEXT_EXAMPLES,
        "gradients": GRADIENT_EXAMPLES,
        "logos": LOGO_EXAMPLES,
        "icons": ICON_EXAMPLES,
        "layers": LAYER_EXAMPLES,
        "export": EXPORT_EXAMPLES,
        "layout": LAYOUT_EXAMPLES,
        "text_style": TEXT_STYLE_EXAMPLES
    }


def list_available_examples() -> dict:
    """List all available example names by category."""
    return {
        "shapes": list(SHAPE_EXAMPLES.keys()),
        "text": list(TEXT_EXAMPLES.keys()),
        "gradients": list(GRADIENT_EXAMPLES.keys()),
        "logos": list(LOGO_EXAMPLES.keys()),
        "icons": list(ICON_EXAMPLES.keys()),
        "layers": list(LAYER_EXAMPLES.keys()),
        "export": list(EXPORT_EXAMPLES.keys()),
        "layout": list(LAYOUT_EXAMPLES.keys()),
        "text_style": list(TEXT_STYLE_EXAMPLES.keys())
    }


def get_layout_example(example_name: str) -> str:
    """Get example code for layout operations."""
    return LAYOUT_EXAMPLES.get(example_name, "Layout example not found")


def get_text_style_example(example_name: str) -> str:
    """Get example code for text styling."""
    return TEXT_STYLE_EXAMPLES.get(example_name, "Text style example not found")
