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
    if not text:
        return []
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


def _draw_checkmark(draw, x, y, size, color):
    """Draws a checkmark as actual vector lines (not a Unicode character) —
    this guarantees it renders correctly on every system, since some fonts
    don't include a glyph for ✓ and show a blank box instead."""
    p1 = (x, y + size * 0.5)
    p2 = (x + size * 0.35, y + size * 0.85)
    p3 = (x + size, y)
    draw.line([p1, p2], fill=color, width=max(2, int(size * 0.16)))
    draw.line([p2, p3], fill=color, width=max(2, int(size * 0.16)))


def _get_region_average_color(image: Image.Image, box) -> tuple:
    region = image.convert("RGB").crop(box)
    small = region.resize((1, 1))
    return small.getpixel((0, 0))


def _detect_is_light_background(avg_rgb: tuple) -> bool:
    r, g, b = avg_rgb
    brightness = (0.299 * r + 0.587 * g + 0.114 * b)
    return brightness > 165


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
    background color — no hardcoded preset colors. Whatever color the human
    requests via regeneration feedback automatically gets a matching,
    contrast-safe text/accent/footer palette."""
    h, s, v = _rgb_to_hsv(avg_rgb)
    is_light = _detect_is_light_background(avg_rgb)

    accent_hue = (h + 0.5) % 1.0  # complementary hue
    if is_light:
        accent  = _hsv_to_rgb_hex(accent_hue, min(0.65, s + 0.35), 0.55)
        text    = "#13181F"
        muted   = "#454F5C"
        primary = "#13181F"
    else:
        accent  = _hsv_to_rgb_hex(accent_hue, min(0.55, s + 0.25), 0.85)
        text    = "#FFFFFF"
        muted   = "#C7D0DC"
        primary = "#13181F"

    return {"primary": primary, "accent": accent, "text": text, "muted": muted}


def _draw_text_block(draw, x_left, x_right, y_start, y_end, copy, colors, footer_text=None,
                      footer_color=None, align="center"):
    """Shared text-block renderer used by both layouts. Draws headline,
    divider, sub-headline, highlights, and CTA within the horizontal band
    [x_left, x_right] and vertical band [y_start, y_end].
    align: "center" or "left" — controls text alignment within the block."""
    block_width = x_right - x_left
    block_center_x = x_left + block_width / 2
    W_ref = block_width  # used for proportional font sizing

    headline_font  = _load_font(int(W_ref * 0.11), bold=True)
    sub_font       = _load_font(int(W_ref * 0.052), bold=False)
    highlight_font = _load_font(int(W_ref * 0.046), bold=False)
    cta_font       = _load_font(int(W_ref * 0.052), bold=True)

    headline_lines = _wrap_text(copy.get("headline", ""), headline_font, block_width, draw)
    sub_lines      = _wrap_text(copy.get("sub_headline", ""), sub_font, block_width, draw)
    highlights     = copy.get("highlights", [])
    cta_text       = copy.get("cta", "")

    # Measure total height to vertically center within [y_start, y_end]
    block_height = 0
    block_height += len(headline_lines) * (headline_font.size + 10)
    if headline_lines:
        block_height += 24  # divider spacing
    if sub_lines:
        block_height += len(sub_lines) * (sub_font.size + 8) + 20
    if highlights:
        block_height += len(highlights) * (highlight_font.size + 18) + 20
    if cta_text:
        block_height += (cta_font.size + 46) + 24

    available_h = y_end - y_start
    y = y_start + max(0, (available_h - block_height) / 2)

    def text_x(line_width):
        if align == "left":
            return x_left
        return block_center_x - line_width / 2

    # Headline
    for line in headline_lines:
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        w = bbox[2] - bbox[0]
        draw.text((text_x(w), y), line, font=headline_font, fill=colors["text"])
        y += headline_font.size + 10

    if headline_lines:
        y += 8
        divider_w = block_width * 0.22
        dx = x_left if align == "left" else block_center_x - divider_w / 2
        draw.line([(dx, y), (dx + divider_w, y)], fill=colors["accent"], width=3)
        y += 22

    # Sub-headline
    for line in sub_lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        w = bbox[2] - bbox[0]
        draw.text((text_x(w), y), line, font=sub_font, fill=colors["muted"])
        y += sub_font.size + 8
    if sub_lines:
        y += 20

    # Highlights
    if highlights:
        check_size = highlight_font.size * 0.85
        gap = 14
        if align == "left":
            block_x = x_left
        else:
            line_widths = []
            for h in highlights:
                bbox = draw.textbbox((0, 0), h, font=highlight_font)
                line_widths.append(check_size + gap + (bbox[2] - bbox[0]))
            bw = max(line_widths) if line_widths else 0
            block_x = block_center_x - bw / 2

        for h in highlights:
            _draw_checkmark(draw, block_x, y + 2, check_size, colors["accent"])
            draw.text((block_x + check_size + gap, y), h, font=highlight_font, fill=colors["text"])
            y += highlight_font.size + 18
        y += 20

    # CTA button
    if cta_text:
        bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        btn_w = text_w + 84
        btn_h = text_h + 46
        btn_x0 = x_left if align == "left" else block_center_x - btn_w / 2
        btn_y0 = y
        draw.rounded_rectangle([btn_x0, btn_y0, btn_x0 + btn_w, btn_y0 + btn_h],
                                 radius=btn_h // 2, fill=colors["accent"])
        draw.text((btn_x0 + (btn_w - text_w) / 2, btn_y0 + (btn_h - text_h) / 2 - bbox[1]),
                   cta_text, font=cta_font, fill=colors["primary"])
        y = btn_y0 + btn_h

    return y


def _compose_centered(base, colors, copy, contact_footer, is_light_bg):
    """Original layout: text block centered in the lower ~60% of the image,
    full-width. Good for single-subject promotional/ad posts."""
    W, H = base.size
    footer_h = int(H * 0.055) if contact_footer else 0
    content_h = H - footer_h

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    overlay_top = int(content_h * 0.38)
    overlay_color = (255, 255, 255) if is_light_bg else (6, 16, 32)
    max_alpha = 165 if is_light_bg else 195
    for y in range(overlay_top, content_h):
        alpha = int(max_alpha * ((y - overlay_top) / (content_h - overlay_top)))
        odraw.line([(0, y), (W, y)], fill=(*overlay_color, alpha))
    if footer_h:
        footer_color = (255, 255, 255, 255) if is_light_bg else (6, 14, 28, 255)
        odraw.rectangle([0, content_h, W, H], fill=footer_color)
    base = Image.alpha_composite(base, overlay)

    draw = ImageDraw.Draw(base)
    margin = int(W * 0.10)
    x_left = margin
    x_right = W - margin
    y_start = int(content_h * 0.36)
    y_end = int(content_h * 0.96)

    _draw_text_block(draw, x_left, x_right, y_start, y_end, copy, colors, align="center")

    if contact_footer and footer_h:
        footer_font = _load_font(int(W * 0.020), bold=False)
        fbbox = draw.textbbox((0, 0), contact_footer, font=footer_font)
        fw = fbbox[2] - fbbox[0]
        fh = fbbox[3] - fbbox[1]
        footer_y = content_h + (footer_h - fh) / 2 - fbbox[1]
        draw.text((W / 2 - fw / 2, footer_y), contact_footer, font=footer_font, fill=colors["muted"])

    return base


def _compose_split(base, colors, copy, contact_footer, is_light_bg):
    """Greeting-card style layout: the LEFT half keeps the original
    background art mostly untouched (subtle darkening only), and the RIGHT
    half gets a solid color panel with the text block — similar to the
    reference Eid/greeting poster layout (art on one side, message on the
    other)."""
    W, H = base.size
    footer_h = int(H * 0.05) if contact_footer else 0
    content_h = H - footer_h

    panel_x = int(W * 0.52)  # right ~48% becomes the solid text panel
    panel_color = (16, 22, 32, 255) if not is_light_bg else (250, 250, 248, 255)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Subtle darken/lighten on the LEFT art half for any small text/logo
    # that might sit near the edge — kept light so the art stays visible.
    left_tint = (0, 0, 0, 40) if not is_light_bg else (255, 255, 255, 40)
    odraw.rectangle([0, 0, panel_x, content_h], fill=left_tint)

    # Solid panel on the right for the text block
    odraw.rectangle([panel_x, 0, W, H], fill=panel_color)

    base = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(base)

    panel_text_colors = dict(colors)
    if is_light_bg:
        panel_text_colors["text"] = "#13181F"
        panel_text_colors["muted"] = "#454F5C"
    # else keep the derived dark-bg colors (white text etc.) since the panel is dark

    margin = int((W - panel_x) * 0.14)
    x_left = panel_x + margin
    x_right = W - margin
    y_start = int(content_h * 0.10)
    y_end = int(content_h * 0.92)

    _draw_text_block(draw, x_left, x_right, y_start, y_end, copy, panel_text_colors, align="left")

    if contact_footer and footer_h:
        footer_font = _load_font(int(W * 0.018), bold=False)
        draw.rectangle([0, content_h, W, H],
                        fill=(panel_color[0], panel_color[1], panel_color[2], 255))
        draw.text((x_left, content_h + footer_h / 2 - footer_font.size / 2),
                   contact_footer, font=footer_font, fill=panel_text_colors["muted"])

    return base


def compose_poster(background_bytes: bytes, copy: dict, brand_colors: dict = None,
                    contact_footer: str = None, layout: str = "centered") -> bytes:
    """
    copy = {"headline": str, "sub_headline": str, "highlights": [str,...], "cta": str}

    layout:
      "centered" — full-width text block in the lower portion (default,
                   best for single-subject promotional/ad posts)
      "split"    — left side keeps the background art, right side becomes a
                   solid text panel (best for greeting/occasion posts —
                   Eid, New Year, company anniversary, etc.)

    Colors are NOT hardcoded. The actual background color (whatever the
    human requested via feedback) is sampled from the image and used to
    derive a matching, contrast-safe palette automatically.
    """
    base_for_detection = Image.open(BytesIO(background_bytes)).convert("RGB")
    W0, H0 = base_for_detection.size
    sample_box = (int(W0 * 0.15), int(H0 * 0.40), int(W0 * 0.85), int(H0 * 0.95))
    avg_rgb = _get_region_average_color(base_for_detection, sample_box)
    is_light_bg = _detect_is_light_background(avg_rgb)

    colors = brand_colors or _derive_palette_from_background(avg_rgb)
    base = Image.open(BytesIO(background_bytes)).convert("RGBA")

    if layout == "split":
        base = _compose_split(base, colors, copy, contact_footer, is_light_bg)
    else:
        base = _compose_centered(base, colors, copy, contact_footer, is_light_bg)

    out = BytesIO()
    base.convert("RGB").save(out, format="JPEG", quality=92)
    return out.getvalue()