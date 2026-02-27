"""
Design principles and guidelines for Adobe Illustrator MCP Server
Provides knowledge base for creating professional designs
"""

# Color palettes for different purposes
COLOR_PALETTES = {
    "corporate": {
        "description": "Professional business colors",
        "colors": {
            "primary_blue": {"rgb": [41, 128, 185], "hex": "#2980B9", "usage": "Headers, CTAs"},
            "dark_gray": {"rgb": [44, 62, 80], "hex": "#2C3E50", "usage": "Text, backgrounds"},
            "light_gray": {"rgb": [236, 240, 241], "hex": "#ECF0F1", "usage": "Backgrounds"},
            "accent_green": {"rgb": [39, 174, 96], "hex": "#27AE60", "usage": "Success, positive"},
            "white": {"rgb": [255, 255, 255], "hex": "#FFFFFF", "usage": "Backgrounds, text"}
        }
    },
    "creative": {
        "description": "Bold, creative agency colors",
        "colors": {
            "vibrant_orange": {"rgb": [230, 126, 34], "hex": "#E67E22", "usage": "Primary accent"},
            "deep_purple": {"rgb": [142, 68, 173], "hex": "#8E44AD", "usage": "Secondary"},
            "bright_yellow": {"rgb": [241, 196, 15], "hex": "#F1C40F", "usage": "Highlights"},
            "coral": {"rgb": [231, 76, 60], "hex": "#E74C3C", "usage": "Emphasis"},
            "turquoise": {"rgb": [26, 188, 156], "hex": "#1ABC9C", "usage": "Fresh accents"}
        }
    },
    "minimal": {
        "description": "Clean, minimal design colors",
        "colors": {
            "black": {"rgb": [0, 0, 0], "hex": "#000000", "usage": "Primary text"},
            "dark_gray": {"rgb": [51, 51, 51], "hex": "#333333", "usage": "Secondary text"},
            "medium_gray": {"rgb": [153, 153, 153], "hex": "#999999", "usage": "Subtle elements"},
            "light_gray": {"rgb": [245, 245, 245], "hex": "#F5F5F5", "usage": "Backgrounds"},
            "white": {"rgb": [255, 255, 255], "hex": "#FFFFFF", "usage": "Primary background"}
        }
    },
    "nature": {
        "description": "Organic, nature-inspired colors",
        "colors": {
            "forest_green": {"rgb": [34, 139, 34], "hex": "#228B22", "usage": "Primary"},
            "earth_brown": {"rgb": [139, 90, 43], "hex": "#8B5A2B", "usage": "Accents"},
            "sky_blue": {"rgb": [135, 206, 235], "hex": "#87CEEB", "usage": "Secondary"},
            "sand": {"rgb": [244, 164, 96], "hex": "#F4A460", "usage": "Warm accents"},
            "cream": {"rgb": [255, 253, 208], "hex": "#FFFDD0", "usage": "Backgrounds"}
        }
    },
    "tech": {
        "description": "Modern tech company colors",
        "colors": {
            "electric_blue": {"rgb": [0, 122, 255], "hex": "#007AFF", "usage": "Primary"},
            "dark_slate": {"rgb": [30, 30, 30], "hex": "#1E1E1E", "usage": "Dark backgrounds"},
            "neon_green": {"rgb": [50, 205, 50], "hex": "#32CD32", "usage": "Success, active"},
            "cyber_purple": {"rgb": [138, 43, 226], "hex": "#8A2BE2", "usage": "Accents"},
            "silver": {"rgb": [192, 192, 192], "hex": "#C0C0C0", "usage": "Subtle elements"}
        }
    },
    "warm": {
        "description": "Warm, inviting colors",
        "colors": {
            "sunset_orange": {"rgb": [255, 99, 71], "hex": "#FF6347", "usage": "Primary"},
            "golden_yellow": {"rgb": [255, 215, 0], "hex": "#FFD700", "usage": "Highlights"},
            "terracotta": {"rgb": [204, 78, 92], "hex": "#CC4E5C", "usage": "Accents"},
            "peach": {"rgb": [255, 218, 185], "hex": "#FFDAB9", "usage": "Soft backgrounds"},
            "burgundy": {"rgb": [128, 0, 32], "hex": "#800020", "usage": "Deep accents"}
        }
    },
    "cool": {
        "description": "Cool, calming colors",
        "colors": {
            "ocean_blue": {"rgb": [0, 105, 148], "hex": "#006994", "usage": "Primary"},
            "mint_green": {"rgb": [152, 255, 152], "hex": "#98FF98", "usage": "Fresh accents"},
            "lavender": {"rgb": [230, 230, 250], "hex": "#E6E6FA", "usage": "Soft backgrounds"},
            "steel_blue": {"rgb": [70, 130, 180], "hex": "#4682B4", "usage": "Secondary"},
            "ice_gray": {"rgb": [220, 220, 220], "hex": "#DCDCDC", "usage": "Neutral"}
        }
    }
}

