import streamlit as st
import pandas as pd
import altair as alt


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NBA Player Value Analytics",
    page_icon="🏀",
    layout="wide"
)


# =========================================================
# MODEL SETTINGS
# =========================================================

ALPHA = 0.30
MINIMUM_PLAYER_SCORE = 60


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    leaderboard = pd.read_csv(
        "nba_value_leaderboard.csv"
    )

    master = pd.read_csv(
        "nba_value_master_database.csv"
    )

    # Make salary numeric
    master["Salary"] = pd.to_numeric(
        master["Salary"],
        errors="coerce"
    )

    # Salary per scheduled NBA game
    master["Salary_Per_Game"] = (
        master["Salary"] / 82
    )

    # Salary per game in $100K units
    master["Salary_Per_Game_100K"] = (
        master["Salary_Per_Game"] / 100000
    )

    # Final contract value formula
    master["Final_Value_Score"] = (
        master["Overall_Player_Score"]
        /
        (
            master["Salary_Per_Game_100K"]
            ** ALPHA
        )
    )

    return leaderboard, master


leaderboard_df, master_df = load_data()


# =========================================================
# PLAYER PERCENTILES
# =========================================================

master_df["Performance_Percentile"] = (
    master_df["Overall_Player_Score"]
    .rank(
        pct=True,
        method="average"
    )
    * 100
)


master_df["OVS_Percentile"] = (
    master_df["OVS"]
    .rank(
        pct=True,
        method="average"
    )
    * 100
)


master_df["DVS_Percentile"] = (
    master_df["DVS"]
    .rank(
        pct=True,
        method="average"
    )
    * 100
)


master_df["AVS_Percentile"] = (
    master_df["AVS"]
    .rank(
        pct=True,
        method="average"
    )
    * 100
)


master_df["Salary_Percentile"] = (
    master_df["Salary"]
    .rank(
        pct=True,
        method="average"
    )
    * 100
)


master_df["Contract_Efficiency_Gap"] = (
    master_df["Performance_Percentile"]
    -
    master_df["Salary_Percentile"]
)


# =========================================================
# HOMEPAGE / HERO
# =========================================================

st.title(
    "🏀 NBA Player Value Analytics"
)

st.markdown(
    "### Who is actually worth what they're being paid?"
)

st.write(
    """
    NBA Player Value Analytics is an independent sports analytics
    project that measures player performance against contract cost.

    The model combines **offense, defense, availability, efficiency,
    and salary** to answer a question that traditional NBA rankings
    don't:

    **Which players provide the most basketball value for the money?**
    """
)

st.divider()


# =========================================================
# HEADLINE METRICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Players Analyzed",
        f"{len(master_df):,}"
    )


with col2:

    qualified_count = master_df[
        master_df["Overall_Player_Score"]
        >= MINIMUM_PLAYER_SCORE
    ].shape[0]

    st.metric(
        "Qualified Contracts",
        f"{qualified_count:,}"
    )


with col3:

    qualified_players = master_df[
        master_df["Overall_Player_Score"]
        >= MINIMUM_PLAYER_SCORE
    ]

    best_value_player = (
        qualified_players
        .sort_values(
            "Final_Value_Score",
            ascending=False
        )
        .iloc[0]["Player"]
    )

    st.metric(
        "#1 Contract Value",
        best_value_player
    )


with col4:

    best_player_row = master_df.loc[
        master_df[
            "Overall_Player_Score"
        ].idxmax()
    ]

    st.metric(
        "#1 Overall Player",
        best_player_row["Player"]
    )


st.divider()


# =========================================================
# HOW THE MODEL WORKS
# =========================================================

st.subheader(
    "How the Model Works"
)

st.write(
    """
    Player statistics are transformed into three performance scores,
    combined into an Overall Player Score, and then compared against
    salary to measure contract value.
    """
)


step1, step2, step3, step4, step5 = st.columns(5)


with step1:

    st.markdown("### 📊")
    st.markdown("**NBA Statistics**")
    st.caption("2025–26 performance data")


with step2:

    st.markdown("### →")
    st.markdown("**OVS · DVS · AVS**")
    st.caption("Offense, defense & availability")


with step3:

    st.markdown("### →")
    st.markdown("**Player Score**")
    st.caption(
        "36% offense · 34% defense · 30% availability"
    )


with step4:

    st.markdown("### →")
    st.markdown("**Salary Adjustment**")
    st.caption("2026–27 contract cost")


with step5:

    st.markdown("### 🏆")
    st.markdown("**Contract Value**")
    st.caption("Performance relative to cost")


st.divider()


# =========================================================
# NAVIGATION
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "💰 Value Leaderboard",
        "⭐ Player Rankings",
        "🔎 Player Explorer",
        "⚔️ Compare Players",
        "🏢 Front Office Efficiency",
        "🧠 Methodology"
    ]
)


# =========================================================
# TAB 1 — VALUE LEADERBOARD
# =========================================================

