import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Single-chart color: blue for all arrests, red for juvenile-only
COLOR_ALL = "#4a9eff"
COLOR_JUVENILE_ONLY = "#e85d4a"
# Exception charts (race + trend): both groups, juvenile highlighted
COLOR_ADULT_MUTED = "#7eb8ff"
COLOR_JUVENILE_HIGHLIGHT = "#e85d4a"

DATA_PATH = Path(__file__).parent.parent / "data" / "arrests_clean.csv"
if not DATA_PATH.exists():
    DATA_PATH = Path(__file__).parent / "arrests_clean.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    # Ensure is_juvenile is boolean
    if "is_juvenile" in df.columns:
        df["is_juvenile"] = df["is_juvenile"].map(
            lambda x: x is True or (isinstance(x, str) and x.strip().upper() == "TRUE")
        )
    if "school_hours" in df.columns:
        df["school_hours"] = df["school_hours"].map(
            lambda x: x is True or (isinstance(x, str) and x.strip().upper() == "TRUE")
        ).fillna(False)
    # Ensure year is numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def main():
    df_raw = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")

    show_juvenile_only = st.sidebar.toggle("Juvenile Only", value=False)

    year_options = ["All Years"] + sorted(df_raw["year"].dropna().unique().astype(int).tolist())
    selected_year = st.sidebar.selectbox("Year", options=year_options, index=0)
    if selected_year == 2025:
        st.sidebar.warning("2025 data is partial — January through March only.")

    district_options = ["All Districts"] + sorted([
        d for d in df_raw["district_name"].dropna().unique()
        if str(d).strip() != "Unknown"
    ])
    selected_district = st.sidebar.selectbox("District", options=district_options, index=0)

    # Apply filters
    df = df_raw.copy()
    if selected_year != "All Years":
        df = df[df["year"] == int(selected_year)]
    if selected_district != "All Districts":
        df = df[df["district_name"] == selected_district]
    if show_juvenile_only:
        filtered_df = df[df["is_juvenile"] == True].copy()
    else:
        filtered_df = df.copy()

    total_count = len(filtered_df)
    juvenile_count = int(filtered_df["is_juvenile"].sum()) if "is_juvenile" in filtered_df.columns else 0
    pct_juvenile = (100.0 * juvenile_count / total_count) if total_count else 0
    _juv_districts = filtered_df[filtered_df["is_juvenile"] == True]["district_name"]
    _juv_districts_known = _juv_districts[_juv_districts.notna() & (_juv_districts.astype(str).str.strip() != "Unknown")]
    most_affected = (
        _juv_districts_known.value_counts().index[0]
        if len(_juv_districts_known) and "district_name" in filtered_df.columns
        else "—"
    )

    title_suffix = "— Juvenile Only" if show_juvenile_only else "— All Arrests"
    chart_color = COLOR_JUVENILE_ONLY if show_juvenile_only else COLOR_ALL

    # --- MAIN PAGE ---
    st.title("Boston Youth Arrests Analysis")
    st.caption("Source: Boston Police Index, 2020–2025")
    st.divider()

    # Section 1 — Overview metrics
    st.subheader("Overview")
    m1, m2, m3, m4 = st.columns(4)
    if show_juvenile_only:
        black_pct = (
            filtered_df[filtered_df["race_desc"] == "BLACK OR AFRICAN AMERICAN"].shape[0]
            / total_count * 100
        ) if total_count else 0
        sh = filtered_df["school_hours"]
        school_pct = (sh == True).mean() * 100 if len(sh) else 0
        with m1:
            st.metric("Juvenile Arrests", f"{total_count:,}")
        with m2:
            st.metric("Most Affected District", str(most_affected))
        with m3:
            st.metric("Black Arrestees", f"{black_pct:.1f}%")
        with m4:
            st.metric("During School Hours", f"{school_pct:.1f}%")
    else:
        with m1:
            st.metric("Total Arrests", f"{total_count:,}")
        with m2:
            st.metric("Juvenile Arrests", f"{juvenile_count:,}")
        with m3:
            st.metric("% Juvenile", f"{pct_juvenile:.1f}%")
        with m4:
            st.metric("Most Affected District", str(most_affected))
    if not show_juvenile_only:
        st.caption("Race and trend charts below always show Juvenile vs Adult for comparison.")
    st.divider()

    # Section 2 — Arrests by District (single color)
    st.subheader("Where: Arrests by District")
    df_dist = filtered_df[filtered_df["district_name"].notna()].copy()
    dist_counts = df_dist.groupby("district_name", dropna=False).size().reset_index(name="count")
    if not dist_counts.empty:
        dist_counts["pct_of_total"] = (dist_counts["count"] / dist_counts["count"].sum() * 100).round(1)
        fig_dist = px.bar(
            dist_counts,
            x="count",
            y="district_name",
            orientation="h",
            custom_data=["pct_of_total"],
            color_discrete_sequence=[chart_color],
            title=f"Arrests by District {title_suffix}",
        )
        fig_dist.update_traces(
            hovertemplate="<b>%{y}</b><br>Arrests: %{x:,}<br>% of total: %{customdata[0]:.1f}%<extra></extra>"
        )
        fig_dist.update_layout(yaxis={"categoryorder": "total ascending"}, height=400, showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No district data for current filters.")

    dist_all = df[df["district_name"].notna() & (df["district_name"] != "Unknown")].groupby("district_name").size().reset_index(name="total")
    dist_juv = df[(df["is_juvenile"] == True) & (df["district_name"].notna()) & (df["district_name"] != "Unknown")].groupby("district_name").size().reset_index(name="juvenile")
    dist_compare = dist_all.merge(dist_juv, on="district_name", how="left").fillna(0)
    dist_compare["juv_pct"] = (dist_compare["juvenile"] / dist_compare["total"] * 100).round(1)
    dist_compare = dist_compare.sort_values("juv_pct", ascending=False)

    fig_disp = px.bar(
        dist_compare,
        x="district_name",
        y="juv_pct",
        title="Juvenile % of All Arrests by District",
        labels={"juv_pct": "% Juvenile", "district_name": "District"},
        color="juv_pct",
        color_continuous_scale="Reds",
    )
    fig_disp.update_layout(xaxis_tickangle=-45, height=350, showlegend=False)
    fig_disp.update_traces(
        hovertemplate="<b>%{x}</b><br>Juvenile: %{y:.1f}%<extra></extra>"
    )
    st.plotly_chart(fig_disp, use_container_width=True)
    st.caption("Which districts arrest the most youth relative to their total arrest volume.")
    st.divider()

    # Section 3 — Demographics (3 columns)
    st.subheader("Who: Demographics")
    juv_total_demo = len(filtered_df[filtered_df["is_juvenile"] == True])
    black_juv = len(filtered_df[
        (filtered_df["is_juvenile"] == True) &
        (filtered_df["race_desc"] == "BLACK OR AFRICAN AMERICAN")
    ])
    black_pct_demo = (black_juv / juv_total_demo * 100) if juv_total_demo else 0

    st.markdown(f"""
<div style='background:rgba(232,93,74,0.08); border-left:3px solid #e85d4a;
padding:12px 16px; border-radius:4px; margin-bottom:16px'>
<span style='font-size:28px; font-weight:bold; color:#e85d4a'>{black_pct_demo:.1f}%</span>
<span style='color:#aaa; margin-left:10px'>of juvenile arrestees are Black —
in a city that is ~25% Black (3.1× disparity)</span>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        # Exception: always show both juvenile and adult, highlight juvenile
        race_counts = filtered_df.groupby(["race_desc", "is_juvenile"]).size().reset_index(name="count")
        race_counts["juvenile_label"] = race_counts["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
        if not race_counts.empty:
            fig_race = px.bar(
                race_counts,
                x="count",
                y="race_desc",
                color="juvenile_label",
                orientation="h",
                color_discrete_map={"Adult": COLOR_ADULT_MUTED, "Juvenile": COLOR_JUVENILE_HIGHLIGHT},
                title="Race breakdown — Juvenile vs Adult",
            )
            fig_race.update_layout(yaxis={"categoryorder": "total ascending"}, height=300)
            for d in fig_race.data:
                if d.name == "Juvenile":
                    d.marker.update(line=dict(width=2, color="#333"))
                else:
                    d.opacity = 0.75
            st.plotly_chart(fig_race, use_container_width=True)
        else:
            st.write("No data")

    with c2:
        df_juv = filtered_df[(filtered_df["is_juvenile"] == True) & (filtered_df["age"].between(10, 18))]
        if not df_juv.empty and df_juv["age"].notna().any():
            fig_age = px.histogram(
                df_juv,
                x="age",
                nbins=9,
                title=f"Age Distribution of Juvenile Arrests {title_suffix}",
                color_discrete_sequence=[chart_color],
            )
            fig_age.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.write("No juvenile age data (10–18)")

    with c3:
        gender_counts = filtered_df.groupby("gender_desc", dropna=False).size().reset_index(name="count")
        if not gender_counts.empty:
            fig_gender = px.pie(
                gender_counts,
                values="count",
                names="gender_desc",
                title=f"Gender breakdown {title_suffix}",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_gender.update_layout(height=300)
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 4 — Time patterns
    st.subheader("When: Time Patterns")
    t1, t2 = st.columns(2)

    with t1:
        if show_juvenile_only:
            year_counts = filtered_df.groupby("year", dropna=False).size().reset_index(name="count")
            if not year_counts.empty:
                fig_year = px.line(
                    year_counts,
                    x="year",
                    y="count",
                    title="Arrest Trend Over Time — Juvenile Only",
                )
                fig_year.update_traces(line_color=chart_color, line_width=3)
                fig_year.update_layout(height=350, showlegend=False)
                max_2025 = year_counts[year_counts["year"] == 2025]["count"].max() if 2025 in year_counts["year"].values else None
                if max_2025 is not None:
                    fig_year.add_annotation(
                        x=2025,
                        y=max_2025,
                        text="Partial year<br>(Jan–Mar only)",
                        showarrow=True,
                        arrowhead=2,
                        font=dict(size=10, color="#aaa"),
                        ax=40, ay=-30
                    )
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.write("No data")
        else:
            # Show both juvenile and adult, highlight juvenile
            year_counts = df.groupby(["year", "is_juvenile"]).size().reset_index(name="count")
            year_counts["juvenile_label"] = year_counts["is_juvenile"].map(lambda x: "Juvenile" if x else "Adult")
            if not year_counts.empty:
                fig_year = px.line(
                    year_counts,
                    x="year",
                    y="count",
                    color="juvenile_label",
                    color_discrete_map={"Adult": COLOR_ADULT_MUTED, "Juvenile": COLOR_JUVENILE_HIGHLIGHT},
                    title="Arrest Trend Over Time — Juvenile vs Adult",
                )
                fig_year.update_layout(height=350)
                for i, d in enumerate(fig_year.data):
                    if d.name == "Juvenile":
                        d.line = dict(width=4)
                    else:
                        d.line = dict(width=2, dash="dot")
                max_2025 = year_counts[year_counts["year"] == 2025]["count"].max() if 2025 in year_counts["year"].values else None
                if max_2025 is not None:
                    fig_year.add_annotation(
                        x=2025,
                        y=max_2025,
                        text="Partial year<br>(Jan–Mar only)",
                        showarrow=True,
                        arrowhead=2,
                        font=dict(size=10, color="#aaa"),
                        ax=40, ay=-30
                    )
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.write("No data")

    with t2:
        time_order = ["Morning", "Afternoon", "Evening", "Night"]
        df_time = filtered_df[filtered_df["time_of_day"].notna()].copy()
        time_counts = df_time.groupby("time_of_day", dropna=False).size().reset_index(name="count")
        time_counts["time_of_day"] = pd.Categorical(time_counts["time_of_day"], categories=time_order, ordered=True)
        time_counts = time_counts.sort_values("time_of_day")
        if not time_counts.empty:
            fig_time = px.bar(
                time_counts,
                x="time_of_day",
                y="count",
                color_discrete_sequence=[chart_color],
                title=f"Arrests by Time of Day {title_suffix}",
            )
            fig_time.update_layout(height=350, xaxis={"categoryorder": "array", "categoryarray": time_order}, showlegend=False)
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 5 — Charge types
    st.subheader("What: Charge Types")
    s1, s2 = st.columns(2)

    with s1:
        sev_df = df[df["charge_severity"].notna()].copy()
        sev_df["label"] = sev_df["is_juvenile"].map({True: "Juvenile", False: "Adult"})
        sev_counts = sev_df.groupby(["charge_severity", "label"]).size().reset_index(name="count")
        sev_counts["total"] = sev_counts.groupby("label")["count"].transform("sum")
        sev_counts["pct"] = (sev_counts["count"] / sev_counts["total"] * 100).round(1)

        fig_sev = px.bar(
            sev_counts,
            x="label",
            y="pct",
            color="charge_severity",
            barmode="stack",
            title="Charge Severity — Juvenile vs Adult",
            labels={"pct": "% of arrests", "label": ""},
            color_discrete_map={
                "Serious": "#e85d4a",
                "Minor/Status": "#f5a623",
                "Other": "#4a9eff"
            }
        )
        fig_sev.update_layout(height=350)
        st.plotly_chart(fig_sev, use_container_width=True)

    with s2:
        top_charges = filtered_df["charge_desc"].value_counts().head(10).reset_index()
        top_charges.columns = ["charge_desc", "count"]
        if not top_charges.empty:
            fig_charge = px.bar(
                top_charges,
                x="count",
                y="charge_desc",
                orientation="h",
                title=f"Top 10 Charges {title_suffix}",
                color_discrete_sequence=[chart_color],
            )
            fig_charge.update_layout(yaxis={"categoryorder": "total ascending"}, height=350, showlegend=False)
            st.plotly_chart(fig_charge, use_container_width=True)
        else:
            st.write("No data")
    st.divider()

    # Section 6 — School hours
    st.subheader("School Hours")
    df_juv_only = filtered_df[filtered_df["is_juvenile"] == True]
    juv_total = len(df_juv_only)
    juv_school = int(df_juv_only["school_hours"].sum()) if juv_total > 0 else 0
    pct_school = (100.0 * juv_school / juv_total) if juv_total else 0
    st.metric(
        "Juvenile arrests during school hours (Mon–Fri 8am–3pm)",
        f"{pct_school:.1f}%",
    )

    df_juv_dist = df_juv_only[df_juv_only["district_name"].notna() & (df_juv_only["district_name"].astype(str).str.strip() != "Unknown")].copy()
    if not df_juv_dist.empty and "school_hours" in df_juv_dist.columns:
        df_juv_dist["school_hours_bool"] = df_juv_dist["school_hours"]
        rate_by_dist = (
            df_juv_dist.groupby("district_name")["school_hours_bool"]
            .agg(["sum", "count"])
            .assign(rate=lambda x: 100.0 * x["sum"] / x["count"])
            .sort_values("rate", ascending=False)
            .reset_index()
        )
        fig_school = px.bar(
            rate_by_dist,
            x="district_name",
            y="rate",
            title=f"School Hours Arrest Rate by District {title_suffix}",
            labels={"rate": "% during school hours", "district_name": "District"},
            color_discrete_sequence=[chart_color],
        )
        fig_school.update_layout(xaxis_tickangle=-45, height=350)
        st.plotly_chart(fig_school, use_container_width=True)

    st.markdown("**Are school hours arrests more serious?**")
    juv_school_sev = df_juv_only[df_juv_only["charge_severity"].notna()].copy()
    juv_school_sev["label"] = juv_school_sev["school_hours"].map(
        {True: "School Hours", False: "Outside School Hours"}
    )
    school_sev = juv_school_sev.groupby(["label", "charge_severity"]).size().reset_index(name="count")
    school_sev["total"] = school_sev.groupby("label")["count"].transform("sum")
    school_sev["pct"] = (school_sev["count"] / school_sev["total"] * 100).round(1)

    fig_school_sev = px.bar(
        school_sev,
        x="label",
        y="pct",
        color="charge_severity",
        barmode="stack",
        title="Charge Severity — School Hours vs Outside School Hours (Juvenile Only)",
        labels={"pct": "% of arrests", "label": ""},
        color_discrete_map={
            "Serious": "#e85d4a",
            "Minor/Status": "#f5a623",
            "Other": "#4a9eff"
        }
    )
    fig_school_sev.update_layout(height=300)
    st.plotly_chart(fig_school_sev, use_container_width=True)
    st.caption("School hours defined as Monday–Friday, 8am–3pm.")
    st.divider()

    st.caption(
        "Note: 9.4% of arrests have no district recorded and are excluded from district-level charts. "
        "Missing district data has increased from 263 records in 2020 to 2,637 in 2024."
    )


if __name__ == "__main__":
    main()
