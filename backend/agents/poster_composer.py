# Poster Composer
# Takes a text-free AI-generated background + structured copy (headline, sub-headline,
# highlights, CTA) and renders a complete marketing poster using Pillow.
# This is the "layered" approach: AI generates the background art, code renders the text —
# because AI image models cannot reliably render readable text inside an image.

import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# ── Font resolution (cross-platform: tries Windows fonts, falls back to Linux/Mac) ──

def _find_font(bold: bool = False) -> str:
    candidates = [
        # Windows
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Mac
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None  # Pillow will fall back to its built-in default bitmap font


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = _find_font(bold)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_centered_text(draw, text, font, center_x, y, fill, max_width=None, line_spacing=8):
    """Draw text horizontally centered at center_x, returns the y-position after the text."""
    if not text:
        return y
    lines = _wrap_text(text, font, max_width, draw) if max_width else [text]
    line_height = font.size + line_spacing
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text((center_x - w / 2, y), line, font=font, fill=fill)
        y += line_height
    return y


def _draw_checkmark(draw, x, y, size, color):
    """Draws a checkmark as actual vector lines (not a Unicode character) —
    this guarantees it renders correctly on every system, since some fonts
    don't include a glyph for ✓ and show a blank box instead."""
    # A simple two-stroke check, scaled to `size`
    p1 = (x, y + size * 0.5)
    p2 = (x + size * 0.35, y + size * 0.85)
    p3 = (x + size, y)
    draw.line([p1, p2], fill=color, width=max(2, int(size * 0.16)))
    draw.line([p2, p3], fill=color, width=max(2, int(size * 0.16)))


def _get_region_average_color(image: Image.Image, box) -> tuple:
    """Returns the average (r, g, b) of a region — used both for brightness
    detection and for deriving a color palette that actually matches
    whatever color the background really is (not a fixed preset)."""
    region = image.convert("RGB").crop(box)
    small = region.resize((1, 1))
    return small.getpixel((0, 0))


def _detect_is_light_background(avg_rgb: tuple) -> bool:
    r, g, b = avg_rgb
    brightness = (0.299 * r + 0.587 * g + 0.114 * b)
    return brightness > 165  # threshold tuned for readability


def _rgb_to_hsv(rgb):
    import colorsys
    r, g, b = [c / 255.0 for c in rgb]
    return colorsys.rgb_to_hsv(r, g, b)


def _hsv_to_rgb_hex(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255))


def _derive_palette_from_background(avg_rgb: tuple) -> dict:
    """Derives a complete, readable color palette FROM the actual detected
    background color — instead of picking from a fixed list of presets.
    This means whatever color the human asks for via regeneration feedback
    (red, green, purple, anything) automatically gets a matching, contrast-
    safe text/accent/footer palette, with no hardcoded color names anywhere.

    Approach: read the background's hue, then pick text/accent lightness
    and saturation based on whether the background itself is light or dark,
    so contrast is always preserved regardless of the hue.
    """
    h, s, v = _rgb_to_hsv(avg_rgb)
    is_light = _detect_is_light_background(avg_rgb)

    # Accent: a complementary-ish, vivid version of the background's own hue
    # shifted slightly so it doesn't disappear into the background, but still
    # feels related to it rather than an arbitrary gold/navy.
    accent_hue = (h + 0.5) % 1.0  # complementary hue
    if is_light:
        accent = _hsv_to_rgb_hex(accent_hue, min(0.65, s + 0.35), 0.55)
        text   = "#13181F"          # near-black, readable on light bg
        muted  = "#454F5C"          # dark gray
        primary = "#13181F"         # CTA button text color
    else:
        accent = _hsv_to_rgb_hex(accent_hue, min(0.55, s + 0.25), 0.85)
        text   = "#FFFFFF"          # white, readable on dark bg
        muted  = "#C7D0DC"          # light gray-blue
        primary = "#13181F"         # CTA button text stays dark for contrast against the bright accent button

    return {
        "primary": primary,
        "accent":  accent,
        "text":    text,
        "muted":   muted,
    }


