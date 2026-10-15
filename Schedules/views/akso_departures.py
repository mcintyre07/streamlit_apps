from datetime import date, timedelta

import streamlit as st

import rota

# ======================================================================
# SETTINGS: paste the OSL2 / AKSO hex codes from Figma here.
# ======================================================================
LOCATION_COLORS = {
    "OSL2": "#9AD0C2",
    "AKSO": "#F2A68B",
}

# Start time of shift 1 to 8. DTL n works shift n.
SHIFT_TIMES = {
    "m": ["4:15", "4:30", "4:45", "5:00", "5:15", "5:30", "5:45", "6:00"],
    "e": ["12:45", "13:00", "13:15", "13:30", "13:45", "14:00", "14:15", "14:30"],
}
OSL2_SHIFTS = 4  # on weekdays the first 4 working shifts depart OSL2, the rest AKSO

# Days off for the two DTLs on weekend duty (0 = Monday ... 6 = Sunday).
OFF_BEFORE_WEEKEND = {"m": (3, 4), "e": (2, 3)}  # morning Thu+Fri, evening Wed+Thu
OFF_AFTER_WEEKEND = {"m": 2, "e": 1}             # following Wednesday / Tuesday


def departures(weekday, kind, pair_now, pair_prev):
    """Departure for shifts 1-8 on one day: 'OSL2', 'AKSO', or None if the shift is off."""
    if weekday >= 5:  # weekend: only the weekend pair works, everything leaves OSL2
        return {n: ("OSL2" if n in pair_now else None) for n in range(1, 9)}
    working = []
    for n in range(1, 9):
        off_before = n in pair_now and weekday in OFF_BEFORE_WEEKEND[kind]
        off_after = n in pair_prev and weekday == OFF_AFTER_WEEKEND[kind]
        if not (off_before or off_after):
            working.append(n)
    first = set(working[:OSL2_SHIFTS])  # the first 4 shifts that are working leave OSL2
    return {
        n: (None if n not in working else ("OSL2" if n in first else "AKSO"))
        for n in range(1, 9)
    }


def cell(location):
    if location is None:
        return '<td class="c off">Off</td>'
    color = LOCATION_COLORS[location]
    return f'<td class="c" style="background:{color};color:{rota.text_on(color)}">{location}</td>'


def table_html(kind, body):
    heads = ""
    for n in range(1, 9):
        heads += f"<th>DTL {n}<br>{SHIFT_TIMES[kind][n - 1]}</th>"
    return (
        '<table class="rot dep"><thead><tr><th>Week</th><th>Date</th>'
        + heads
        + "</tr></thead><tbody>"
        + body
        + "</tbody></table>"
    )


EXTRA_CSS = (
    "<style>"
    ".dep thead th{opacity:1;font-weight:600;line-height:1.25;padding:8px 4px}"
    ".dep td.c{font-size:13px;font-weight:600;padding:6px 2px;"
    "border-left:1px solid rgba(255,255,255,.7);border-right:1px solid rgba(255,255,255,.7)}"
    ".dep td.off{color:rgba(128,128,128,.75);font-weight:400}"
    ".dep td.dt{text-align:left;white-space:nowrap}"
    ".dep td.dt.we{font-weight:600;background:rgba(128,128,128,.12)}"
    ".dep td.dt.today{background:rgba(255,190,0,.3);font-weight:700}"
    ".dep tr.wkstart td{border-top:2px solid rgba(128,128,128,.6)}"
    ".loc{display:inline-block;padding:3px 12px;border-radius:6px;font-weight:600;margin-right:6px}"
    "</style>"
)

# ---------------------------------------------------------------- header
st.title("AKSO Departures")
st.caption(
    "Where each shift departs from. Weekdays: the first 4 shifts working that day leave from "
    "OSL2 and the remaining shifts leave from AKSO. Weekends: everything leaves from OSL2."
)

legend = "".join(
    f'<span class="loc" style="background:{c};color:{rota.text_on(c)}">{name}</span>'
    for name, c in LOCATION_COLORS.items()
)
st.markdown(EXTRA_CSS + legend + " Off = not working that day", unsafe_allow_html=True)

# ---------------------------------------------------------------- month filter
today = date.today()
this_monday = today - timedelta(days=today.weekday())
month_starts = [date(y, m, 1) for y in range(today.year, today.year + 3) for m in range(1, 13)]
labels = [d.strftime("%b %Y") for d in month_starts]
now_idx = today.month - 1

col_from, col_to = st.columns(2)
from_label = col_from.selectbox("From month", labels, index=now_idx)
to_label = col_to.selectbox("To month", labels, index=now_idx)

range_start = month_starts[labels.index(from_label)]
to_first = month_starts[labels.index(to_label)]
range_end = (to_first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

if to_first < range_start:
    st.warning("The 'To month' is before the 'From month'. Pick the same month or a later one.")
    st.stop()

# ---------------------------------------------------------------- build rows
rows = {"m": [], "e": []}
current_month = None
monday = range_start - timedelta(days=range_start.weekday() + 7)

while monday <= range_end:
    thursday = monday + timedelta(days=3)  # a week belongs to the month of its Thursday
    if range_start <= thursday <= range_end:
        month_label = thursday.strftime("%B %Y")
        if month_label != current_month:
            for kind in rows:
                rows[kind].append(f'<tr class="month"><td colspan="10">{month_label}</td></tr>')
            current_month = month_label

        turnus_now = rota.week_info(rota.template_week_for(monday))["turnus"]
        turnus_prev = rota.week_info(rota.template_week_for(monday - timedelta(days=7)))["turnus"]
        pair_now = rota.WEEKEND[turnus_now]    # DTLs working this weekend
        pair_prev = rota.WEEKEND[turnus_prev]  # DTLs who worked last weekend
        iso_week = monday.isocalendar()[1]

        for wd in range(7):
            day = monday + timedelta(days=wd)
            date_cls = "dt" + (" we" if wd >= 5 else "") + (" today" if day == today else "")
            label = f"{day.strftime('%a')} {day.day} {day.strftime('%b')}"
            wk_cell = f'<td class="wk" rowspan="7">{iso_week}</td>' if wd == 0 else ""
            for kind in rows:
                deps = departures(wd, kind, pair_now, pair_prev)
                cells = "".join(cell(deps[n]) for n in range(1, 9))
                rows[kind].append(
                    f'<tr class="{"wkstart" if wd == 0 else ""}">{wk_cell}'
                    f'<td class="{date_cls}">{label}</td>{cells}</tr>'
                )
    monday += timedelta(days=7)

# ---------------------------------------------------------------- tables
tab_m, tab_e = st.tabs(["Morning shifts", "Evening shifts"])
with tab_m:
    st.markdown(table_html("m", "".join(rows["m"])), unsafe_allow_html=True)
with tab_e:
    st.markdown(table_html("e", "".join(rows["e"])), unsafe_allow_html=True)

st.caption(
    "The two DTLs on weekend duty that week (see the template page) have days off around it. "
    "Morning: Thursday and Friday before the weekend, and the Wednesday after. "
    "Evening: Wednesday and Thursday before the weekend, and the Tuesday after."
)
st.caption(
    "Each week is listed under the month that contains its Thursday. "
    "A heavier line marks the start of a week."
)
