import random

BG = "#0A0E14"
STRIP_BG = "#05070A"
PRIMARY = "#5FD068"
SECONDARY = "#FF6B6B"
MUTED = "#7C8797"
WHITE = "#F2F5F8"
VIOLET = "#A78BFA"

def char_w(size, ratio=0.6):
    return size * ratio

def text_width(s, size, ratio=0.6):
    return len(s) * char_w(size, ratio)

def up_triangle(cx, cy, s, color, opacity=1):
    return (f'<polygon points="{cx},{cy-s} {cx-s*0.9:.1f},{cy+s*0.7:.1f} {cx+s*0.9:.1f},{cy+s*0.7:.1f}" '
            f'fill="{color}" opacity="{opacity}"/>')

def down_triangle(cx, cy, s, color, opacity=1):
    return (f'<polygon points="{cx},{cy+s} {cx-s*0.9:.1f},{cy-s*0.7:.1f} {cx+s*0.9:.1f},{cy-s*0.7:.1f}" '
            f'fill="{color}" opacity="{opacity}"/>')

def dot(cx, cy, r, color, opacity=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{opacity}"/>'

def bg_candles(canvas_w, y_base, n, seed=3):
    random.seed(seed)
    out = []
    step = canvas_w / n
    for i in range(n):
        x = i*step + step*0.25
        w = step*0.4
        body_h = random.uniform(8, 26)
        wick_h = body_h + random.uniform(4, 12)
        up = random.random() > 0.4
        color = PRIMARY if up else SECONDARY
        cx = x + w/2
        out.append(f'<line x1="{cx:.1f}" y1="{y_base-wick_h:.1f}" x2="{cx:.1f}" y2="{y_base:.1f}" stroke="{color}" stroke-width="1"/>')
        out.append(f'<rect x="{x:.1f}" y="{y_base-body_h:.1f}" width="{w:.1f}" height="{body_h:.1f}" fill="{color}"/>')
    return '\n'.join(out)

def sparkline(x0, y0, w, h, closes, color):
    if not closes or len(closes) < 2:
        return ''
    lo, hi = min(closes), max(closes)
    rng = (hi - lo) or 1
    coords = []
    for i, p in enumerate(closes):
        x = x0 + (i/(len(closes)-1))*w
        y = y0 + h - ((p-lo)/rng)*h
        coords.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(coords)
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'

def render_tape_group(entries, size, y_baseline, sep, x_offset):
    out = []
    x = x_offset
    for i, (sym, is_up, desc) in enumerate(entries):
        out.append(f'<text x="{x:.1f}" y="{y_baseline}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="{size}" font-weight="700" fill="{WHITE}">{sym}</text>')
        x += text_width(sym, size) + 8
        marker_color = PRIMARY if is_up else VIOLET
        if is_up:
            out.append(up_triangle(x, y_baseline-5, 5, marker_color))
        else:
            out.append(dot(x, y_baseline-5, 4, marker_color))
        x += 16
        out.append(f'<text x="{x:.1f}" y="{y_baseline}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="{size}" fill="{MUTED}">{desc}</text>')
        x += text_width(desc, size)
        if i != len(entries)-1:
            out.append(f'<text x="{x:.1f}" y="{y_baseline}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="{size}" fill="{MUTED}" opacity="0.5">{sep}</text>')
            x += text_width(sep, size)
    return '\n'.join(out), x - x_offset

def watchlist_panel(stocks, x0=628, y0=14, w=340, h=150):
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="4" fill="none" stroke="{PRIMARY}" opacity="0.35"/>']
    out.append(f'<text x="{x0+14}" y="{y0+22}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="12" font-weight="700" fill="{MUTED}" letter-spacing="1">WATCHLIST</text>')

    row_y = y0 + 46
    row_h = 26
    for s in stocks:
        sym = s["symbol"]
        price = s["price"]
        pct = s["pct"]
        up = pct >= 0
        color = PRIMARY if up else SECONDARY
        price_str = f"${price:,.2f}" if price is not None else "--"
        pct_str = f"{pct:+.2f}%" if pct is not None else "--"
        out.append(f'<text x="{x0+14}" y="{row_y}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="14" font-weight="700" fill="{WHITE}">{sym}</text>')
        out.append(f'<text x="{x0+92}" y="{row_y}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="13" fill="{MUTED}">{price_str}</text>')
        marker_cx = x0 + 208
        if up:
            out.append(up_triangle(marker_cx, row_y-5, 5, color))
        else:
            out.append(down_triangle(marker_cx, row_y-5, 5, color))
        out.append(f'<text x="{x0+222}" y="{row_y}" font-family="\'SF Mono\',Consolas,Monaco,monospace" font-size="13" font-weight="700" fill="{color}">{pct_str}</text>')
        hist = s.get("history") or []
        if hist:
            out.append(sparkline(x0+w-92, row_y-16, 78, 18, hist, color))
        row_y += row_h
    return '\n'.join(out)


def build(stocks, canvas_w=1000, canvas_h=260):
    name = "KANISHKA SARKAR"
    name_size = 46
    name_x = 42
    name_y = 92

    subtitle = "SOFTWARE ENGINEER  .  QUANT + AI SYSTEMS  .  SYDNEY, AU"
    sub_size = 16
    sub_x = 44
    sub_y = 132
    sub_w = text_width(subtitle, sub_size, 0.58)
    cursor_full_x = sub_x + sub_w + 8

    grid_lines = '\n'.join(
        f'<line x1="0" y1="{y}" x2="{canvas_w}" y2="{y}" stroke="{PRIMARY}" stroke-width="1" opacity="0.05"/>'
        for y in range(30, 175, 24)
    )
    bgc = bg_candles(canvas_w, 168, 34, seed=9)

    panel = watchlist_panel(stocks)

    entries = [
        ("CARDINAL", True, "EQUITY ANALYSIS TERMINAL"),
        ("STRATUM", True, "MOMENTUM ENGINE"),
        ("OPE", False, "OPTIONS PRICING"),
        ("CATTLESCANNER", True, "YOLO11 / CV"),
        ("USYD", False, "SWE (HONS) 2026"),
    ]
    size = 15
    y_baseline = 233
    sep = "      |      "
    _, one_w = render_tape_group(entries, size, y_baseline, sep, 0)
    tape1, _ = render_tape_group(entries, size, y_baseline, sep, 0)
    tape2, _ = render_tape_group(entries, size, y_baseline, sep, one_w + text_width(sep, size))
    total_w = one_w + text_width(sep, size)
    dur = max(16, total_w / 45)

    # typing animation timeline
    cyc = 8.0
    kt = "0;0.375;0.6875;0.875;1"
    width_vals = f"0;{sub_w:.1f};{sub_w:.1f};0;0"
    cursor_vals = f"{sub_x};{cursor_full_x:.1f};{cursor_full_x:.1f};{sub_x};{sub_x}"

    svg = f'''<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3"/>
    </filter>
    <clipPath id="typeClip">
      <rect x="{sub_x}" y="{sub_y-15}" width="0" height="20">
        <animate attributeName="width" values="{width_vals}" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/>
      </rect>
    </clipPath>
  </defs>

  <rect width="{canvas_w}" height="{canvas_h}" fill="{BG}"/>
  {grid_lines}
  <g opacity="0.10">{bgc}</g>

  {panel}

  <text x="{name_x}" y="{name_y}" font-family="'SF Mono',Consolas,Monaco,monospace" font-size="{name_size}" font-weight="700" fill="{PRIMARY}" filter="url(#softGlow)" opacity="0.5">{name}</text>
  <text x="{name_x}" y="{name_y}" font-family="'SF Mono',Consolas,Monaco,monospace" font-size="{name_size}" font-weight="700" fill="{WHITE}">
    {name}
    <animate attributeName="opacity" values="1;0.92;1" dur="4s" repeatCount="indefinite"/>
  </text>

  <g clip-path="url(#typeClip)">
    <text x="{sub_x}" y="{sub_y}" font-family="'SF Mono',Consolas,Monaco,monospace" font-size="{sub_size}" fill="{MUTED}">{subtitle}</text>
  </g>
  <rect y="{sub_y-14}" width="9" height="17" fill="{PRIMARY}">
    <animate attributeName="x" values="{cursor_vals}" keyTimes="{kt}" dur="{cyc}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>

  <line x1="0" y1="172" x2="{canvas_w}" y2="172" stroke="{PRIMARY}" stroke-width="1" opacity="0.25"/>

  <rect x="0" y="190" width="{canvas_w}" height="70" fill="{STRIP_BG}"/>
  <line x1="0" y1="190" x2="{canvas_w}" y2="190" stroke="{PRIMARY}" stroke-width="1.5" opacity="0.5"/>

  <g transform="translate(20,0)">
    <animateTransform attributeName="transform" type="translate" values="20,0;{-(total_w)+20:.1f},0" dur="{dur:.1f}s" repeatCount="indefinite"/>
{tape1}
{tape2}
  </g>
</svg>'''
    return svg