with tab1:

    st.header(
        "NBA Contract Value Leaderboard"
    )

    st.write(
        """
        This leaderboard ranks players based on how much basketball
        performance they provide relative to their 2026–27 salary.

        Players must have an **Overall Player Score of at least 60**
        to qualify for the main Value Leaderboard.
        """
    )


    # -----------------------------------------------------
    # METRIC KEY
    # -----------------------------------------------------

    with st.expander(
        "📖 Metric Key"
    ):

        st.markdown(
            """
            **OVS — Offensive Value Score**  
            Measures offensive production and efficiency.

            **DVS — Defensive Value Score**  
            Measures defensive production and impact.

            **AVS — Availability Value Score**  
            Measures availability, playing time, and efficiency.

            **Overall Player Score**  
            Combines OVS, DVS, and AVS into one performance rating.

            **Final Value Score**  
            Measures player performance relative to contract cost.
            """
        )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search_value = st.text_input(
        "Search for a player",
        placeholder="Example: Stephen Curry",
        key="value_search"
    )


    value_display = leaderboard_df.copy()


    if search_value:

        value_display = value_display[
            value_display["Player"]
            .str.contains(
                search_value,
                case=False,
                na=False
            )
        ]


    st.dataframe(
        value_display,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # SALARY VS PERFORMANCE QUADRANT
    # =====================================================

    st.divider()

    st.subheader(
        "Salary vs. Player Performance"
    )

    st.write(
        """
        This chart compares each player's overall performance
        with his annual salary.

        The white dashed lines represent the **median salary**
        and **median Overall Player Score** in the dataset.

        Hover over any point to identify the player and view his
        salary, Overall Player Score, and Contract Value Score.
        """
    )


    chart_df = master_df[
        [
            "Player",
            "Salary",
            "Overall_Player_Score",
            "Final_Value_Score"
        ]
    ].dropna().copy()


    median_salary = chart_df[
        "Salary"
    ].median()

    median_player_score = chart_df[
        "Overall_Player_Score"
    ].median()

    max_salary = chart_df[
        "Salary"
    ].max()

    min_salary = chart_df[
        "Salary"
    ].min()

    max_score = chart_df[
        "Overall_Player_Score"
    ].max()

    min_score = chart_df[
        "Overall_Player_Score"
    ].min()


    # -----------------------------------------------------
    # PLAYER DOTS
    # -----------------------------------------------------

    points = (
        alt.Chart(chart_df)
        .mark_circle(
            size=90,
            opacity=0.75
        )
        .encode(

            x=alt.X(
                "Salary:Q",
                title="Annual Salary",
                axis=alt.Axis(
                    format="$,.0f"
                )
            ),

            y=alt.Y(
                "Overall_Player_Score:Q",
                title="Overall Player Score"
            ),

            tooltip=[
                alt.Tooltip(
                    "Player:N",
                    title="Player"
                ),

                alt.Tooltip(
                    "Salary:Q",
                    title="Annual Salary",
                    format="$,.0f"
                ),

                alt.Tooltip(
                    "Overall_Player_Score:Q",
                    title="Overall Player Score",
                    format=".2f"
                ),

                alt.Tooltip(
                    "Final_Value_Score:Q",
                    title="Contract Value Score",
                    format=".2f"
                )
            ]
        )
    )


    # -----------------------------------------------------
    # MEDIAN SALARY LINE
    # -----------------------------------------------------

    salary_line = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Median Salary": [
                        median_salary
                    ]
                }
            )
        )
        .mark_rule(
            strokeDash=[7, 7],
            strokeWidth=2.5,
            color="white",
            opacity=0.9
        )
        .encode(
            x="Median Salary:Q"
        )
    )


    # -----------------------------------------------------
    # MEDIAN SCORE LINE
    # -----------------------------------------------------

    score_line = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Median Score": [
                        median_player_score
                    ]
                }
            )
        )
        .mark_rule(
            strokeDash=[7, 7],
            strokeWidth=2.5,
            color="white",
            opacity=0.9
        )
        .encode(
            y="Median Score:Q"
        )
    )


    # -----------------------------------------------------
    # QUADRANT LABEL LOCATIONS
    # -----------------------------------------------------

    left_x = (
        min_salary
        +
        (
            median_salary
            - min_salary
        )
        * 0.35
    )


    right_x = (
        median_salary
        +
        (
            max_salary
            - median_salary
        )
        * 0.50
    )


    top_y = (
        median_player_score
        +
        (
            max_score
            - median_player_score
        )
        * 0.75
    )


    bottom_y = (
        min_score
        +
        (
            median_player_score
            - min_score
        )
        * 0.25
    )


    quadrant_labels = pd.DataFrame(
        {
            "Salary": [
                left_x,
                right_x,
                left_x,
                right_x
            ],

            "Score": [
                top_y,
                top_y,
                bottom_y,
                bottom_y
            ],

            "Label": [
                "HIGH VALUE",
                "EXPENSIVE STARS",
                "LOW-COST ROLE PLAYERS",
                "POOR CONTRACT VALUE"
            ]
        }
    )


    labels = (
        alt.Chart(
            quadrant_labels
        )
        .mark_text(
            fontSize=13,
            fontWeight="normal",
            color="white",
            opacity=0.70
        )
        .encode(
            x="Salary:Q",
            y="Score:Q",
            text="Label:N"
        )
    )


    value_quadrant_chart = (
        points
        + salary_line
        + score_line
        + labels
    ).properties(
        height=525
    ).interactive()


    st.altair_chart(
        value_quadrant_chart,
        use_container_width=True
    )


    st.caption(
        f"Median Annual Salary: "
        f"${median_salary:,.0f}   |   "
        f"Median Overall Player Score: "
        f"{median_player_score:.2f}"
    )


    # =====================================================
    # TOP 10 CONTRACT VALUES
    # =====================================================

    st.divider()

    st.subheader(
        "Top 10 Contract Values"
    )

    st.write(
        """
        The ten highest-ranked qualifying contracts according
        to the NBA Player Value model.
        """
    )


    top_10 = (
        master_df[
            master_df["Overall_Player_Score"]
            >= MINIMUM_PLAYER_SCORE
        ]
        .sort_values(
            "Final_Value_Score",
            ascending=False
        )
        .head(10)
        .copy()
    )


    top_10_chart = (
        alt.Chart(
            top_10
        )
        .mark_bar()
        .encode(

            x=alt.X(
                "Final_Value_Score:Q",
                title="Contract Value Score"
            ),

            y=alt.Y(
                "Player:N",
                title=None,
                sort="-x"
            ),

            tooltip=[
                alt.Tooltip(
                    "Player:N",
                    title="Player"
                ),

                alt.Tooltip(
                    "Final_Value_Score:Q",
                    title="Value Score",
                    format=".2f"
                ),

                alt.Tooltip(
                    "Overall_Player_Score:Q",
                    title="Player Score",
                    format=".2f"
                ),

                alt.Tooltip(
                    "Salary:Q",
                    title="Annual Salary",
                    format="$,.0f"
                )
            ]
        )
        .properties(
            height=400
        )
    )


    st.altair_chart(
        top_10_chart,
        use_container_width=True
    )


    # =====================================================
    # CONTRACT EFFICIENCY ANALYSIS
    # =====================================================

    st.divider()

    st.header(
        "Contract Efficiency Analysis"
    )

    st.write(
        """
        **Elite Bargains** identifies players performing in the
        top 20% of the NBA according to the model and then determines
        which provide the greatest contract value.

        **Least Efficient Contracts** identifies highly paid players
        whose performance falls below the league median.
        """
    )


    elite_bargains = (
        master_df[
            master_df[
                "Performance_Percentile"
            ]
            >= 80
        ]
        .sort_values(
            "Final_Value_Score",
            ascending=False
        )
        .head(10)
        .copy()
    )


    least_efficient = (
        master_df[
            (
                master_df[
                    "Salary_Percentile"
                ]
                >= 80
            )
            &
            (
                master_df[
                    "Performance_Percentile"
                ]
                < 50
            )
        ]
        .sort_values(
            "Contract_Efficiency_Gap",
            ascending=True
        )
        .head(10)
        .copy()
    )


    bargain_col, inefficient_col = (
        st.columns(2)
    )


    # -----------------------------------------------------
    # ELITE BARGAINS
    # -----------------------------------------------------

    with bargain_col:

        st.subheader(
            "💎 Elite Bargains"
        )

        st.caption(
            "Top-20% performers ranked by Contract Value Score"
        )


        bargain_chart = (
            alt.Chart(
                elite_bargains
            )
            .mark_bar()
            .encode(

                x=alt.X(
                    "Final_Value_Score:Q",
                    title="Value Score"
                ),

                y=alt.Y(
                    "Player:N",
                    title=None,
                    sort="-x"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Player:N",
                        title="Player"
                    ),

                    alt.Tooltip(
                        "Performance_Percentile:Q",
                        title="Performance Percentile",
                        format=".1f"
                    ),

                    alt.Tooltip(
                        "Salary_Percentile:Q",
                        title="Salary Percentile",
                        format=".1f"
                    ),

                    alt.Tooltip(
                        "Overall_Player_Score:Q",
                        title="Overall Player Score",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Salary:Q",
                        title="Annual Salary",
                        format="$,.0f"
                    ),

                    alt.Tooltip(
                        "Final_Value_Score:Q",
                        title="Value Score",
                        format=".2f"
                    )
                ]
            )
            .properties(
                height=400
            )
        )


        st.altair_chart(
            bargain_chart,
            use_container_width=True
        )


    # -----------------------------------------------------
    # LEAST EFFICIENT CONTRACTS
    # -----------------------------------------------------

    with inefficient_col:

        st.subheader(
            "💸 Least Efficient Contracts"
        )

        st.caption(
            "Top-20% salaries with below-median performance"
        )


        if len(
            least_efficient
        ) > 0:

            inefficient_chart = (
                alt.Chart(
                    least_efficient
                )
                .mark_bar()
                .encode(

                    x=alt.X(
                        "Contract_Efficiency_Gap:Q",
                        title=(
                            "Performance − Salary "
                            "Percentile Gap"
                        )
                    ),

                    y=alt.Y(
                        "Player:N",
                        title=None,
                        sort="x"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Player:N",
                            title="Player"
                        ),

                        alt.Tooltip(
                            "Salary:Q",
                            title="Annual Salary",
                            format="$,.0f"
                        ),

                        alt.Tooltip(
                            "Salary_Percentile:Q",
                            title="Salary Percentile",
                            format=".1f"
                        ),

                        alt.Tooltip(
                            "Performance_Percentile:Q",
                            title="Performance Percentile",
                            format=".1f"
                        ),

                        alt.Tooltip(
                            "Overall_Player_Score:Q",
                            title="Overall Player Score",
                            format=".2f"
                        ),

                        alt.Tooltip(
                            "Contract_Efficiency_Gap:Q",
                            title="Efficiency Gap",
                            format="+.1f"
                        )
                    ]
                )
                .properties(
                    height=400
                )
            )


            st.altair_chart(
                inefficient_chart,
                use_container_width=True
            )


    with st.expander(
        "How are these groups defined?"
    ):

        st.markdown(
            """
            **💎 Elite Bargains**

            - Overall Player Score must rank in the
              **80th percentile or higher**.
            - Players are then ranked by Final Value Score.

            **💸 Least Efficient Contracts**

            - Salary must rank in the **80th percentile or higher**.
            - Performance must rank **below the 50th percentile**.
            - Players are ranked by the gap between performance
              percentile and salary percentile.
            """
        )


