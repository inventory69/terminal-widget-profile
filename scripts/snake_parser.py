#!/usr/bin/env python3
"""
Snake SVG Parser and Embedder

Parses Platane/snk generated snake.svg and prepares it for embedding
into the terminal widget SVG with proper CSS scoping and theme adaptation.
"""

import re
from pathlib import Path
from typing import Dict, Optional


# Theme color mappings for snake animation
THEME_COLORS = {
    'catppuccin': {
        '--cb': '#45475a0a',   # Border (semi-transparent)
        '--cs': '#cba6f7',     # Snake color (Mauve)
        '--ce': '#1e1e2e',     # Empty cell
        '--c0': '#1e1e2e',     # Level 0
        '--c1': '#313244',     # Level 1
        '--c2': '#45475a',     # Level 2
        '--c3': '#585b70',     # Level 3
        '--c4': '#cba6f7',     # Level 4 (Mauve)
    },
    'nord': {
        '--cb': '#4c566a0a',
        '--cs': '#88c0d0',     # Frost
        '--ce': '#2e3440',
        '--c0': '#2e3440',
        '--c1': '#3b4252',
        '--c2': '#434c5e',
        '--c3': '#4c566a',
        '--c4': '#88c0d0',
    },
    'gruvbox': {
        '--cb': '#3c38360a',
        '--cs': '#b8bb26',     # Green
        '--ce': '#282828',
        '--c0': '#282828',
        '--c1': '#3c3836',
        '--c2': '#504945',
        '--c3': '#665c54',
        '--c4': '#b8bb26',
    },
    'tokyo_night': {
        '--cb': '#414868aa',
        '--cs': '#7aa2f7',     # Blue
        '--ce': '#1a1b26',
        '--c0': '#1a1b26',
        '--c1': '#24283b',
        '--c2': '#414868',
        '--c3': '#565f89',
        '--c4': '#7aa2f7',
    }
}


def parse_snake_svg(svg_path: Path) -> Optional[Dict[str, str]]:
    """
    Parse snake.svg and extract style and content.
    
    Args:
        svg_path: Path to the snake.svg file
        
    Returns:
        Dictionary with 'style' and 'content' keys, or None if file doesn't exist
    """
    if not svg_path.exists():
        return None
        
    svg_content = svg_path.read_text(encoding='utf-8')
    
    # Extract style block
    style_match = re.search(r'<style>(.*?)</style>', svg_content, re.DOTALL)
    style = style_match.group(1) if style_match else ""
    
    # Format CSS: add line breaks after closing braces for better browser compatibility
    # Some browsers struggle with extremely long single-line CSS (60KB+ on one line)
    if style:
        style = re.sub(r'}(?=[^}])', '}\n', style)
    
    # Extract body (everything between </style> and </svg>)
    body_match = re.search(r'</style>(.*?)</svg>', svg_content, re.DOTALL)
    body = body_match.group(1).strip() if body_match else ""
    
    # Extract viewBox for scale calculation
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
    viewbox = viewbox_match.group(1) if viewbox_match else "-16 -32 880 192"
    
    return {
        'style': style,
        'content': body,
        'viewbox': viewbox
    }


def scope_snake_css(style: str, prefix: str = "snk-") -> str:
    """
    Add prefix to all CSS classes to avoid conflicts with terminal CSS.
    
    Args:
        style: Original CSS content
        prefix: Prefix to add to class names
        
    Returns:
        Scoped CSS content
    """
    # First scope classes with numbers/letters (.c0, .c1, .u0, .s0, etc.)
    scoped = re.sub(r'\.([cus])([0-9a-z]+)', f'.{prefix}\\1\\2', style)
    
    # Then scope single-letter classes (.c, .u, .s) - matches before {, comma, or dot
    scoped = re.sub(r'\.([cus])(?=\s*[{,\.])', f'.{prefix}\\1', scoped)
    
    return scoped


def scope_snake_content(content: str, prefix: str = "snk-") -> str:
    """
    Add prefix to all class attributes in SVG elements.
    
    Args:
        content: Original SVG content
        prefix: Prefix to add to class names
        
    Returns:
        Scoped SVG content
    """
    def replace_class(match):
        classes = match.group(1)
        # Split classes and prefix each
        new_classes = ' '.join(f'{prefix}{c}' for c in classes.split())
        return f'class="{new_classes}"'
    
    return re.sub(r'class="([^"]+)"', replace_class, content)


