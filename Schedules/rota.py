"""Shared rotation data, colours and table helpers used by every page."""
from datetime import date, timedelta

import streamlit as st

# ======================================================================
# COLOURS: paste the hex codes from Figma here. Text switches between
# dark and white automatically so it stays readable on any colour.
# ======================================================================
DOM_COLORS = {
    1: "#B4A7D6",  # morning DOMs
    2: "#6FA8DC",
    3: "#F6B26B",
    4: "#E06666",  # evening DOMs
    5: "#93C47D",
    6: "#FFD966",
}

# DTL numbers are the same for both shifts, but they are different people,
# so each shift has its own colour list.
DTL_MORNING_COLORS = {
    1: "#D9D2E9", 2: "#D9D2E9", 3: "#D9D2E9",  # report to DOM 1
    4: "#A4C2F4", 5: "#A4C2F4", 6: "#A4C2F4",  # report to DOM 2
    7: "#FCE5CD", 8: "#FCE5CD",                # report to DOM 3
}
DTL_EVENING_COLORS = {
    1: "#F4CCCC", 2: "#F4CCCC",                # report to DOM 4
    3: "#CDF4D3", 4: "#CDF4D3", 5: "#CDF4D3",  # report to DOM 5
    6: "#FFF2CC", 7: "#FFF2CC", 8: "#FFF2CC",  # report to DOM 6
}

# ======================================================================
# ROTATION
# ======================================================================
DTL = [4, 2, 7, 5, 3, 1, 8, 6]                          # weekday evening DTL, 8-week cycle
WEEKEND = {1: (7, 8), 2: (5, 6), 3: (3, 4), 4: (1, 2)}  # weekend DTLs by turnus week
MORNING_DOM = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3}  # DTL -> reporting DOM
EVENING_DOM = {1: 4, 2: 4, 3: 5, 4: 5, 5: 5, 6: 6, 7: 6, 8: 6}
CYCLE_WEEKS = 24  # lcm(4, 3, 8): the whole pattern repeats after this

# ======================================================================
# CALENDAR ANCHOR: ties the 24-week template to real dates.
# ANCHOR_MONDAY is the Monday of ISO week 42, 2026 (turnus week 2).
# ANCHOR_TEMPLATE_WEEK is the row (1-24) of the template that week matches.
# Turnus 2 could be template week 2, 6, 10, 14, 18 or 22. Pick the one
# where the DOMs and DTL shown also match who is actually on duty now.
# ======================================================================
ANCHOR_MONDAY = date(2026, 10, 12)
ANCHOR_TEMPLATE_WEEK = 2
ANCHOR_TURNUS = 2

if ANCHOR_MONDAY.weekday() != 0:
    raise ValueError("ANCHOR_MONDAY must be a Monday.")
if (ANCHOR_TEMPLATE_WEEK - 1) % 4 + 1 != ANCHOR_TURNUS:
    raise ValueError(
        f"Template week {ANCHOR_TEMPLATE_WEEK} is not turnus week {ANCHOR_TURNUS}. "
        "Use 2, 6, 10, 14, 18 or 22."
    )


def week_info(template_week):
    """Who is on duty in a given template week (1-24)."""
    turnus = (template_week - 1) % 4 + 1
    morning = (template_week - 1) % 3 + 1
    return {
        "turnus": turnus,
        "morning": morning,
        "evening": morning + 3,
        "dtl": DTL[(template_week - 1) % 8],
        "weekend": WEEKEND[turnus],
    }


def template_week_for(monday):
    """Template week (1-24) for the week starting on this Monday."""
    weeks_since_anchor = (monday - ANCHOR_MONDAY).days // 7
    return (ANCHOR_TEMPLATE_WEEK - 1 + weeks_since_anchor) % CYCLE_WEEKS + 1


def date_range(monday):
    """'12–18 Oct' or '28 Sep – 4 Oct' for a Monday-to-Sunday week."""
    sunday = monday + timedelta(days=6)
    if monday.month == sunday.month:
        return f"{monday.day}–{sunday.day} {sunday.strftime('%b')}"
    return f"{monday.day} {monday.strftime('%b')} – {sunday.day} {sunday.strftime('%b')}"


