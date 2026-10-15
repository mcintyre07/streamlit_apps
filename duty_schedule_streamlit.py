import streamlit as st

st.set_page_config(page_title="Rotation schedule", layout="wide")

# ---------------------------------------------------------------- rotation data
DTL = [4, 2, 7, 5, 3, 1, 8, 6]                   # weekday evening DTL, 8-week cycle
WEEKEND = {1: (7, 8), 2: (5, 6), 3: (3, 4), 4: (1, 2)}  # DTLs by turnus week
MORNING_DOM = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3}  # DTL -> reporting DOM
EVENING_DOM = {1: 4, 2: 4, 3: 5, 4: 5, 5: 5, 6: 6, 7: 6, 8: 6}

# ======================================================================
# COLOURS: paste the hex codes from Figma here. Text switches between
# dark and white automatically so it stays readable on any colour.
# ======================================================================
DOM_COLORS = {
    1: "#874FFF",  # morning DOMs
    2: "#3DADFF",
    3: "#FF9E42",
    4: "#F849C1",  # evening DOMs
    5: "#66D575",
    6: "#FFC943",
}

# DTL numbers are the same for both shifts, but they are different people,
# so each shift has its own colour list.
DTL_MORNING_COLORS = {
    1: "#DCCCFF", 2: "#DCCCFF", 3: "#DCCCFF",  # report to DOM 1
    4: "#C2E5FF", 5: "#C2E5FF", 6: "#C2E5FF",  # report to DOM 2
    7: "#FCE5CD", 8: "#FCE5CD",                # report to DOM 3
}
DTL_EVENING_COLORS = {
    1: "#F4CCCC", 2: "#F4CCCC",                # report to DOM 4
    3: "#CDF4D3", 4: "#CDF4D3", 5: "#CDF4D3",  # report to DOM 5
    6: "#FFE0C2", 7: "#FFE0C2", 8: "#FFE0C2",  # report to DOM 6
}
WEEKS = 24  # lcm(4, 3, 8): the pattern repeats after this

# ---------------------------------------------------------------- page header
st.title("Work rotation schedule")
st.caption(
    "24-week cycle, then it repeats from week 1. Colours show who reports to which DOM."
)

choice = st.radio(
    "Highlight DOM team (DOM and the DTLs who report to them)",
    ["All"] + [f"DOM {i}" for i in range(1, 7)],
    horizontal=True,
)
selected = 0 if choice == "All" else int(choice.split()[1])

dtl_choice = st.radio(
    "Highlight a DTL",
    ["All"] + [f"DTL {i}" for i in range(1, 9)],
    horizontal=True,
)
selected_dtl = 0 if dtl_choice == "All" else int(dtl_choice.split()[1])

dtl_shift = "Both"
if selected_dtl:
    dtl_shift = st.radio("DTL shift", ["Both", "Morning", "Evening"], horizontal=True)

# ---------------------------------------------------------------- table builder
weeks_hit = set()


def text_on(hex_color):
    """Dark text on light colours, white text on dark ones."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#1D2433" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#FFFFFF"


def chip(number, color, team, week, kind="dom", shift="e"):
    by_dom = bool(selected) and team == selected
    by_dtl = (
        bool(selected_dtl)
        and kind == "dtl"
        and number == selected_dtl
        and dtl_shift in ("Both", "Morning" if shift == "m" else "Evening")
    )
    on = by_dom or by_dtl
    if on:
        weeks_hit.add(week)
    cls = "chip"
    if selected or selected_dtl:
        cls += " on" if on else " off"
    return (
        f'<span class="{cls}" style="background:{color};color:{text_on(color)}">'
        f"{number}</span>"
    )


rows = []
for w in range(1, WEEKS + 1):
    t = (w - 1) % 4 + 1          # turnus week
    morning = (w - 1) % 3 + 1    # morning DOM
    evening = morning + 3        # evening DOM
    dtl = DTL[(w - 1) % 8]
    a, b = WEEKEND[t]

    cls = ("alt " if ((w - 1) // 4) % 2 else "") + ("start" if t == 1 else "")
    rows.append(
        f'<tr class="{cls}">'
        f'<td class="wk">{w}</td><td class="tn">{t}</td>'
        f"<td>{chip(morning, DOM_COLORS[morning], morning, w)}</td>"
        f"<td>{chip(evening, DOM_COLORS[evening], evening, w)}</td>"
        f"<td>{chip(dtl, DTL_EVENING_COLORS[dtl], EVENING_DOM[dtl], w, 'dtl', 'e')}</td>"
        f'<td class="gap"></td>'
        f"<td>{chip(a, DTL_MORNING_COLORS[a], MORNING_DOM[a], w, 'dtl', 'm')}"
        f"{chip(b, DTL_MORNING_COLORS[b], MORNING_DOM[b], w, 'dtl', 'm')}</td>"
        f"<td>{chip(a, DTL_EVENING_COLORS[a], EVENING_DOM[a], w, 'dtl', 'e')}"
        f"{chip(b, DTL_EVENING_COLORS[b], EVENING_DOM[b], w, 'dtl', 'e')}</td>"
        "</tr>"
    )

css = (
    "<style>"
    ".rot{border-collapse:collapse;width:100%;font-size:15px}"
    ".rot th,.rot td{padding:8px 10px;text-align:center;border-bottom:1px solid rgba(128,128,128,.25)}"
    ".rot thead th{font-weight:600;opacity:.85}"
    ".rot td.wk{font-weight:600}"
    ".rot td.tn{opacity:.6}"
    ".rot th.gap,.rot td.gap{width:14px;padding:0;border-bottom:none}"
    ".rot tr.alt td:not(.gap){background:rgba(128,128,128,.09)}"
    ".rot tr.start td{border-top:2px solid rgba(128,128,128,.6)}"
    ".chip{display:inline-block;min-width:30px;padding:3px 0;border-radius:6px;font-weight:600}"
    ".chip+.chip{margin-left:4px}"
    ".chip.off{opacity:.12}"
    ".chip.on{outline:2px solid currentColor}"
    "</style>"
)

head = (
    '<table class="rot"><thead>'
    '<tr><th rowspan="2">Week</th><th rowspan="2">Turnus</th>'
    '<th colspan="2">DOM on duty</th><th>DTL on duty</th>'
    '<th class="gap" rowspan="2"></th><th colspan="2">Weekend DTLs</th></tr>'
    "<tr><th>Morning</th><th>Evening</th><th>Evening</th><th>Morning</th><th>Evening</th></tr>"
    "</thead><tbody>"
)

# Single-line HTML: indented or blank lines would be read as markdown code.
st.markdown(css + head + "".join(rows) + "</tbody></table>", unsafe_allow_html=True)

if selected or selected_dtl:
    st.caption(f"Highlighted shifts appear in {len(weeks_hit)} of {WEEKS} weeks.")

st.caption(
    "Morning team: DOM 1 (DTL 1–3), DOM 2 (DTL 4–6), DOM 3 (DTL 7–8). "
    "Evening team: DOM 4 (DTL 1–2), DOM 5 (DTL 3–5), DOM 6 (DTL 6–8). "
    "Turnus repeats every 4 weeks, DOM every 3, DTL every 8."
)