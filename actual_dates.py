from datetime import date, timedelta

import streamlit as st

import rota

st.title("Rotation by date")
st.caption(
    "Real weeks and dates, worked out from the 24-week template. "
    "Weeks run Monday to Sunday."
)

today = date.today()
this_monday = today - timedelta(days=today.weekday())

# ---------------------------------------------------------------- month filter
month_starts = [
    date(y, m, 1) for y in range(today.year, today.year + 3) for m in range(1, 13)
]
labels = [d.strftime("%b %Y") for d in month_starts]
now_idx = today.month - 1                       # current month in the list
end_idx = min(now_idx + 2, len(labels) - 1)     # default view: three months

col_from, col_to = st.columns(2)
from_label = col_from.selectbox("From month", labels, index=now_idx)
to_label = col_to.selectbox("To month", labels, index=end_idx)

range_start = month_starts[labels.index(from_label)]
to_first = month_starts[labels.index(to_label)]
range_end = (to_first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

if to_first < range_start:
    st.warning("The 'To month' is before the 'From month'. Pick the same month or a later one.")
    st.stop()

hl = rota.highlight_controls("dates")

# ---------------------------------------------------------------- build rows
rows = []
shown = 0
current_month = None
monday = range_start - timedelta(days=range_start.weekday() + 7)

while monday <= range_end:
    thursday = monday + timedelta(days=3)  # a week belongs to the month of its Thursday
    if range_start <= thursday <= range_end:
        month_label = thursday.strftime("%B %Y")
        if month_label != current_month:
            rows.append(rota.month_row(month_label, 3))
            current_month = month_label

        info = rota.week_info(rota.template_week_for(monday))
        is_now = monday == this_monday
        cls = ("start " if info["turnus"] == 1 else "") + ("now" if is_now else "")
        week_no = monday.isocalendar()[1]
        badge = ' <span class="badge">Now</span>' if is_now else ""
        rows.append(
            f'<tr class="{cls.strip()}">'
            f'<td class="wk">{week_no}{badge}</td>'
            f'<td class="dt">{rota.date_range(monday)}</td>'
            f'<td class="tn">{info["turnus"]}</td>'
            f"{rota.row_cells(info, hl, monday)}"
            "</tr>"
        )
        shown += 1
    monday += timedelta(days=7)

st.markdown(rota.table_html(["Week", "Dates", "Turnus"], "".join(rows)), unsafe_allow_html=True)

if hl.active:
    st.caption(f"Highlighted shifts appear in {len(hl.hits)} of the {shown} weeks shown.")
st.caption(
    "Each week is listed under the month that contains its Thursday, so no week appears twice. "
    "A heavier line marks the start of a new 4-week turnus."
)
st.caption(rota.LEGEND)