# =========================================================
# TAB 2 — PLAYER RANKINGS
# =========================================================

with tab2:

    st.header(
        "Overall Player Rankings"
    )

    st.write(
        """
        This ranking ignores salary entirely.

        **How strong was the player's overall basketball performance?**
        """
    )


    performance_df = master_df[
        [
            "Player",
            "OVS",
            "DVS",
            "AVS",
            "Overall_Player_Score"
        ]
    ].copy()


    performance_df = (
        performance_df
        .sort_values(
            "Overall_Player_Score",
            ascending=False
        )
    )


    performance_df[
        "Player_Rank"
    ] = range(
        1,
        len(performance_df) + 1
    )


    performance_df = performance_df[
        [
            "Player_Rank",
            "Player",
            "OVS",
            "DVS",
            "AVS",
            "Overall_Player_Score"
        ]
    ]


    for column in [
        "OVS",
        "DVS",
        "AVS",
        "Overall_Player_Score"
    ]:

        performance_df[
            column
        ] = (
            performance_df[
                column
            ].round(2)
        )


    performance_search = (
        st.text_input(
            "Search player rankings",
            placeholder="Example: Nikola Jokic",
            key="performance_search"
        )
    )


    if performance_search:

        performance_df = (
            performance_df[
                performance_df[
                    "Player"
                ]
                .str.contains(
                    performance_search,
                    case=False,
                    na=False
                )
            ]
        )


    st.dataframe(
        performance_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 3 — PLAYER EXPLORER
# =========================================================

with tab3:

    st.header(
        "Player Explorer"
    )

    st.write(
        """
        Select any player in the database to explore his offensive,
        defensive, availability, overall performance, salary, and
        contract value.
        """
    )


    player_list = sorted(
        master_df["Player"]
        .dropna()
        .unique()
    )


    selected_player = st.selectbox(
        "Select a player",
        player_list,
        key="player_explorer_select"
    )


    player_data = master_df[
        master_df["Player"]
        == selected_player
    ].iloc[0]


    overall_rank = (
        master_df[
            "Overall_Player_Score"
        ]
        .rank(
            ascending=False,
            method="min"
        )
        .loc[
            player_data.name
        ]
    )


    ovs_rank = (
        master_df["OVS"]
        .rank(
            ascending=False,
            method="min"
        )
        .loc[
            player_data.name
        ]
    )


    dvs_rank = (
        master_df["DVS"]
        .rank(
            ascending=False,
            method="min"
        )
        .loc[
            player_data.name
        ]
    )


    avs_rank = (
        master_df["AVS"]
        .rank(
            ascending=False,
            method="min"
        )
        .loc[
            player_data.name
        ]
    )


    st.subheader(
        selected_player
    )

    st.caption(
        f"Overall Performance Rank: "
        f"#{int(overall_rank)} of {len(master_df)}"
    )


    score1, score2, score3, score4 = (
        st.columns(4)
    )


    with score1:

        st.metric(
            "OVS",
            f"{player_data['OVS']:.2f}"
        )

        st.caption(
            f"{player_data['OVS_Percentile']:.1f}th percentile "
            f"• Rank #{int(ovs_rank)}"
        )


    with score2:

        st.metric(
            "DVS",
            f"{player_data['DVS']:.2f}"
        )

        st.caption(
            f"{player_data['DVS_Percentile']:.1f}th percentile "
            f"• Rank #{int(dvs_rank)}"
        )


    with score3:

        st.metric(
            "AVS",
            f"{player_data['AVS']:.2f}"
        )

        st.caption(
            f"{player_data['AVS_Percentile']:.1f}th percentile "
            f"• Rank #{int(avs_rank)}"
        )


    with score4:

        st.metric(
            "Overall Player Score",
            f"{player_data['Overall_Player_Score']:.2f}"
        )

        st.caption(
            f"{player_data['Performance_Percentile']:.1f}th percentile "
            f"• Rank #{int(overall_rank)}"
        )


    st.divider()

    st.subheader(
        "Contract"
    )


    contract1, contract2, contract3 = (
        st.columns(3)
    )


    with contract1:

        st.metric(
            "Annual Salary",
            f"${player_data['Salary']:,.0f}"
        )

        st.caption(
            f"{player_data['Salary_Percentile']:.1f}th "
            "salary percentile"
        )


    with contract2:

        st.metric(
            "Salary Per Game",
            f"${player_data['Salary_Per_Game']:,.0f}"
        )


    with contract3:

        if (
            player_data[
                "Overall_Player_Score"
            ]
            >= MINIMUM_PLAYER_SCORE
        ):

            st.metric(
                "Final Value Score",
                f"{player_data['Final_Value_Score']:.2f}"
            )

        else:

            st.metric(
                "Final Value Score",
                "Not Qualified"
            )


    # -----------------------------------------------------
    # PERFORMANCE PROFILE
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Performance Profile"
    )


    profile_df = pd.DataFrame(
        {
            "Category": [
                "OVS",
                "DVS",
                "AVS",
                "Overall"
            ],

            "Percentile": [
                player_data[
                    "OVS_Percentile"
                ],

                player_data[
                    "DVS_Percentile"
                ],

                player_data[
                    "AVS_Percentile"
                ],

                player_data[
                    "Performance_Percentile"
                ]
            ]
        }
    )


    profile_chart = (
        alt.Chart(
            profile_df
        )
        .mark_bar()
        .encode(

            x=alt.X(
                "Percentile:Q",
                title="League Percentile",
                scale=alt.Scale(
                    domain=[0, 100]
                )
            ),

            y=alt.Y(
                "Category:N",
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    "Category:N",
                    title="Category"
                ),

                alt.Tooltip(
                    "Percentile:Q",
                    title="Percentile",
                    format=".1f"
                )
            ]
        )
        .properties(
            height=250
        )
    )


    st.altair_chart(
        profile_chart,
        use_container_width=True
    )


    # -----------------------------------------------------
    # UNDERLYING STATS
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Underlying Statistics"
    )


    offense_col, defense_col, availability_col = (
        st.columns(3)
    )


    with offense_col:

        st.markdown(
            "### 🏀 Offense"
        )

        st.write(
            f"**True Shooting %:** "
            f"{player_data['TS%'] * 100:.1f}%"
        )

        st.write(
            f"**Offensive Win Shares:** "
            f"{player_data['OWS']:.2f}"
        )

        st.write(
            f"**Points Per Game:** "
            f"{player_data['PPG']:.1f}"
        )

        st.write(
            f"**Assists Per Game:** "
            f"{player_data['APG']:.1f}"
        )

        st.write(
            f"**Offensive Rebounds/Game:** "
            f"{player_data['ORPG']:.1f}"
        )


    with defense_col:

        st.markdown(
            "### 🛡️ Defense"
        )

        st.write(
            f"**Defensive Rebounds/Game:** "
            f"{player_data['DRPG']:.1f}"
        )

        st.write(
            f"**Steals + Blocks/Game:** "
            f"{player_data['Steals_Blocks']:.1f}"
        )

        st.write(
            f"**Defensive Win Shares:** "
            f"{player_data['DWS']:.2f}"
        )


    with availability_col:

        st.markdown(
            "### ⏱️ Availability"
        )

        st.write(
            f"**Games Played:** "
            f"{player_data['Games_Played']:.0f}"
        )

        st.write(
            f"**Minutes Per Game:** "
            f"{player_data['Minutes_Per_Game']:.1f}"
        )

        st.write(
            f"**Player Efficiency Rating:** "
            f"{player_data['PER']:.1f}"
        )