def adapt_snake_colors(style: str, theme: str) -> str:
    """
    Replace snake colors with theme-appropriate colors.
    
    Args:
        style: CSS content
        theme: Theme name (catppuccin, nord, gruvbox, tokyo_night)
        
    Returns:
        CSS with adapted colors
    """
    colors = THEME_COLORS.get(theme, THEME_COLORS['catppuccin'])
    
    for var, value in colors.items():
        # Replace CSS custom property definitions in :root
        # Use [^;}]+ to stop at both semicolons AND closing braces
        style = re.sub(
            rf'{re.escape(var)}:\s*[^;}}]+;',
            f'{var}:{value};',
            style
        )
    
    return style


def prepare_embedded_snake(
    svg_path: Path,
    theme: str = 'catppuccin',
    prefix: str = 'snk-',
    target_width: float = 740.0
) -> Optional[str]:
    """
    Main function: Prepare snake SVG for embedding into terminal widget.
    
    Args:
        svg_path: Path to snake.svg file
        theme: Color theme name
        prefix: CSS class prefix for scoping
        target_width: Target width for scaling (default: 740px to fit in terminal)
        
    Returns:
        String with scoped <style> and SVG content ready for embedding,
        or None if snake.svg doesn't exist
    """
    parsed = parse_snake_svg(svg_path)
    
    if parsed is None:
        return None
    
    # 1. Scope CSS classes
    scoped_style = scope_snake_css(parsed['style'], prefix)
    
    # 2. Adapt colors to theme
    themed_style = adapt_snake_colors(scoped_style, theme)
    
    # 3. Scope SVG content classes
    scoped_content = scope_snake_content(parsed['content'], prefix)
    
    # 4. Get original viewBox
    viewbox_parts = parsed['viewbox'].split()
    if len(viewbox_parts) >= 4:
        vb_x, vb_y, vb_width, vb_height = viewbox_parts
        original_width = float(vb_width)
    else:
        vb_x, vb_y, vb_width, vb_height = "-16", "-32", "880", "192"
        original_width = 880
    
    # 5. Calculate scaled height
    original_height = float(vb_height)
    scale = target_width / original_width
    scaled_height = original_height * scale
    
    # 6. Build embedded content - use nested SVG with viewBox for proper clipping
    # This ensures snake content stays within bounds even if coords exceed target_width
    # Note: No xmlns on nested SVG - it inherits from parent
    embedded = f'''<svg width="{target_width}" height="{scaled_height}" viewBox="{vb_x} {vb_y} {vb_width} {vb_height}" preserveAspectRatio="xMidYMid meet">
  <defs>
    <style type="text/css">{themed_style}</style>
  </defs>
  <g class="{prefix}container">
    {scoped_content}
  </g>
</svg>'''
    
    return embedded


def get_snake_dimensions(svg_path: Path, target_width: float = 740.0) -> Dict[str, float]:
    """
    Calculate dimensions for the embedded snake.
    
    Args:
        svg_path: Path to snake.svg
        target_width: Target width after scaling
        
    Returns:
        Dictionary with 'width', 'height', and 'viewbox'
    """
    parsed = parse_snake_svg(svg_path)
    
    if parsed is None:
        return {'width': target_width, 'height': 160, 'viewbox': '-16 -32 880 192'}
    
    viewbox_parts = parsed['viewbox'].split()
    if len(viewbox_parts) >= 4:
        original_width = float(viewbox_parts[2])
        original_height = float(viewbox_parts[3])
        scale = target_width / original_width
        scaled_height = original_height * scale
    else:
        original_width = 880
        original_height = 192
        scale = target_width / 880
        scaled_height = 192 * scale
    
    return {
        'width': target_width,
        'height': scaled_height,
        'viewbox': parsed['viewbox']
    }


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        snake_path = Path(sys.argv[1])
    else:
        snake_path = Path(__file__).parent.parent / "snake.svg"
    
    if snake_path.exists():
        print(f"Parsing {snake_path}...")
        result = prepare_embedded_snake(snake_path, theme='catppuccin')
        if result:
            print(f"Successfully prepared snake SVG ({len(result)} chars)")
            print(f"\nFirst 500 chars:\n{result[:500]}...")
        else:
            print("Failed to parse snake SVG")
    else:
        print(f"Snake SVG not found at {snake_path}")
