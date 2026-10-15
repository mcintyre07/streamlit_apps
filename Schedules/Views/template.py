import streamlit as st

import Schedules.rota as rota

st.title("Work rotation schedule")
st.caption("24-week cycle, then it repeats from week 1. Colours show who reports to which DOM.")

hl = rota.highlight_controls("template")

rows = []
for w in range(1, rota.CYCLE_WEEKS + 1):
    info = rota.week_info(w)
    cls = ("alt " if ((w - 1) // 4) % 2 else "") + ("start" if info["turnus"] == 1 else "")
    rows.append(
        f'<tr class="{cls.strip()}">'
        f'<td class="wk">{w}</td><td class="tn">{info["turnus"]}</td>'
        f"{rota.row_cells(info, hl, w)}"
        "</tr>"
    )

st.markdown(rota.table_html(["Week", "Turnus"], "".join(rows)), unsafe_allow_html=True)

if hl.active:
    st.caption(f"Highlighted shifts appear in {len(hl.hits)} of {rota.CYCLE_WEEKS} weeks.")
st.caption(rota.LEGEND)