# =========================================================
# TAB 4 — PLAYER COMPARISON
# =========================================================

with tab4:

    st.header(
        "⚔️ Player Comparison"
    )

    st.write(
        """
        Compare two NBA players across performance,
        contract cost, and contract value.
        """
    )


    compare_player_list = sorted(
        master_df[
            "Player"
        ]
        .dropna()
        .unique()
    )


    select_col1, select_col2 = (
        st.columns(2)
    )


    with select_col1:

        player_1_name = st.selectbox(
            "Player 1",
            compare_player_list,
            index=0,
            key="compare_player_1"
        )


    with select_col2:

        player_2_name = st.selectbox(
            "Player 2",
            compare_player_list,
            index=1,
            key="compare_player_2"
        )


    player_1 = master_df[
        master_df["Player"]
        == player_1_name
    ].iloc[0]


    player_2 = master_df[
        master_df["Player"]
        == player_2_name
    ].iloc[0]


    st.divider()


    name_col1, name_col2 = (
        st.columns(2)
    )


    with name_col1:

        st.subheader(
            player_1_name
        )


    with name_col2:

        st.subheader(
            player_2_name
        )


    st.markdown(
        "### Overall Player Score"
    )


    overall_col1, overall_col2 = (
        st.columns(2)
    )


    with overall_col1:

        st.metric(
            player_1_name,
            f"{player_1['Overall_Player_Score']:.2f}"
        )


    with overall_col2:

        st.metric(
            player_2_name,
            f"{player_2['Overall_Player_Score']:.2f}"
        )


    st.markdown(
        "### Performance Breakdown"
    )


    comparison_data = pd.DataFrame(
        {
            "Category": [
                "OVS",
                "DVS",
                "AVS"
            ],

            player_1_name: [
                player_1["OVS"],
                player_1["DVS"],
                player_1["AVS"]
            ],

            player_2_name: [
                player_2["OVS"],
                player_2["DVS"],
                player_2["AVS"]
            ]
        }
    )


    comparison_long = (
        comparison_data
        .melt(
            id_vars="Category",
            var_name="Player",
            value_name="Score"
        )
    )


    comparison_chart = (
        alt.Chart(
            comparison_long
        )
        .mark_bar()
        .encode(

            x=alt.X(
                "Category:N",
                title=None
            ),

            y=alt.Y(
                "Score:Q",
                title="Score"
            ),

            xOffset="Player:N",

            color=alt.Color(
                "Player:N",
                title="Player"
            ),

            tooltip=[
                alt.Tooltip(
                    "Player:N",
                    title="Player"
                ),

                alt.Tooltip(
                    "Category:N",
                    title="Category"
                ),

                alt.Tooltip(
                    "Score:Q",
                    title="Score",
                    format=".2f"
                )
            ]
        )
        .properties(
            height=400
        )
    )


    st.altair_chart(
        comparison_chart,
        use_container_width=True
    )


    st.markdown(
        "### Contract Comparison"
    )


    salary_col1, salary_col2 = (
        st.columns(2)
    )


    with salary_col1:

        st.metric(
            f"{player_1_name} Salary",
            f"${player_1['Salary']:,.0f}"
        )

        st.metric(
            f"{player_1_name} Salary / Game",
            f"${player_1['Salary_Per_Game']:,.0f}"
        )


    with salary_col2:

        st.metric(
            f"{player_2_name} Salary",
            f"${player_2['Salary']:,.0f}"
        )

        st.metric(
            f"{player_2_name} Salary / Game",
            f"${player_2['Salary_Per_Game']:,.0f}"
        )


    st.markdown(
        "### Contract Value"
    )


    value_col1, value_col2 = (
        st.columns(2)
    )


    with value_col1:

        if (
            player_1[
                "Overall_Player_Score"
            ]
            >= MINIMUM_PLAYER_SCORE
        ):

            st.metric(
                player_1_name,
                f"{player_1['Final_Value_Score']:.2f}"
            )

        else:

            st.metric(
                player_1_name,
                "Not Qualified"
            )


    with value_col2:

        if (
            player_2[
                "Overall_Player_Score"
            ]
            >= MINIMUM_PLAYER_SCORE
        ):

            st.metric(
                player_2_name,
                f"{player_2['Final_Value_Score']:.2f}"
            )

        else:

            st.metric(
                player_2_name,
                "Not Qualified"
            )


    st.divider()

    st.markdown(
        "### Statistical Comparison"
    )


    stat_comparison = pd.DataFrame(
        {
            "Metric": [
                "True Shooting %",
                "Offensive Win Shares",
                "Points Per Game",
                "Assists Per Game",
                "Offensive Rebounds/Game",
                "Defensive Rebounds/Game",
                "Steals + Blocks/Game",
                "Defensive Win Shares",
                "Games Played",
                "Minutes Per Game",
                "PER"
            ],

            player_1_name: [
                player_1["TS%"] * 100,
                player_1["OWS"],
                player_1["PPG"],
                player_1["APG"],
                player_1["ORPG"],
                player_1["DRPG"],
                player_1["Steals_Blocks"],
                player_1["DWS"],
                player_1["Games_Played"],
                player_1["Minutes_Per_Game"],
                player_1["PER"]
            ],

            player_2_name: [
                player_2["TS%"] * 100,
                player_2["OWS"],
                player_2["PPG"],
                player_2["APG"],
                player_2["ORPG"],
                player_2["DRPG"],
                player_2["Steals_Blocks"],
                player_2["DWS"],
                player_2["Games_Played"],
                player_2["Minutes_Per_Game"],
                player_2["PER"]
            ]
        }
    )


    stat_comparison[
        player_1_name
    ] = stat_comparison[
        player_1_name
    ].round(2)


    stat_comparison[
        player_2_name
    ] = stat_comparison[
        player_2_name
    ].round(2)


    st.dataframe(
        stat_comparison,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 5 — FRONT OFFICE EFFICIENCY
# =========================================================

with tab5:

    st.header("🏢 Front Office Efficiency")

    st.write(
        """
        This dashboard evaluates how effectively NBA front offices
        convert their **2026–27 payroll** into player performance
        based on the 2025–26 season.
        """
    )


    # =====================================================
    # BUILD TEAM DATABASE
    # =====================================================

    team_source = master_df[
        [
            "Player",
            "Team",
            "Salary",
            "OVS",
            "DVS",
            "AVS",
            "Overall_Player_Score",
            "Minutes_Per_Game",
            "Final_Value_Score"
        ]
    ].dropna(subset=["Team"]).copy()


    team_source["Weighted_Score_Contribution"] = (
        team_source["Overall_Player_Score"]
        * team_source["Minutes_Per_Game"]
    )


    team_df = (
        team_source
        .groupby("Team")
        .agg(
            Player_Count=("Player", "count"),
            Total_Payroll=("Salary", "sum"),
            Avg_OVS=("OVS", "mean"),
            Avg_DVS=("DVS", "mean"),
            Avg_AVS=("AVS", "mean"),
            Avg_Player_Score=("Overall_Player_Score", "mean"),
            Total_Weighted_Score=("Weighted_Score_Contribution", "sum"),
            Total_Minutes=("Minutes_Per_Game", "sum"),
            Avg_Value_Score=("Final_Value_Score", "mean")
        )
        .reset_index()
    )


    team_df["Weighted_Player_Score"] = (
        team_df["Total_Weighted_Score"]
        / team_df["Total_Minutes"]
    )
# TEMPORARY TEAM COVERAGE CHECK
st.write(
    team_df[
        ["Team", "Player_Count", "Total_Payroll"]
    ].sort_values(
        "Player_Count",
        ascending=False
    )
)

    # =====================================================
    # TEAM RANKS + PERCENTILES
    # =====================================================

    team_df["Payroll_Rank"] = (
        team_df["Total_Payroll"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )


    team_df["Performance_Rank"] = (
        team_df["Weighted_Player_Score"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )


    team_df["Payroll_Percentile"] = (
        team_df["Total_Payroll"]
        .rank(
            pct=True,
            method="average"
        )
        * 100
    )


    team_df["Performance_Percentile"] = (
        team_df["Weighted_Player_Score"]
        .rank(
            pct=True,
            method="average"
        )
        * 100
    )


    team_df["Efficiency_Gap"] = (
        team_df["Performance_Percentile"]
        - team_df["Payroll_Percentile"]
    )


    team_df["Efficiency_Rank"] = (
        team_df["Efficiency_Gap"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )


    # =====================================================
    # CLEAN DISPLAY TABLE
    # =====================================================

    team_display = team_df[
        [
            "Efficiency_Rank",
            "Team",
            "Total_Payroll",
            "Payroll_Rank",
            "Avg_Player_Score",
            "Weighted_Player_Score",
            "Performance_Rank",
            "Efficiency_Gap",
            "Avg_OVS",
            "Avg_DVS",
            "Avg_AVS"
        ]
    ].copy()


    team_display = team_display.sort_values(
        "Efficiency_Rank"
    )


    for col in [
        "Avg_Player_Score",
        "Weighted_Player_Score",
        "Efficiency_Gap",
        "Avg_OVS",
        "Avg_DVS",
        "Avg_AVS"
    ]:
        team_display[col] = team_display[col].round(2)


    team_display["Total_Payroll"] = (
        team_display["Total_Payroll"]
        .apply(
            lambda x: f"${x:,.0f}"
        )
    )


    # =====================================================
    # HEADLINE METRICS
    # =====================================================

    most_efficient = (
        team_df
        .sort_values("Efficiency_Rank")
        .iloc[0]
    )


    highest_payroll = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=False
        )
        .iloc[0]
    )


    best_performance = (
        team_df
        .sort_values(
            "Weighted_Player_Score",
            ascending=False
        )
        .iloc[0]
    )


    lowest_payroll = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=True
        )
        .iloc[0]
    )


    front1, front2, front3, front4 = st.columns(4)


    with front1:

        st.metric(
            "Most Efficient Front Office",
            most_efficient["Team"]
        )


    with front2:

        st.metric(
            "Highest Payroll",
            highest_payroll["Team"],
            f"${highest_payroll['Total_Payroll']:,.0f}"
        )


    with front3:

        st.metric(
            "Best Team Performance",
            best_performance["Team"],
            f"{best_performance['Weighted_Player_Score']:.2f}"
        )


    with front4:

        st.metric(
            "Lowest Payroll",
            lowest_payroll["Team"],
            f"${lowest_payroll['Total_Payroll']:,.0f}"
        )


    st.divider()


    # =====================================================
    # 1. FRONT OFFICE LEADERBOARD
    # =====================================================

    st.subheader("Front Office Efficiency Leaderboard")

    st.write(
        """
        Efficiency compares each team's **performance percentile**
        with its **payroll percentile**.

        A positive Efficiency Gap means the team is producing a
        higher level of performance than its payroll ranking would suggest.
        """
    )


    st.dataframe(
        team_display,
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    # =====================================================
    # 2. PAYROLL ANALYSIS
    # =====================================================

    st.subheader("Payroll Analysis")

    st.write(
        """
        Spending more does not automatically mean getting more value.
        These rankings compare the NBA's highest- and lowest-payroll
        teams with the performance those payrolls are producing.
        """
    )


    highest_payroll_teams = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=False
        )
        .head(5)
        .copy()
    )


    lowest_payroll_teams = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=True
        )
        .head(5)
        .copy()
    )


    high_payroll_col, low_payroll_col = st.columns(2)


    # -----------------------------------------------------
    # HIGHEST PAYROLLS
    # -----------------------------------------------------

    with high_payroll_col:

        st.markdown("### 💰 Highest Payrolls")

        st.caption(
            "The NBA's biggest 2026–27 payrolls"
        )


        highest_payroll_chart = (
            alt.Chart(
                highest_payroll_teams
            )
            .mark_bar()
            .encode(

                x=alt.X(
                    "Total_Payroll:Q",
                    title="2026–27 Payroll",
                    axis=alt.Axis(
                        format="$,.0f"
                    )
                ),

                y=alt.Y(
                    "Team:N",
                    title=None,
                    sort="-x"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Team:N",
                        title="Team"
                    ),

                    alt.Tooltip(
                        "Total_Payroll:Q",
                        title="Payroll",
                        format="$,.0f"
                    ),

                    alt.Tooltip(
                        "Payroll_Rank:Q",
                        title="Payroll Rank"
                    ),

                    alt.Tooltip(
                        "Weighted_Player_Score:Q",
                        title="Weighted Performance",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Performance_Rank:Q",
                        title="Performance Rank"
                    ),

                    alt.Tooltip(
                        "Efficiency_Rank:Q",
                        title="Efficiency Rank"
                    )
                ]
            )
            .properties(
                height=300
            )
        )


        st.altair_chart(
            highest_payroll_chart,
            use_container_width=True
        )


        for _, row in highest_payroll_teams.iterrows():

            st.caption(
                f"**{row['Team']}** — "
                f"${row['Total_Payroll']:,.0f} | "
                f"Performance #{int(row['Performance_Rank'])} | "
                f"Efficiency #{int(row['Efficiency_Rank'])}"
            )


    # -----------------------------------------------------
    # LOWEST PAYROLLS
    # -----------------------------------------------------

    with low_payroll_col:

        st.markdown("### 🏷️ Lowest Payrolls")

        st.caption(
            "The NBA's smallest 2026–27 payrolls"
        )


        lowest_payroll_chart = (
            alt.Chart(
                lowest_payroll_teams
            )
            .mark_bar()
            .encode(

                x=alt.X(
                    "Total_Payroll:Q",
                    title="2026–27 Payroll",
                    axis=alt.Axis(
                        format="$,.0f"
                    )
                ),

                y=alt.Y(
                    "Team:N",
                    title=None,
                    sort="x"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Team:N",
                        title="Team"
                    ),

                    alt.Tooltip(
                        "Total_Payroll:Q",
                        title="Payroll",
                        format="$,.0f"
                    ),

                    alt.Tooltip(
                        "Payroll_Rank:Q",
                        title="Payroll Rank"
                    ),

                    alt.Tooltip(
                        "Weighted_Player_Score:Q",
                        title="Weighted Performance",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Performance_Rank:Q",
                        title="Performance Rank"
                    ),

                    alt.Tooltip(
                        "Efficiency_Rank:Q",
                        title="Efficiency Rank"
                    )
                ]
            )
            .properties(
                height=300
            )
        )


        st.altair_chart(
            lowest_payroll_chart,
            use_container_width=True
        )


        for _, row in lowest_payroll_teams.iterrows():

            st.caption(
                f"**{row['Team']}** — "
                f"${row['Total_Payroll']:,.0f} | "
                f"Performance #{int(row['Performance_Rank'])} | "
                f"Efficiency #{int(row['Efficiency_Rank'])}"
            )


    # -----------------------------------------------------
    # SPENDING CONTEXT
    # -----------------------------------------------------

    st.markdown("### Spending Context")


    highest_spender = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=False
        )
        .iloc[0]
    )


    lowest_spender = (
        team_df
        .sort_values(
            "Total_Payroll",
            ascending=True
        )
        .iloc[0]
    )


    payroll_difference = (
        highest_spender["Total_Payroll"]
        - lowest_spender["Total_Payroll"]
    )


    context1, context2, context3 = st.columns(3)


    with context1:

        st.metric(
            "Highest-Spending Team",
            highest_spender["Team"],
            f"Performance #{int(highest_spender['Performance_Rank'])}"
        )


    with context2:

        st.metric(
            "Lowest-Spending Team",
            lowest_spender["Team"],
            f"Performance #{int(lowest_spender['Performance_Rank'])}"
        )


    with context3:

        st.metric(
            "Payroll Difference",
            f"${payroll_difference:,.0f}"
        )


    st.divider()


    # =====================================================
    # 3. PAYROLL VS TEAM PERFORMANCE
    # =====================================================

    st.subheader("Payroll vs. Team Performance")

    st.write(
        """
        This chart shows how each front office's total payroll compares
        with the minutes-weighted performance of its contracted players.
        """
    )


    team_chart = (
        alt.Chart(team_df)
        .mark_circle(
            size=140,
            opacity=0.8
        )
        .encode(

            x=alt.X(
                "Total_Payroll:Q",
                title="2026–27 Payroll",
                axis=alt.Axis(
                    format="$,.0f"
                )
            ),

            y=alt.Y(
                "Weighted_Player_Score:Q",
                title="Minutes-Weighted Player Score"
            ),

            tooltip=[
                alt.Tooltip(
                    "Team:N",
                    title="Team"
                ),

                alt.Tooltip(
                    "Total_Payroll:Q",
                    title="Payroll",
                    format="$,.0f"
                ),

                alt.Tooltip(
                    "Weighted_Player_Score:Q",
                    title="Weighted Performance",
                    format=".2f"
                ),

                alt.Tooltip(
                    "Payroll_Rank:Q",
                    title="Payroll Rank"
                ),

                alt.Tooltip(
                    "Performance_Rank:Q",
                    title="Performance Rank"
                ),

                alt.Tooltip(
                    "Efficiency_Rank:Q",
                    title="Efficiency Rank"
                ),

                alt.Tooltip(
                    "Efficiency_Gap:Q",
                    title="Efficiency Gap",
                    format="+.1f"
                )
            ]
        )
        .properties(
            height=500
        )
        .interactive()
    )


    st.altair_chart(
        team_chart,
        use_container_width=True
    )


    st.divider()


    # =====================================================
    # 4. FRONT OFFICE EFFICIENCY LEADERS
    # =====================================================

    st.subheader("Front Office Efficiency Leaders")

    st.write(
        """
        These rankings compare each team's **payroll percentile**
        with its **minutes-weighted performance percentile**.

        Teams with a large positive gap are generating stronger
        performance than their payroll level would suggest, while
        teams with a large negative gap are spending at a higher
        level than their performance would suggest.
        """
    )


    most_efficient_teams = (
        team_df
        .sort_values(
            "Efficiency_Gap",
            ascending=False
        )
        .head(5)
        .copy()
    )


    least_efficient_teams = (
        team_df
        .sort_values(
            "Efficiency_Gap",
            ascending=True
        )
        .head(5)
        .copy()
    )


    efficient_col, inefficient_col = st.columns(2)


    # -----------------------------------------------------
    # MOST EFFICIENT
    # -----------------------------------------------------

    with efficient_col:

        st.markdown("### 💎 Most Efficient")

        st.caption(
            "Performance exceeds payroll level"
        )


        most_efficient_chart = (
            alt.Chart(
                most_efficient_teams
            )
            .mark_bar()
            .encode(

                x=alt.X(
                    "Efficiency_Gap:Q",
                    title="Efficiency Gap"
                ),

                y=alt.Y(
                    "Team:N",
                    title=None,
                    sort="-x"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Team:N",
                        title="Team"
                    ),

                    alt.Tooltip(
                        "Total_Payroll:Q",
                        title="Payroll",
                        format="$,.0f"
                    ),

                    alt.Tooltip(
                        "Payroll_Rank:Q",
                        title="Payroll Rank"
                    ),

                    alt.Tooltip(
                        "Weighted_Player_Score:Q",
                        title="Weighted Performance",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Performance_Rank:Q",
                        title="Performance Rank"
                    ),

                    alt.Tooltip(
                        "Efficiency_Gap:Q",
                        title="Efficiency Gap",
                        format="+.1f"
                    )
                ]
            )
            .properties(
                height=300
            )
        )


        st.altair_chart(
            most_efficient_chart,
            use_container_width=True
        )


        for _, row in most_efficient_teams.iterrows():

            st.caption(
                f"**{row['Team']}** — "
                f"Payroll #{int(row['Payroll_Rank'])} → "
                f"Performance #{int(row['Performance_Rank'])}"
            )


    # -----------------------------------------------------
    # LEAST EFFICIENT
    # -----------------------------------------------------

    with inefficient_col:

        st.markdown("### 💸 Least Efficient")

        st.caption(
            "Payroll level exceeds performance"
        )


        least_efficient_chart = (
            alt.Chart(
                least_efficient_teams
            )
            .mark_bar()
            .encode(

                x=alt.X(
                    "Efficiency_Gap:Q",
                    title="Efficiency Gap"
                ),

                y=alt.Y(
                    "Team:N",
                    title=None,
                    sort="x"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Team:N",
                        title="Team"
                    ),

                    alt.Tooltip(
                        "Total_Payroll:Q",
                        title="Payroll",
                        format="$,.0f"
                    ),

                    alt.Tooltip(
                        "Payroll_Rank:Q",
                        title="Payroll Rank"
                    ),

                    alt.Tooltip(
                        "Weighted_Player_Score:Q",
                        title="Weighted Performance",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Performance_Rank:Q",
                        title="Performance Rank"
                    ),

                    alt.Tooltip(
                        "Efficiency_Gap:Q",
                        title="Efficiency Gap",
                        format="+.1f"
                    )
                ]
            )
            .properties(
                height=300
            )
        )


        st.altair_chart(
            least_efficient_chart,
            use_container_width=True
        )


        for _, row in least_efficient_teams.iterrows():

            st.caption(
                f"**{row['Team']}** — "
                f"Payroll #{int(row['Payroll_Rank'])} → "
                f"Performance #{int(row['Performance_Rank'])}"
            )


    with st.expander(
        "How is Front Office Efficiency calculated?"
    ):

        st.markdown(
            """
            **Step 1 — Payroll Percentile**  
            Each team's total 2026–27 payroll is ranked against
            the other teams in the database.

            **Step 2 — Performance Percentile**  
            Team performance is measured using its
            **minutes-weighted Overall Player Score**.

            Players receiving more playing time therefore have
            more influence on the team's performance score.

            **Step 3 — Efficiency Gap**

            **Efficiency Gap = Performance Percentile − Payroll Percentile**

            A **positive** number means the team's performance
            ranks higher than its spending.

            A **negative** number means the team's spending
            ranks higher than its performance.
            """
        )


    st.divider()


    # =====================================================
    # 5. FRONT OFFICE COMPARISON
    # =====================================================

    st.subheader("⚔️ Front Office Comparison")

    st.write(
        """
        Compare two NBA front offices across payroll, performance,
        and spending efficiency.
        """
    )


    team_list = sorted(
        team_df["Team"]
        .dropna()
        .unique()
    )


    team_select1, team_select2 = st.columns(2)


    with team_select1:

        team_1_name = st.selectbox(
            "Front Office 1",
            team_list,
            index=0,
            key="front_office_1"
        )


    with team_select2:

        team_2_name = st.selectbox(
            "Front Office 2",
            team_list,
            index=1,
            key="front_office_2"
        )


    team_1 = team_df[
        team_df["Team"] == team_1_name
    ].iloc[0]


    team_2 = team_df[
        team_df["Team"] == team_2_name
    ].iloc[0]


    # -----------------------------------------------------
    # PAYROLL COMPARISON
    # -----------------------------------------------------

    st.markdown("### Payroll")

    payroll1, payroll2 = st.columns(2)


    with payroll1:

        st.metric(
            team_1_name,
            f"${team_1['Total_Payroll']:,.0f}",
            f"Payroll Rank #{int(team_1['Payroll_Rank'])}"
        )


    with payroll2:

        st.metric(
            team_2_name,
            f"${team_2['Total_Payroll']:,.0f}",
            f"Payroll Rank #{int(team_2['Payroll_Rank'])}"
        )


    # -----------------------------------------------------
    # PERFORMANCE COMPARISON
    # -----------------------------------------------------

    st.markdown("### Team Performance")

    performance1, performance2 = st.columns(2)


    with performance1:

        st.metric(
            team_1_name,
            f"{team_1['Weighted_Player_Score']:.2f}",
            f"Performance Rank #{int(team_1['Performance_Rank'])}"
        )


    with performance2:

        st.metric(
            team_2_name,
            f"{team_2['Weighted_Player_Score']:.2f}",
            f"Performance Rank #{int(team_2['Performance_Rank'])}"
        )


    # -----------------------------------------------------
    # EFFICIENCY COMPARISON
    # -----------------------------------------------------

    st.markdown("### Front Office Efficiency")

    efficiency1, efficiency2 = st.columns(2)


    with efficiency1:

        st.metric(
            team_1_name,
            f"{team_1['Efficiency_Gap']:+.1f}",
            f"Efficiency Rank #{int(team_1['Efficiency_Rank'])}"
        )


    with efficiency2:

        st.metric(
            team_2_name,
            f"{team_2['Efficiency_Gap']:+.1f}",
            f"Efficiency Rank #{int(team_2['Efficiency_Rank'])}"
        )


    # -----------------------------------------------------
    # OVS / DVS / AVS COMPARISON
    # -----------------------------------------------------

    st.markdown("### Team Score Breakdown")


    front_comparison = pd.DataFrame(
        {
            "Category": [
                "OVS",
                "DVS",
                "AVS"
            ],

            team_1_name: [
                team_1["Avg_OVS"],
                team_1["Avg_DVS"],
                team_1["Avg_AVS"]
            ],

            team_2_name: [
                team_2["Avg_OVS"],
                team_2["Avg_DVS"],
                team_2["Avg_AVS"]
            ]
        }
    )


    front_comparison_long = (
        front_comparison
        .melt(
            id_vars="Category",
            var_name="Team",
            value_name="Score"
        )
    )


    front_comparison_chart = (
        alt.Chart(
            front_comparison_long
        )
        .mark_bar()
        .encode(

            x=alt.X(
                "Category:N",
                title=None
            ),

            y=alt.Y(
                "Score:Q",
                title="Average Team Score"
            ),

            xOffset="Team:N",

            color=alt.Color(
                "Team:N",
                title="Team"
            ),

            tooltip=[
                alt.Tooltip(
                    "Team:N",
                    title="Team"
                ),

                alt.Tooltip(
                    "Category:N",
                    title="Category"
                ),

                alt.Tooltip(
                    "Score:Q",
                    title="Score",
                    format=".2f"
                )
            ]
        )
        .properties(
            height=400
        )
    )


    st.altair_chart(
        front_comparison_chart,
        use_container_width=True
    )


    # -----------------------------------------------------
    # DIRECT DIFFERENCES
    # -----------------------------------------------------

    st.markdown("### Head-to-Head Differences")


    payroll_diff = (
        team_1["Total_Payroll"]
        - team_2["Total_Payroll"]
    )


    performance_diff = (
        team_1["Weighted_Player_Score"]
        - team_2["Weighted_Player_Score"]
    )


    efficiency_diff = (
        team_1["Efficiency_Gap"]
        - team_2["Efficiency_Gap"]
    )


    diff1, diff2, diff3 = st.columns(3)


    with diff1:

        st.metric(
            "Payroll Difference",
            f"${abs(payroll_diff):,.0f}"
        )


    with diff2:

        st.metric(
            "Performance Difference",
            f"{abs(performance_diff):.2f}"
        )


    with diff3:

        st.metric(
            "Efficiency Gap Difference",
            f"{abs(efficiency_diff):.1f}"
        )
        