# Typography guidelines
TYPOGRAPHY_GUIDE = {
    "hierarchy": {
        "h1": {"size_range": "48-72pt", "weight": "Bold", "usage": "Main headlines"},
        "h2": {"size_range": "32-48pt", "weight": "Bold/Semibold", "usage": "Section headers"},
        "h3": {"size_range": "24-32pt", "weight": "Semibold", "usage": "Subsections"},
        "body": {"size_range": "14-18pt", "weight": "Regular", "usage": "Main content"},
        "caption": {"size_range": "10-12pt", "weight": "Regular/Light", "usage": "Labels, notes"},
        "small": {"size_range": "8-10pt", "weight": "Regular", "usage": "Fine print"}
    },
    "font_pairings": [
        {
            "name": "Modern Professional",
            "heading": "Helvetica Neue Bold",
            "body": "Helvetica Neue Regular",
            "style": "Clean, corporate"
        },
        {
            "name": "Creative Contrast",
            "heading": "Playfair Display Bold",
            "body": "Source Sans Pro Regular",
            "style": "Elegant, editorial"
        },
        {
            "name": "Tech Forward",
            "heading": "Roboto Bold",
            "body": "Roboto Regular",
            "style": "Modern, tech"
        },
        {
            "name": "Classic Serif",
            "heading": "Georgia Bold",
            "body": "Georgia Regular",
            "style": "Traditional, trustworthy"
        },
        {
            "name": "Minimal Sans",
            "heading": "Futura Bold",
            "body": "Futura Book",
            "style": "Geometric, minimal"
        }
    ],
    "spacing_rules": {
        "line_height": "1.4-1.6x font size for body text",
        "letter_spacing_headlines": "-2% to 0 (tighter)",
        "letter_spacing_body": "0 to +2% (normal to slightly open)",
        "paragraph_spacing": "0.5-1x line height between paragraphs"
    }
}

# Layout and composition rules
LAYOUT_PRINCIPLES = {
    "grid_systems": {
        "12_column": {
            "description": "Standard web/print grid",
            "usage": "Flexible layouts, responsive design",
            "column_ratios": [1, 2, 3, 4, 6, 12]
        },
        "golden_ratio": {
            "description": "1:1.618 ratio",
            "usage": "Natural, pleasing proportions",
            "value": 1.618
        },
        "rule_of_thirds": {
            "description": "Divide into 3x3 grid",
            "usage": "Photo composition, focal points",
            "intersections": "Place key elements at line intersections"
        }
    },
    "white_space": {
        "micro": "8-16px - Between related elements",
        "small": "16-24px - Between components",
        "medium": "32-48px - Between sections",
        "large": "64-96px - Major section breaks"
    },
    "alignment": {
        "left": "Default for text, creates natural reading flow",
        "center": "Headlines, short text, formal designs",
        "right": "Captions, numbers, special emphasis",
        "justified": "Formal documents, newspapers (use carefully)"
    },
    "visual_hierarchy": [
        "1. Size - Larger elements draw attention first",
        "2. Color - Bright/contrasting colors stand out",
        "3. Position - Top-left to bottom-right reading pattern",
        "4. Contrast - High contrast attracts the eye",
        "5. White space - Isolation creates importance",
        "6. Typography - Bold, italic create emphasis"
    ]
}