# ======================================================================
# HIGHLIGHTING
# ======================================================================
def text_on(hex_color):
    """Dark text on light colours, white text on dark ones."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#1D2433" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#FFFFFF"


class Highlighter:
    """Holds the highlight choices and draws the coloured number chips."""

    def __init__(self, dom=0, dtl=0, shift="Both"):
        self.dom, self.dtl, self.shift = dom, dtl, shift
        self.hits = set()

    @property
    def active(self):
        return bool(self.dom or self.dtl)

    def chip(self, number, color, team, row_id, kind="dom", shift="e"):
        by_dom = bool(self.dom) and team == self.dom
        by_dtl = (
            bool(self.dtl)
            and kind == "dtl"
            and number == self.dtl
            and self.shift in ("Both", "Morning" if shift == "m" else "Evening")
        )
        on = by_dom or by_dtl
        if on:
            self.hits.add(row_id)
        cls = "chip"
        if self.active:
            cls += " on" if on else " off"
        return (
            f'<span class="{cls}" style="background:{color};color:{text_on(color)}">'
            f"{number}</span>"
        )


def button_css(prefix):
    """Colour each highlight button like its chip in the schedule.

    DOM buttons use DOM_COLORS. DTL buttons are split: morning colour on the
    left half, evening colour on the right half. Needs Streamlit 1.39+, which
    gives every keyed widget an `st-key-<key>` class to aim the CSS at.
    """
    def label_color(c1, c2=None):
        if c2 is None or c1 == c2:
            return c1, text_on(c1)
        same = text_on(c1) == text_on(c2)
        return f"linear-gradient(90deg,{c1} 50%,{c2} 50%)", text_on(c1) if same else "#1D2433"

    rules = [
        ".st-key-{k} [role=radiogroup]{{gap:6px 4px}}"
        ".st-key-{k} [role=radiogroup]>label{{padding:3px 10px;border-radius:8px;"
        "border:2px solid transparent;margin-right:0}}"
        ".st-key-{k} [role=radiogroup]>label:has(input:checked){{border-color:currentColor;"
        "font-weight:700}}"
        .format(k=f"{prefix}_dom"),
        ".st-key-{k} [role=radiogroup]>label{{padding:3px 10px;border-radius:8px;"
        "border:2px solid transparent;margin-right:0}}"
        ".st-key-{k} [role=radiogroup]>label:has(input:checked){{border-color:currentColor;"
        "font-weight:700}}"
        .format(k=f"{prefix}_dtl"),
    ]
    for i in range(1, 7):
        bg, fg = label_color(DOM_COLORS[i])
        rules.append(
            f".st-key-{prefix}_dom [role=radiogroup]>label:nth-child({i + 1})"
            f"{{background:{bg};color:{fg}!important}}"
            f".st-key-{prefix}_dom [role=radiogroup]>label:nth-child({i + 1}) *{{color:{fg}!important}}"
        )
    for i in range(1, 9):
        bg, fg = label_color(DTL_MORNING_COLORS[i], DTL_EVENING_COLORS[i])
        rules.append(
            f".st-key-{prefix}_dtl [role=radiogroup]>label:nth-child({i + 1})"
            f"{{background:{bg};color:{fg}!important}}"
            f".st-key-{prefix}_dtl [role=radiogroup]>label:nth-child({i + 1}) *{{color:{fg}!important}}"
        )
    return "<style>" + "".join(rules) + "</style>"


def highlight_controls(prefix):
    """Draw the DOM / DTL highlight buttons and return a Highlighter."""
    st.markdown(button_css(prefix), unsafe_allow_html=True)
    dom_choice = st.radio(
        "Highlight DOM team (DOM and the DTLs who report to them)",
        ["All"] + [f"DOM {i}" for i in range(1, 7)],
        horizontal=True,
        key=f"{prefix}_dom",
    )
    dtl_choice = st.radio(
        "Highlight a DTL",
        ["All"] + [f"DTL {i}" for i in range(1, 9)],
        horizontal=True,
        key=f"{prefix}_dtl",
    )
    shift = "Both"
    dtl = 0 if dtl_choice == "All" else int(dtl_choice.split()[1])
    if dtl:
        shift = st.radio(
            "DTL shift", ["Both", "Morning", "Evening"], horizontal=True, key=f"{prefix}_shift"
        )
    dom = 0 if dom_choice == "All" else int(dom_choice.split()[1])
    return Highlighter(dom, dtl, shift)


# ======================================================================
# TABLE HTML
# ======================================================================
CSS = (
    "<style>"
    ".rot{border-collapse:collapse;width:100%;font-size:15px}"
    ".rot th,.rot td{padding:8px 10px;text-align:center;border-bottom:1px solid rgba(128,128,128,.25)}"
    ".rot thead th{font-weight:600;opacity:.85}"
    ".rot td.wk{font-weight:600;white-space:nowrap}"
    ".rot td.tn{opacity:.6}"
    ".rot td.dt{white-space:nowrap;opacity:.85}"
    ".rot th.gap,.rot td.gap{width:14px;padding:0;border-bottom:none}"
    ".rot tr.alt td:not(.gap){background:rgba(128,128,128,.09)}"
    ".rot tr.start td{border-top:2px solid rgba(128,128,128,.6)}"
    ".rot tr.month td{text-align:left;font-weight:700;font-size:16px;padding:18px 10px 6px;"
    "border-bottom:2px solid rgba(128,128,128,.5)}"
    ".rot tr.now td:not(.gap){background:rgba(255,190,0,.16)}"
    ".rot tr.now td.wk{box-shadow:inset 4px 0 0 #E8A200}"
    ".badge{display:inline-block;margin-left:6px;padding:0 6px;border-radius:8px;"
    "font-size:11px;font-weight:600;background:#E8A200;color:#1D2433}"
    ".chip{display:inline-block;min-width:30px;padding:3px 0;border-radius:6px;font-weight:600}"
    ".chip+.chip{margin-left:4px}"
    ".chip.off{opacity:.12}"
    ".chip.on{outline:2px solid currentColor}"
    "</style>"
)

LEGEND = (
    "Morning team: DOM 1 (DTL 1–3), DOM 2 (DTL 4–6), DOM 3 (DTL 7–8). "
    "Evening team: DOM 4 (DTL 1–2), DOM 5 (DTL 3–5), DOM 6 (DTL 6–8). "
    "Turnus repeats every 4 weeks, DOM every 3, DTL every 8."
)


def row_cells(info, hl, row_id):
    """The six duty cells (DOM morning/evening, DTL, gap, weekend morning/evening)."""
    m, e, d = info["morning"], info["evening"], info["dtl"]
    a, b = info["weekend"]
    return (
        f"<td>{hl.chip(m, DOM_COLORS[m], m, row_id)}</td>"
        f"<td>{hl.chip(e, DOM_COLORS[e], e, row_id)}</td>"
        f"<td>{hl.chip(d, DTL_EVENING_COLORS[d], EVENING_DOM[d], row_id, 'dtl', 'e')}</td>"
        '<td class="gap"></td>'
        f"<td>{hl.chip(a, DTL_MORNING_COLORS[a], MORNING_DOM[a], row_id, 'dtl', 'm')}"
        f"{hl.chip(b, DTL_MORNING_COLORS[b], MORNING_DOM[b], row_id, 'dtl', 'm')}</td>"
        f"<td>{hl.chip(a, DTL_EVENING_COLORS[a], EVENING_DOM[a], row_id, 'dtl', 'e')}"
        f"{hl.chip(b, DTL_EVENING_COLORS[b], EVENING_DOM[b], row_id, 'dtl', 'e')}</td>"
    )


def month_row(label, lead_columns):
    return f'<tr class="month"><td colspan="{lead_columns + 6}">{label}</td></tr>'


def table_html(lead_headers, body):
    """Full table. lead_headers are the left-hand columns, e.g. ['Week', 'Turnus']."""
    lead = "".join(f'<th rowspan="2">{h}</th>' for h in lead_headers)
    head = (
        '<table class="rot"><thead><tr>' + lead +
        '<th colspan="2">DOM on duty</th><th>DTL on duty</th>'
        '<th class="gap" rowspan="2"></th><th colspan="2">Weekend DTLs</th></tr>'
        "<tr><th>Morning</th><th>Evening</th><th>Evening</th><th>Morning</th><th>Evening</th></tr>"
        "</thead><tbody>"
    )
    # Single-line HTML: indented or blank lines would be read as markdown code.
    return CSS + head + body + "</tbody></table>"