# =========================================================
# TAB 6 — METHODOLOGY
# =========================================================

with tab6:

    st.header(
        "Methodology"
    )

    st.write(
        """
        The model was designed to answer two separate questions:

        **1. How good was the player?**

        **2. How much value does the team receive relative to
        the player's contract?**
        """
    )

    st.divider()


    st.subheader(
        "1. Statistical Benchmarking"
    )

    st.write(
        """
        Each statistic is compared against the **95th percentile
        of NBA players** in the dataset.

        A score of **100** represents approximately 95th-percentile
        performance.

        Individual statistical scores are capped at **115** so
        that one extreme statistic cannot disproportionately control
        an entire category.
        """
    )


    st.subheader(
        "2. Offensive Value Score — OVS"
    )

    st.write(
        """
        OVS is the average of:

        - True Shooting Percentage
        - Offensive Win Shares
        - Points Per Game
        - Assists Per Game
        - Offensive Rebounds Per Game
        """
    )


    st.subheader(
        "3. Defensive Value Score — DVS"
    )

    st.write(
        """
        DVS is the average of:

        - Defensive Rebounds Per Game
        - Steals + Blocks Per Game
        - Defensive Win Shares
        """
    )


    st.subheader(
        "4. Availability Value Score — AVS"
    )

    st.write(
        """
        AVS incorporates:

        - Games Played
        - Minutes Per Game
        - Player Efficiency Rating
        """
    )


    st.subheader(
        "5. Overall Player Score"
    )


    st.latex(
        r"""
        Player\ Score =
        0.36(OVS)
        +
        0.34(DVS)
        +
        0.30(AVS)
        """
    )


    st.subheader(
        "6. Salary Per Game"
    )


    st.latex(
        r"""
        Salary\ Per\ Game =
        \frac{Annual\ Salary}{82}
        """
    )


    st.subheader(
        "7. Final Value Score"
    )


    st.latex(
        r"""
        Final\ Value =
        \frac{Overall\ Player\ Score}
        {(Salary\ Per\ Game\ in\ \$100K)^{0.30}}
        """
    )


    st.write(
        """
        Players must have an **Overall Player Score of at least 60**
        to qualify for the primary Value Leaderboard.
        """
    )


    st.subheader(
        "8. Elite Bargains"
    )

    st.write(
        """
        Elite Bargains must rank in the **80th percentile or higher**
        in Overall Player Score and are then ranked by Final Value Score.
        """
    )


    st.subheader(
        "9. Least Efficient Contracts"
    )

    st.write(
        """
        Least Efficient Contracts require:

        - **80th percentile or higher salary**
        - **Below 50th percentile performance**

        Players are ranked by the difference between their
        performance percentile and salary percentile.
        """
    )


    st.subheader(
        "10. Data"
    )

    st.write(
        """
        Player performance is based on **2025–26 NBA statistics**.

        Contract value uses **2026–27 salary and contract team**.

        Player statistics and contract data were collected from
        Basketball-Reference.
        """
    )


    st.subheader(
        "11. Model Limitations"
    )

    st.write(
        """
        No single numerical model can completely describe an NBA
        player's value.

        Role, position, lineup context, coaching, injuries,
        playoff performance, age, contract structure, and future
        development are not fully captured.

        The model should therefore be interpreted as an analytical
        tool for comparing player production and contract efficiency,
        rather than as a definitive ranking of NBA talent.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "NBA Player Value Analytics — Independent sports business analytics project"
)