# Logo design guidelines
LOGO_GUIDELINES = {
    "principles": [
        "Simple - Easy to recognize and remember",
        "Memorable - Distinctive and unique",
        "Timeless - Avoid trendy elements that age quickly",
        "Versatile - Works at any size, in any color",
        "Appropriate - Reflects the brand's personality"
    ],
    "types": {
        "wordmark": {
            "description": "Company name as logo",
            "examples": "Google, Coca-Cola, Disney",
            "best_for": "Companies with unique, short names"
        },
        "lettermark": {
            "description": "Initials or acronym",
            "examples": "IBM, HBO, NASA",
            "best_for": "Long company names"
        },
        "symbol": {
            "description": "Icon or graphic mark",
            "examples": "Apple, Nike, Twitter",
            "best_for": "Established brands, global companies"
        },
        "combination": {
            "description": "Symbol + wordmark",
            "examples": "Adidas, Burger King, Lacoste",
            "best_for": "New brands building recognition"
        },
        "emblem": {
            "description": "Text inside a symbol",
            "examples": "Starbucks, Harley-Davidson, NFL",
            "best_for": "Traditional, prestigious brands"
        }
    },
    "sizing": {
        "minimum_size": "Ensure legibility at 16px/0.5inch",
        "clear_space": "Maintain padding equal to logo height/4",
        "aspect_ratio": "Keep consistent, don't stretch"
    },
    "color_usage": {
        "primary": "Main brand color version",
        "reversed": "White/light version for dark backgrounds",
        "monochrome": "Single color for limited applications",
        "black": "Black version for formal/print uses"
    }
}

# Icon design guidelines
ICON_GUIDELINES = {
    "style_types": {
        "outline": {
            "description": "Stroke-based, no fill",
            "stroke_width": "1.5-2px at 24px size",
            "best_for": "Modern, light interfaces"
        },
        "filled": {
            "description": "Solid filled shapes",
            "best_for": "Bold, prominent icons"
        },
        "duotone": {
            "description": "Two tones/opacities",
            "best_for": "Adding depth while staying simple"
        },
        "flat": {
            "description": "Solid colors, no gradients",
            "best_for": "Clean, modern design"
        }
    },
    "grid_sizes": {
        "16px": "Smallest usable size",
        "24px": "Standard UI icon",
        "32px": "Medium emphasis",
        "48px": "Large/featured icons",
        "64px+": "Illustration-style icons"
    },
    "consistency_rules": [
        "Use consistent stroke width across set",
        "Maintain same corner radius",
        "Align to pixel grid for crisp rendering",
        "Use same visual weight/density",
        "Keep similar level of detail"
    ]
}

# Print design specifications
PRINT_SPECS = {
    "business_card": {
        "standard_size": "3.5 x 2 inches (88.9 x 50.8 mm)",
        "bleed": "0.125 inches (3mm)",
        "safe_zone": "0.125 inches from edge",
        "resolution": "300 DPI",
        "color_mode": "CMYK"
    },
    "flyer_a4": {
        "size": "210 x 297 mm (8.27 x 11.69 inches)",
        "bleed": "3mm",
        "safe_zone": "5mm from edge",
        "resolution": "300 DPI",
        "color_mode": "CMYK"
    },
    "poster_a3": {
        "size": "297 x 420 mm (11.69 x 16.54 inches)",
        "bleed": "3mm",
        "resolution": "300 DPI for close viewing, 150 DPI acceptable for large format",
        "color_mode": "CMYK"
    },
    "letterhead": {
        "size": "8.5 x 11 inches (Letter) or A4",
        "margins": "0.5-1 inch",
        "logo_placement": "Top left or center",
        "color_mode": "CMYK"
    }
}

