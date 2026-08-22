BG = "#0A0E14"
PRIMARY = "#5FD068"
SECONDARY = "#FF6B6B"
MUTED = "#7C8797"
WHITE = "#F2F5F8"
VIOLET = "#A78BFA"
FONT = "'SF Mono',Consolas,Monaco,monospace"

def fmt(n):
    if n is None:
        return "--"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

def col_divider(x, y0, y1):
    return f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{PRIMARY}" stroke-width="1" opacity="0.2"/>'

def stats_column(x0, y0, w, stats):
    out = [f'<text x="{x0}" y="{y0}" font-family="{FONT}" font-size="13" font-weight="700" fill="{PRIMARY}" letter-spacing="1">STATS</text>']
    row_y = y0 + 30
    for label, value in stats:
        out.append(f'<text x="{x0}" y="{row_y}" font-family="{FONT}" font-size="13" fill="{MUTED}">{label}</text>')
        out.append(f'<text x="{x0+w-14}" y="{row_y}" font-family="{FONT}" font-size="14" font-weight="700" fill="{WHITE}" text-anchor="end">{value}</text>')
        row_y += 26
    return '\n'.join(out)

def languages_column(x0, y0, w, langs):
    # langs: list of (name, pct, color) sorted desc, top 5
    out = [f'<text x="{x0}" y="{y0}" font-family="{FONT}" font-size="13" font-weight="700" fill="{PRIMARY}" letter-spacing="1">TOP LANGUAGES</text>']
    bar_y = y0 + 16
    bar_h = 8
    bx = x0
    for name, pct, color in langs:
        seg_w = max(2, w * (pct/100))
        out.append(f'<rect x="{bx:.1f}" y="{bar_y}" width="{seg_w:.1f}" height="{bar_h}" fill="{color}"/>')
        bx += seg_w
    row_y = y0 + 46
    for name, pct, color in langs:
        out.append(f'<circle cx="{x0+5}" cy="{row_y-4}" r="4" fill="{color}"/>')
        out.append(f'<text x="{x0+16}" y="{row_y}" font-family="{FONT}" font-size="12" fill="{WHITE}">{name}</text>')
        out.append(f'<text x="{x0+w-4}" y="{row_y}" font-family="{FONT}" font-size="12" fill="{MUTED}" text-anchor="end">{pct:.1f}%</text>')
        row_y += 22
    return '\n'.join(out)

def streak_column(x0, y0, w, current, longest, total, current_since, longest_range):
    out = [f'<text x="{x0}" y="{y0}" font-family="{FONT}" font-size="13" font-weight="700" fill="{PRIMARY}" letter-spacing="1">STREAK</text>']
    cx = x0 + w/2
    out.append(f'<text x="{cx:.1f}" y="{y0+48}" font-family="{FONT}" font-size="38" font-weight="700" fill="{PRIMARY}" text-anchor="middle">{current}</text>')
    out.append(f'<text x="{cx:.1f}" y="{y0+66}" font-family="{FONT}" font-size="11" fill="{MUTED}" text-anchor="middle">CURRENT STREAK</text>')
    if current_since:
        out.append(f'<text x="{cx:.1f}" y="{y0+80}" font-family="{FONT}" font-size="10" fill="{MUTED}" text-anchor="middle" opacity="0.7">since {current_since}</text>')

    row_y = y0 + 104
    out.append(f'<text x="{x0}" y="{row_y}" font-family="{FONT}" font-size="12" fill="{MUTED}">Longest</text>')
    out.append(f'<text x="{x0+w-4}" y="{row_y}" font-family="{FONT}" font-size="13" font-weight="700" fill="{WHITE}" text-anchor="end">{longest}d</text>')
    row_y += 22
    out.append(f'<text x="{x0}" y="{row_y}" font-family="{FONT}" font-size="12" fill="{MUTED}">Total (1y)</text>')
    out.append(f'<text x="{x0+w-4}" y="{row_y}" font-family="{FONT}" font-size="13" font-weight="700" fill="{WHITE}" text-anchor="end">{total}</text>')
    return '\n'.join(out)

def build(stats_data, langs, streak_data, canvas_w=1000, canvas_h=210):
    pad = 34
    col_w = (canvas_w - pad*2 - 60) / 3
    x1 = pad
    x2 = x1 + col_w + 30
    x3 = x2 + col_w + 30
    top = 34

    col1 = stats_column(x1, top, col_w, stats_data)
    col2 = languages_column(x2, top, col_w, langs)
    col3 = streak_column(x3, top, col_w, **streak_data)

    grid_lines = '\n'.join(
        f'<line x1="0" y1="{y}" x2="{canvas_w}" y2="{y}" stroke="{PRIMARY}" stroke-width="1" opacity="0.04"/>'
        for y in range(20, canvas_h, 26)
    )

    svg = f'''<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{canvas_w}" height="{canvas_h}" rx="6" fill="{BG}"/>
  {grid_lines}
  <rect x="1" y="1" width="{canvas_w-2}" height="{canvas_h-2}" rx="6" fill="none" stroke="{PRIMARY}" opacity="0.25"/>
  {col_divider(x2-15, 20, canvas_h-16)}
  {col_divider(x3-15, 20, canvas_h-16)}
  {col1}
  {col2}
  {col3}
</svg>'''
    return svg
