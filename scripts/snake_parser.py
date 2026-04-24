#!/usr/bin/env python3
"""
Snake SVG Parser and Embedder

Parses Platane/snk generated snake.svg and prepares it for embedding
into the terminal widget SVG with proper CSS scoping and theme adaptation.
"""

import re
from pathlib import Path
from typing import Dict, Optional


# Theme color mappings for snake animation.
# --cb  border (semi-transparent)   --cs  snake body color
# --ce  empty cell (= bg color)     --c0..c4  contribution levels 0..4
THEME_COLORS = {
    'catppuccin': {
        '--cb': '#45475a0a',
        '--cs': '#cba6f7',   # Mauve
        '--ce': '#1e1e2e',
        '--c0': '#1e1e2e', '--c1': '#313244', '--c2': '#45475a',
        '--c3': '#585b70', '--c4': '#cba6f7',
    },
    'nord': {
        '--cb': '#4c566a0a',
        '--cs': '#88c0d0',   # Frost
        '--ce': '#2e3440',
        '--c0': '#2e3440', '--c1': '#3b4252', '--c2': '#434c5e',
        '--c3': '#4c566a', '--c4': '#88c0d0',
    },
    'gruvbox': {
        '--cb': '#3c38360a',
        '--cs': '#b8bb26',   # Yellow-green
        '--ce': '#282828',
        '--c0': '#282828', '--c1': '#3c3836', '--c2': '#504945',
        '--c3': '#665c54', '--c4': '#b8bb26',
    },
    'tokyo_night': {          # kept as alias target
        '--cb': '#41486811',
        '--cs': '#7aa2f7',   # Blue
        '--ce': '#1a1b26',
        '--c0': '#1a1b26', '--c1': '#24283b', '--c2': '#414868',
        '--c3': '#565f89', '--c4': '#7aa2f7',
    },
    'tokyo_night_storm': {
        '--cb': '#3b426111',
        '--cs': '#7aa2f7',   # Blue
        '--ce': '#24283b',
        '--c0': '#24283b', '--c1': '#1f2335', '--c2': '#3b4261',
        '--c3': '#787c99', '--c4': '#7aa2f7',
    },
    'rose_pine': {
        '--cb': '#26233a11',
        '--cs': '#c4a7e7',   # Purple
        '--ce': '#191724',
        '--c0': '#191724', '--c1': '#1f1d2e', '--c2': '#26233a',
        '--c3': '#6e6a86', '--c4': '#c4a7e7',
    },
    'everforest': {
        '--cb': '#3d484d11',
        '--cs': '#a7c080',   # Green
        '--ce': '#2d353b',
        '--c0': '#2d353b', '--c1': '#272e33', '--c2': '#3d484d',
        '--c3': '#859289', '--c4': '#a7c080',
    },
}

# Aliases mirror themes.py so the same theme name always works.
THEME_ALIASES = {
    'tokyo_night': 'tokyo_night_storm',
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
    """Replace snake colors with theme-appropriate colors and inline all var() refs.

    Two-pass approach:
      1. Update the :root{} variable definitions (fixes the values at the source).
      2. Inline every remaining var(--xx) reference with the hex value directly.
         This is crucial: GitHub's SVG renderer may strip :root{} blocks from
         nested SVGs, leaving all fill:var(--xx) declarations unresolved (= black).
         Inlining makes the CSS independent of CSS custom-property support.
    """
    # Resolve alias (e.g. 'rose_pine' is defined directly; 'tokyo_night' → storm)
    resolved = THEME_ALIASES.get(theme, theme)
    colors = THEME_COLORS.get(resolved, THEME_COLORS.get(theme, THEME_COLORS['catppuccin']))

    # Pass 1: update :root variable definitions.
    # The last var in :root ends with } not ; — match both terminators.
    for var, value in colors.items():
        style = re.sub(
            rf'{re.escape(var)}:\s*[^;}}]+(?=[;}}])',
            f'{var}:{value}',
            style,
        )

    # Pass 2: inline every var(--xx) occurrence with its hex value.
    # After this the CSS contains no CSS custom-property references at all.
    for var, value in colors.items():
        style = style.replace(f'var({var})', value)

    return style


def prepare_embedded_snake(
    svg_path: Path,
    theme: str = 'catppuccin',
    prefix: str = '',          # prefixing removed: our CSS classes don't conflict
    target_width: float = 740.0,
) -> Optional[str]:
    """Prepare snake SVG for embedding into the terminal widget SVG.

    Returns a nested <svg> string ready for {{ snake_content | safe }},
    or None if snake.svg does not exist.
    """
    parsed = parse_snake_svg(svg_path)
    if parsed is None:
        return None

    # Adapt colors (+ inline all var() refs so no CSS-variable dependency).
    themed_style = adapt_snake_colors(parsed['style'], theme)

    # Remove the now-redundant :root{...} block to keep output clean.
    themed_style = re.sub(r':root\s*\{[^}]*\}', '', themed_style)

    # viewBox geometry
    viewbox_parts = parsed['viewbox'].split()
    if len(viewbox_parts) >= 4:
        vb_x, vb_y, vb_width, vb_height = viewbox_parts
    else:
        vb_x, vb_y, vb_width, vb_height = '-16', '-32', '880', '192'

    original_width = float(vb_width)
    original_height = float(vb_height)
    scale = target_width / original_width
    scaled_height = original_height * scale

    # Use the raw (non-prefixed) content directly.
    content = parsed['content']

    embedded = (
        f'<svg width="{target_width}" height="{scaled_height}"'
        f' viewBox="{vb_x} {vb_y} {vb_width} {vb_height}"'
        f' preserveAspectRatio="xMidYMid meet">\n'
        f'  <defs>\n'
        f'    <style type="text/css">{themed_style}</style>\n'
        f'  </defs>\n'
        f'  <g>\n'
        f'    {content}\n'
        f'  </g>\n'
        f'</svg>'
    )

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