def compose_poster(background_bytes: bytes, copy: dict, brand_colors: dict = None,
                    contact_footer: str = None) -> bytes:
    """
    copy = {
        "headline": str,
        "sub_headline": str,
        "highlights": [str, ...],
        "cta": str,
    }
    contact_footer: optional short string like "keydevs.pk  |  sales@keydevs.com  |  +92 321 7851671"
    rendered as a thin strip at the very bottom of the poster.

    Colors are NOT hardcoded to a fixed brand palette. Instead, the actual
    background color (whatever the human requested via feedback — red,
    green, purple, anything) is sampled from the image itself and used to
    derive a matching, contrast-safe text/accent palette automatically.
    Pass `brand_colors` to override this and force a specific fixed palette
    if ever needed.
    """
    base_for_detection = Image.open(BytesIO(background_bytes)).convert("RGB")
    W0, H0 = base_for_detection.size
    sample_box = (int(W0 * 0.15), int(H0 * 0.40), int(W0 * 0.85), int(H0 * 0.95))
    avg_rgb = _get_region_average_color(base_for_detection, sample_box)
    is_light_bg = _detect_is_light_background(avg_rgb)

    colors = brand_colors or _derive_palette_from_background(avg_rgb)

    base = Image.open(BytesIO(background_bytes)).convert("RGBA")
    W, H = base.size

    # ── Footer strip reserved at the very bottom for contact info ──
    footer_h = int(H * 0.055) if contact_footer else 0
    content_h = H - footer_h

    # ── Gradient overlay over the lower portion so text stays readable
    # regardless of the background art underneath. Direction/color of the
    # overlay flips depending on whether the background is light or dark. ──
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    overlay_top = int(content_h * 0.38)
    overlay_color = (255, 255, 255) if is_light_bg else (6, 16, 32)
    max_alpha = 165 if is_light_bg else 195
    for y in range(overlay_top, content_h):
        alpha = int(max_alpha * ((y - overlay_top) / (content_h - overlay_top)))
        odraw.line([(0, y), (W, y)], fill=(*overlay_color, alpha))
    # Solid footer background band
    if footer_h:
        footer_color = (255, 255, 255, 255) if is_light_bg else (6, 14, 28, 255)
        odraw.rectangle([0, content_h, W, H], fill=footer_color)
    base = Image.alpha_composite(base, overlay)

    draw = ImageDraw.Draw(base)
    center_x = W // 2
    margin = int(W * 0.10)
    content_width = W - 2 * margin

    headline_font   = _load_font(int(W * 0.054), bold=True)
    sub_font        = _load_font(int(W * 0.027), bold=False)
    highlight_font  = _load_font(int(W * 0.025), bold=False)
    cta_font        = _load_font(int(W * 0.028), bold=True)
    footer_font     = _load_font(int(W * 0.020), bold=False)

    # ── Measure total block height first so we can vertically center it
    # within the available lower portion, instead of guessing a fixed y ──
    headline_lines = _wrap_text(copy.get("headline", ""), headline_font, content_width, draw) if copy.get("headline") else []
    sub_lines       = _wrap_text(copy.get("sub_headline", ""), sub_font, content_width, draw) if copy.get("sub_headline") else []
    highlights      = copy.get("highlights", [])
    cta_text        = copy.get("cta", "")

    block_height = 0
    block_height += len(headline_lines) * (headline_font.size + 8)
    if sub_lines:
        block_height += 18 + len(sub_lines) * (sub_font.size + 6)
    if highlights:
        block_height += 26 + len(highlights) * (highlight_font.size + 16)
    if cta_text:
        block_height += 30 + (cta_font.size + 44)

    # Available vertical space for the text block (lower 62% of content area,
    # leaving headroom near the top for the background art to breathe)
    available_top = int(content_h * 0.36)
    available_bottom = int(content_h * 0.96)
    available_h = available_bottom - available_top
    y = available_top + max(0, (available_h - block_height) // 2)

    # ── Headline ──
    for line in headline_lines:
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        w = bbox[2] - bbox[0]
        draw.text((center_x - w / 2, y), line, font=headline_font, fill=colors["text"])
        y += headline_font.size + 8

    # ── Thin gold divider under the headline ──
    if headline_lines:
        y += 6
        divider_w = int(W * 0.10)
        draw.line([(center_x - divider_w / 2, y), (center_x + divider_w / 2, y)],
                   fill=colors["accent"], width=3)
        y += 18

    # ── Sub-headline ──
    for line in sub_lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        w = bbox[2] - bbox[0]
        draw.text((center_x - w / 2, y), line, font=sub_font, fill=colors["muted"])
        y += sub_font.size + 6
    if sub_lines:
        y += 26

    # ── Highlights with real vector checkmarks (not a font glyph) ──
    if highlights:
        check_size = highlight_font.size * 0.9
        gap = 14
        # measure widest line (checkmark + text) to center the whole block
        line_widths = []
        for h in highlights:
            bbox = draw.textbbox((0, 0), h, font=highlight_font)
            line_widths.append(check_size + gap + (bbox[2] - bbox[0]))
        block_width = max(line_widths) if line_widths else 0
        block_x = center_x - block_width / 2

        for h in highlights:
            _draw_checkmark(draw, block_x, y + 2, check_size, colors["accent"])
            draw.text((block_x + check_size + gap, y), h, font=highlight_font, fill=colors["text"])
            y += highlight_font.size + 16
        y += 18

    # ── CTA button ──
    if cta_text:
        bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        btn_w = text_w + 84
        btn_h = text_h + 46
        btn_x0 = center_x - btn_w / 2
        btn_y0 = y
        btn_x1 = btn_x0 + btn_w
        btn_y1 = btn_y0 + btn_h
        draw.rounded_rectangle([btn_x0, btn_y0, btn_x1, btn_y1], radius=btn_h // 2, fill=colors["accent"])
        draw.text((center_x - text_w / 2, btn_y0 + (btn_h - text_h) / 2 - bbox[1]), cta_text,
                   font=cta_font, fill=colors["primary"])

    # ── Footer strip: website | email | phone, centered, muted color ──
    if contact_footer and footer_h:
        fbbox = draw.textbbox((0, 0), contact_footer, font=footer_font)
        fw = fbbox[2] - fbbox[0]
        fh = fbbox[3] - fbbox[1]
        footer_y = content_h + (footer_h - fh) / 2 - fbbox[1]
        draw.text((center_x - fw / 2, footer_y), contact_footer, font=footer_font, fill=colors["muted"])

    out = BytesIO()
    base.convert("RGB").save(out, format="JPEG", quality=92)
    return out.getvalue()