import pandas as pd
import plotly.express as px
import streamlit as st

import queries


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="UK Skills Radar",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
    /* Main page */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    /* Typography */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1.2px;
    }

    h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.4px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 18px 20px;
        border-radius: 14px;
        min-height: 115px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        font-weight: 750;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.15);
    }

    /* Dividers */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        opacity: 0.25;
    }

    /* Buttons */
    .stDownloadButton button {
        border-radius: 8px;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Footer */
    .dashboard-footer {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 0.85rem;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("📊 UK Skills Radar")
    st.markdown(
        "Explore the skills shaping the **UK data and machine learning "
        "job market**."
    )

with header_right:
    st.write("")
    st.write("")
    st.caption("🇬🇧 UNITED KINGDOM")
    st.caption("LIVE JOB MARKET INTELLIGENCE")

st.divider()


# =========================================================
# DATA AVAILABILITY
# =========================================================

totals = queries.get_totals()

if totals["postings"] == 0 or totals["links"] == 0:
    st.warning(
        "No skill data is available yet. "
        "Run `ingest.py` and then `nlp_extract.py` first."
    )
    st.stop()


# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.markdown("## 🎛️ Dashboard controls")
st.sidebar.caption("Customise your skills analysis.")

skills_to_show = st.sidebar.slider(
    "Skills to display",
    min_value=5,
    max_value=30,
    value=10,
    step=5,
)

skill_names = queries.all_skill_names()

if not skill_names:
    st.info("No skills have been extracted yet.")
    st.stop()

chosen_skill = st.sidebar.selectbox(
    "Skill trend",
    skill_names,
)

st.sidebar.divider()

st.sidebar.markdown("### About this dashboard")
st.sidebar.caption(
    "Tracks skills mentioned in UK data and machine learning "
    "job postings using NLP."
)

st.sidebar.caption("Source: Adzuna API")


# =========================================================
# LOAD SKILL DATA
# =========================================================

top_skills = queries.trending_skills(skills_to_show)

if not top_skills:
    st.warning("No skill rankings are available.")
    st.stop()

best_skill = top_skills[0]


# =========================================================
# KPI CARDS
# =========================================================

st.markdown("### Market at a glance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📄 Postings analysed",
        value=f'{totals["postings"]:,}',
        help="Number of job postings recorded in the dataset.",
    )

with col2:
    st.metric(
        label="🔗 Skill matches",
        value=f'{totals["links"]:,}',
        help="Number of posting-to-skill matches found.",
    )

with col3:
    st.metric(
        label="🧠 Distinct skills",
        value=f'{totals["skills"]:,}',
        help="Number of distinct skills in the dataset.",
    )

with col4:
    st.metric(
        label="🏆 Top skill",
        value=best_skill["skill"],
        help="The skill appearing in the largest share of postings.",
    )

    st.caption(
        f'{best_skill["share_pct"]}% of analysed postings'
    )


# =========================================================
# SKILLS CHART
# =========================================================

st.divider()

st.markdown("### 📈 Skills intelligence")
st.caption(
    "Explore the most frequently requested skills and how demand changes."
)

left, right = st.columns([1.15, 1], gap="large")


# ---------------------------------------------------------
# LEFT: MOST IN-DEMAND SKILLS
# ---------------------------------------------------------

with left:
    st.subheader("Most in-demand skills")
    st.caption("Percentage of analysed postings mentioning each skill.")

    skills_table = pd.DataFrame(top_skills)

    if not skills_table.empty:
        skills_table["share_pct"] = pd.to_numeric(
            skills_table["share_pct"],
            errors="coerce",
        )

        skills_table = skills_table.dropna(
            subset=["skill", "share_pct"]
        )

        skills_table = skills_table.sort_values(
            "share_pct",
            ascending=True,
        )

        bar_chart = px.bar(
            skills_table,
            x="share_pct",
            y="skill",
            orientation="h",
            text="share_pct",
            labels={
                "share_pct": "Share of postings (%)",
                "skill": "",
            },
            color_discrete_sequence=["#0B6E78"],
            hover_data={
                "share_pct": ":.1f",
            },
        )

        bar_chart.update_traces(
            texttemplate="%{x:.1f}%",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Share of postings: %{x:.1f}%"
                "<extra></extra>"
            ),
        )

        bar_chart.update_layout(
            template="plotly_white",
            height=max(380, len(skills_table) * 35),
            margin=dict(l=10, r=45, t=20, b=45),
            xaxis=dict(
                title="Share of postings (%)",
                rangemode="tozero",
                showgrid=True,
                gridcolor="#E8EEEE",
                zeroline=False,
            ),
            yaxis=dict(
                title="",
                autorange="reversed",
            ),
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="#263B3E",
            ),
            showlegend=False,
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    else:
        st.info("No skill ranking data is available.")


# ---------------------------------------------------------
# RIGHT: SKILL TREND
# ---------------------------------------------------------

with right:
    st.subheader(f"Trend: {chosen_skill}")
    st.caption(
        "Daily share of postings mentioning the selected skill."
    )

    trend_data = queries.skill_trend(chosen_skill)

    if trend_data:
        trend_table = pd.DataFrame(trend_data)

        if {"day", "share_pct"}.issubset(trend_table.columns):
            trend_table["day"] = pd.to_datetime(
                trend_table["day"],
                errors="coerce",
            )

            trend_table["share_pct"] = pd.to_numeric(
                trend_table["share_pct"],
                errors="coerce",
            )

            trend_table = (
                trend_table
                .dropna(subset=["day", "share_pct"])
                .sort_values("day")
            )

            if not trend_table.empty:
                line_chart = px.line(
                    trend_table,
                    x="day",
                    y="share_pct",
                    markers=True,
                    labels={
                        "day": "Date",
                        "share_pct": "Share of postings (%)",
                    },
                    color_discrete_sequence=["#0B6E78"],
                )

                line_chart.update_traces(
                    line=dict(width=3),
                    marker=dict(size=6),
                    hovertemplate=(
                        "Date: %{x|%d %b %Y}<br>"
                        "Share: %{y:.1f}%"
                        "<extra></extra>"
                    ),
                )

                line_chart.update_layout(
                    template="plotly_white",
                    height=420,
                    margin=dict(l=10, r=20, t=20, b=45),
                    hovermode="x unified",
                    xaxis=dict(
                        title="",
                        showgrid=False,
                    ),
                    yaxis=dict(
                        title="Share of postings (%)",
                        rangemode="tozero",
                        gridcolor="#E8EEEE",
                    ),
                    font=dict(
                        family="Arial, sans-serif",
                        size=12,
                        color="#263B3E",
                    ),
                    showlegend=False,
                )

                st.plotly_chart(
                    line_chart,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

                st.caption(
                    "Daily values may fluctuate when posting volumes are low."
                )

            else:
                st.info("No valid trend data is available yet.")

        else:
            st.info("Trend data is missing the expected columns.")

    else:
        st.info("Not enough historical data for this skill yet.")


# =========================================================
# LATEST JOB POSTINGS
# =========================================================

st.divider()

st.markdown("### 💼 Latest job postings")
st.caption(
    "Browse recent vacancies and the skills detected in their descriptions."
)

latest = queries.latest_postings(100)

if latest:
    # Prepare the display data without changing the original records.
    prepared_postings = []

    for posting in latest:
        row = posting.copy()

        # Handle missing or empty skills.
        skills = row.get("skills") or []

        if isinstance(skills, str):
            row["skills"] = skills if skills.strip() else "No skills detected"
        else:
            row["skills"] = (
                ", ".join(str(skill) for skill in skills)
                if skills
                else "No skills detected"
            )

        # Format dates safely.
        raw_date = row.get("date_posted")

        parsed_date = pd.to_datetime(
            raw_date,
            errors="coerce",
            utc=True,
        )

        row["date_posted"] = (
            parsed_date.strftime("%d %b %Y")
            if pd.notna(parsed_date)
            else "Unknown"
        )

        prepared_postings.append(row)

    postings_table = pd.DataFrame(prepared_postings)

    expected_columns = [
        "title",
        "company",
        "location",
        "skills",
        "date_posted",
        "url",
    ]

    # Ensure the expected display columns exist.
    for column in expected_columns:
        if column not in postings_table.columns:
            postings_table[column] = ""

    postings_table = postings_table[expected_columns].copy()

    # Search across title, company, location and skills.
    search = st.text_input(
        "🔎 Search postings",
        placeholder="Search job titles, companies, locations or skills...",
    )

    if search.strip():
        searchable_columns = [
            "title",
            "company",
            "location",
            "skills",
        ]

        mask = postings_table[searchable_columns].apply(
            lambda column: column.astype(str).str.contains(
                search.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        displayed_postings = postings_table[mask].copy()

    else:
        displayed_postings = postings_table.copy()

    st.caption(
        f"Showing {len(displayed_postings):,} of "
        f"{len(postings_table):,} postings."
    )

    # CSV export.
    csv_data = displayed_postings.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download postings as CSV",
        data=csv_data,
        file_name="uk_skills_radar_postings.csv",
        mime="text/csv",
    )

    st.write("")

    st.dataframe(
        displayed_postings,
        hide_index=True,
        use_container_width=True,
        height=520,
        column_config={
            "title": st.column_config.TextColumn(
                "Job title",
                width="medium",
            ),
            "company": st.column_config.TextColumn(
                "Company",
                width="medium",
            ),
            "location": st.column_config.TextColumn(
                "Location",
                width="small",
            ),
            "skills": st.column_config.TextColumn(
                "Detected skills",
                width="large",
            ),
            "date_posted": st.column_config.TextColumn(
                "Date posted",
                width="small",
            ),
            "url": st.column_config.LinkColumn(
                "Job listing",
                display_text="↗ Open job",
                width="small",
            ),
        },
    )

else:
    st.info("No job postings are available yet.")


# =========================================================
# METHODOLOGY AND FOOTER
# =========================================================

st.divider()

with st.expander("ℹ️ About the data and methodology"):
    st.markdown(
        """
        **Data source:** Adzuna job postings.

        **Skill extraction:** spaCy PhraseMatcher matches job-description
        text against a predefined vocabulary of skills.

        **Demand calculation:** Skill share represents the percentage
        of analysed postings that mention a particular skill, provided
        that the underlying query uses distinct postings as its denominator.

        **Data limitation:** Adzuna may return only a snippet of a full
        job description. Skills mentioned outside that snippet may not
        be detected.

        **Interpretation:** Posting counts and skill shares describe
        the collected dataset. They should not be treated as a complete
        census of the UK labour market.
        """
    )

st.markdown(
    """
    <div class="dashboard-footer">
        <p>
            Built by <b>Prabhjot Singh Virdi</b>
            · Data engineering · NLP · Market intelligence
        </p>
        <p>
            Source code:
            <a href="https://github.com/prabhjot-5/UK_SKILLS_RADAR"
               target="_blank">
                GitHub — UK Skills Radar
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)