# Korean font database with recommendations
KOREAN_FONT_DATABASE = {
    "sans_serif": {
        "nanum_gothic": {
            "name": "NanumGothic",
            "family": "나눔고딕",
            "weights": ["Regular", "Bold", "ExtraBold"],
            "style": "Modern, clean sans-serif",
            "best_for": ["UI", "web", "body text", "presentations"],
            "characteristics": "Clear, readable, modern Korean sans-serif",
            "license": "OFL (Open Font License)",
            "illustrator_name": "NanumGothic"
        },
        "noto_sans_kr": {
            "name": "Noto Sans KR",
            "family": "노토 산스",
            "weights": ["Thin", "Light", "Regular", "Medium", "Bold", "Black"],
            "style": "Google's universal Korean font",
            "best_for": ["UI", "web", "apps", "cross-platform"],
            "characteristics": "Excellent character coverage, multiple weights",
            "license": "OFL",
            "illustrator_name": "NotoSansKR-Regular"
        },
        "spoqa_han_sans": {
            "name": "Spoqa Han Sans",
            "family": "스포카 한 산스",
            "weights": ["Thin", "Light", "Regular", "Bold"],
            "style": "Modern tech-oriented sans-serif",
            "best_for": ["tech companies", "startups", "apps"],
            "characteristics": "Clean, geometric, tech-friendly",
            "license": "OFL",
            "illustrator_name": "SpoqaHanSans-Regular"
        },
        "pretendard": {
            "name": "Pretendard",
            "family": "프리텐다드",
            "weights": ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"],
            "style": "Modern variable font",
            "best_for": ["web", "apps", "branding", "UI"],
            "characteristics": "9 weights, excellent for hierarchy",
            "license": "OFL",
            "illustrator_name": "Pretendard-Regular"
        },
        "malgun_gothic": {
            "name": "Malgun Gothic",
            "family": "맑은 고딕",
            "weights": ["Regular", "Bold"],
            "style": "Windows system font",
            "best_for": ["system UI", "documents", "general use"],
            "characteristics": "Pre-installed on Windows, reliable",
            "license": "Microsoft",
            "illustrator_name": "MalgunGothic"
        },
        "apple_sd_gothic_neo": {
            "name": "Apple SD Gothic Neo",
            "family": "애플 SD 고딕 네오",
            "weights": ["Thin", "UltraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy"],
            "style": "Apple system font",
            "best_for": ["macOS/iOS apps", "Apple ecosystem"],
            "characteristics": "Pre-installed on macOS/iOS, 9 weights",
            "license": "Apple",
            "illustrator_name": "AppleSDGothicNeo-Regular"
        }
    },
    "serif": {
        "nanum_myeongjo": {
            "name": "NanumMyeongjo",
            "family": "나눔명조",
            "weights": ["Regular", "Bold", "ExtraBold"],
            "style": "Traditional Korean serif",
            "best_for": ["books", "formal documents", "traditional designs"],
            "characteristics": "Classic, elegant, good for long text",
            "license": "OFL",
            "illustrator_name": "NanumMyeongjo"
        },
        "noto_serif_kr": {
            "name": "Noto Serif KR",
            "family": "노토 세리프",
            "weights": ["ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "Black"],
            "style": "Google's serif Korean font",
            "best_for": ["editorial", "magazines", "formal text"],
            "characteristics": "Excellent coverage, pairs with Noto Sans",
            "license": "OFL",
            "illustrator_name": "NotoSerifKR-Regular"
        },
        "kopub_batang": {
            "name": "KoPub Batang",
            "family": "코퍼브 바탕",
            "weights": ["Light", "Medium", "Bold"],
            "style": "Professional publishing serif",
            "best_for": ["publishing", "books", "academic"],
            "characteristics": "Designed for Korean publishing industry",
            "license": "OFL",
            "illustrator_name": "KoPubBatang-Light"
        }
    },
    "display": {
        "black_han_sans": {
            "name": "Black Han Sans",
            "family": "블랙 한 산스",
            "weights": ["Regular"],
            "style": "Bold display font",
            "best_for": ["headlines", "posters", "logos"],
            "characteristics": "Very bold, impactful, attention-grabbing",
            "license": "OFL",
            "illustrator_name": "BlackHanSans-Regular"
        },
        "jua": {
            "name": "Jua",
            "family": "주아",
            "weights": ["Regular"],
            "style": "Playful, rounded",
            "best_for": ["children's content", "casual designs", "friendly branding"],
            "characteristics": "Rounded, friendly, approachable",
            "license": "OFL",
            "illustrator_name": "Jua-Regular"
        },
        "do_hyeon": {
            "name": "Do Hyeon",
            "family": "도현",
            "weights": ["Regular"],
            "style": "Retro, bold",
            "best_for": ["retro designs", "posters", "titles"],
            "characteristics": "Vintage Korean style, distinctive",
            "license": "OFL",
            "illustrator_name": "DoHyeon-Regular"
        }
    },
    "handwriting": {
        "nanum_pen_script": {
            "name": "Nanum Pen Script",
            "family": "나눔손글씨 펜",
            "weights": ["Regular"],
            "style": "Casual handwriting",
            "best_for": ["personal notes", "casual designs", "signatures"],
            "characteristics": "Natural pen-written look",
            "license": "OFL",
            "illustrator_name": "NanumPenScript"
        },
        "nanum_brush_script": {
            "name": "Nanum Brush Script",
            "family": "나눔손글씨 붓",
            "weights": ["Regular"],
            "style": "Brush calligraphy",
            "best_for": ["traditional designs", "artistic projects"],
            "characteristics": "Brush-stroke effect, artistic",
            "license": "OFL",
            "illustrator_name": "NanumBrushScript"
        }
    }
}

# Design validation rules
DESIGN_VALIDATION_RULES = {
    "alignment": {
        "tolerance_pt": 2.0,
        "description": "Maximum allowed misalignment between elements that should be aligned",
        "severity_levels": {
            "error": 5.0,      # More than 5pt off is an error
            "warning": 2.0,   # 2-5pt off is a warning
            "info": 0.5       # 0.5-2pt off is info
        }
    },
    "spacing": {
        "variance_threshold": 0.15,  # 15% variance allowed
        "description": "Maximum allowed variance in spacing between similar elements",
        "min_spacing_pt": 8.0,       # Minimum spacing between elements
        "severity_levels": {
            "error": 0.3,     # 30%+ variance is error
            "warning": 0.15,  # 15-30% variance is warning
            "info": 0.05      # 5-15% variance is info
        }
    },
    "margins": {
        "business_card": {
            "min_margin_mm": 3.0,
            "recommended_mm": 5.0,
            "description": "Safe zone for business cards"
        },
        "flyer_a4": {
            "min_margin_mm": 5.0,
            "recommended_mm": 10.0,
            "description": "Safe zone for A4 flyers"
        },
        "poster": {
            "min_margin_mm": 10.0,
            "recommended_mm": 15.0,
            "description": "Safe zone for posters"
        },
        "default": {
            "min_margin_mm": 3.0,
            "recommended_mm": 5.0,
            "description": "Default safe zone"
        }
    },
    "typography": {
        "min_body_size_pt": 8.0,
        "min_caption_size_pt": 6.0,
        "recommended_body_size_pt": 10.0,
        "max_fonts": 3,
        "description": "Typography rules for readability"
    },
    "color": {
        "max_colors": 5,
        "min_contrast_ratio": 4.5,
        "description": "Color usage guidelines"
    },
    "hierarchy": {
        "heading_body_ratio_min": 1.5,
        "heading_body_ratio_max": 3.0,
        "description": "Size ratio between headings and body text"
    }
}

# Design do's and don'ts
DESIGN_RULES = {
    "do": [
        "Use a consistent color palette (3-5 colors max)",
        "Maintain visual hierarchy",
        "Leave enough white space",
        "Align elements to a grid",
        "Use high contrast for readability",
        "Test designs at different sizes",
        "Keep it simple and focused",
        "Use repetition for unity",
        "Create clear focal points",
        "Consider accessibility (color blindness, contrast)"
    ],
    "dont": [
        "Use too many fonts (stick to 2-3 max)",
        "Stretch or distort images/logos",
        "Use low-resolution images for print",
        "Ignore margins and safe zones",
        "Overuse effects (shadows, gradients)",
        "Center-align large blocks of text",
        "Use pure black (#000000) for large areas",
        "Mix too many visual styles",
        "Forget about the target audience",
        "Skip proofreading text"
    ]
}


def get_color_palette(palette_name: str) -> dict:
    """Get a specific color palette."""
    return COLOR_PALETTES.get(palette_name, None)


def get_all_palettes() -> dict:
    """Get all available color palettes."""
    return COLOR_PALETTES


def get_typography_guide() -> dict:
    """Get typography guidelines."""
    return TYPOGRAPHY_GUIDE


def get_layout_principles() -> dict:
    """Get layout and composition principles."""
    return LAYOUT_PRINCIPLES


def get_logo_guidelines() -> dict:
    """Get logo design guidelines."""
    return LOGO_GUIDELINES


def get_icon_guidelines() -> dict:
    """Get icon design guidelines."""
    return ICON_GUIDELINES


def get_print_specs(item_type: str = None) -> dict:
    """Get print specifications."""
    if item_type:
        return PRINT_SPECS.get(item_type, None)
    return PRINT_SPECS


def get_design_rules() -> dict:
    """Get design do's and don'ts."""
    return DESIGN_RULES


def get_full_design_guide() -> dict:
    """Get the complete design guide."""
    return {
        "color_palettes": COLOR_PALETTES,
        "typography": TYPOGRAPHY_GUIDE,
        "layout": LAYOUT_PRINCIPLES,
        "logo_design": LOGO_GUIDELINES,
        "icon_design": ICON_GUIDELINES,
        "print_specs": PRINT_SPECS,
        "rules": DESIGN_RULES,
        "korean_fonts": KOREAN_FONT_DATABASE,
        "validation_rules": DESIGN_VALIDATION_RULES
    }


def get_korean_font_database() -> dict:
    """Get the Korean font database."""
    return KOREAN_FONT_DATABASE


def get_korean_fonts_by_category(category: str) -> dict:
    """Get Korean fonts by category (sans_serif, serif, display, handwriting)."""
    return KOREAN_FONT_DATABASE.get(category, {})


def get_korean_font_info(font_key: str) -> dict:
    """Get information about a specific Korean font."""
    for category, fonts in KOREAN_FONT_DATABASE.items():
        if font_key in fonts:
            return fonts[font_key]
    return None


def recommend_korean_fonts(purpose: str) -> list:
    """
    Recommend Korean fonts based on purpose.

    Args:
        purpose: Use case like "heading", "body", "logo", "ui", "traditional"

    Returns:
        List of recommended fonts with details
    """
    recommendations = []

    purpose_mapping = {
        "heading": {
            "categories": ["display", "sans_serif"],
            "weights": ["Bold", "Black", "ExtraBold"],
            "fonts": ["black_han_sans", "pretendard", "noto_sans_kr"]
        },
        "body": {
            "categories": ["sans_serif", "serif"],
            "weights": ["Regular", "Medium"],
            "fonts": ["nanum_gothic", "noto_sans_kr", "pretendard", "nanum_myeongjo"]
        },
        "logo": {
            "categories": ["display", "sans_serif"],
            "weights": ["Bold", "Black", "Medium"],
            "fonts": ["black_han_sans", "pretendard", "spoqa_han_sans"]
        },
        "ui": {
            "categories": ["sans_serif"],
            "weights": ["Regular", "Medium", "Bold"],
            "fonts": ["pretendard", "noto_sans_kr", "spoqa_han_sans", "apple_sd_gothic_neo"]
        },
        "traditional": {
            "categories": ["serif", "handwriting"],
            "weights": ["Regular", "Medium"],
            "fonts": ["nanum_myeongjo", "noto_serif_kr", "nanum_brush_script"]
        },
        "casual": {
            "categories": ["display", "handwriting"],
            "weights": ["Regular"],
            "fonts": ["jua", "nanum_pen_script", "do_hyeon"]
        },
        "children": {
            "categories": ["display"],
            "weights": ["Regular", "Bold"],
            "fonts": ["jua", "nanum_pen_script"]
        },
        "formal": {
            "categories": ["serif", "sans_serif"],
            "weights": ["Regular", "Medium"],
            "fonts": ["noto_serif_kr", "kopub_batang", "nanum_myeongjo"]
        }
    }

    mapping = purpose_mapping.get(purpose.lower(), purpose_mapping["body"])

    for font_key in mapping["fonts"]:
        font_info = get_korean_font_info(font_key)
        if font_info:
            recommendations.append({
                "key": font_key,
                "name": font_info["name"],
                "family": font_info["family"],
                "recommended_weights": [w for w in font_info["weights"] if w in mapping["weights"]] or font_info["weights"][:2],
                "illustrator_name": font_info["illustrator_name"],
                "reason": font_info["best_for"]
            })

    return recommendations


def get_validation_rules() -> dict:
    """Get design validation rules."""
    return DESIGN_VALIDATION_RULES


def get_validation_rule(rule_type: str) -> dict:
    """Get a specific validation rule."""
    return DESIGN_VALIDATION_RULES.get(rule_type, {})


def get_margin_rule(design_type: str = "default") -> dict:
    """Get margin rules for a specific design type."""
    margins = DESIGN_VALIDATION_RULES.get("margins", {})
    return margins.get(design_type, margins.get("default", {}))
