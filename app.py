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
    leaderboard = pd.read_csv("nba_value_leaderboard.csv")
    master = pd.read_csv("nba_value_master_database.csv")

    # Make sure salary is numeric
    master["Salary"] = pd.to_numeric(
        master["Salary"],
        errors="coerce"
    )

    # Recalculate salary per game
    master["Salary_Per_Game"] = master["Salary"] / 82

    # Salary per game expressed in $100,000 units
    master["Salary_Per_Game_100K"] = (
        master["Salary_Per_Game"] / 100000
    )

    # Official Version 1 value formula
    master["Final_Value_Score"] = (
        master["Overall_Player_Score"]
        / (
            master["Salary_Per_Game_100K"]
            ** ALPHA
        )
    )

    return leaderboard, master


leaderboard_df, master_df = load_data()
# =========================================================
# CONTRACT / PERFORMANCE PERCENTILES
# =========================================================

# Performance percentile:
# What percentage of players have a lower Overall Player Score?
master_df["Performance_Percentile"] = (
    master_df["Overall_Player_Score"]
    .rank(pct=True)
    * 100
)

# Salary percentile:
# What percentage of players earn less?
master_df["Salary_Percentile"] = (
    master_df["Salary"]
    .rank(pct=True)
    * 100
)

# Positive = performance exceeds salary percentile
# Negative = salary exceeds performance percentile
master_df["Contract_Efficiency_Gap"] = (
    master_df["Performance_Percentile"]
    - master_df["Salary_Percentile"]
)

# =========================================================
# HEADER
# =========================================================

st.title("🏀 NBA Player Value Analytics")

st.subheader(
    "Measuring NBA player performance relative to contract cost"
)

st.write(
    """
    NBA Player Value Analytics is a sports business analytics project
    designed to evaluate how much basketball value a player provides
    relative to the money his team is paying him.

    Rather than simply ranking the best players in the NBA, this model
    separates player performance from contract efficiency by combining
    offensive production, defensive performance, availability,
    efficiency, and salary.
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
    st.metric(
        "Value-Qualified Players",
        f"{len(leaderboard_df):,}"
    )

with col3:
    best_value_player = leaderboard_df.iloc[0]["Player"]

    st.metric(
        "Best Contract Value",
        best_value_player
    )

with col4:
    best_player_row = master_df.loc[
        master_df["Overall_Player_Score"].idxmax()
    ]

    st.metric(
        "Highest Player Score",
        best_player_row["Player"]
    )


st.divider()


# =========================================================
# NAVIGATION
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💰 Value Leaderboard",
        "⭐ Player Rankings",
        "🔎 Player Explorer",
        "⚔️ Compare Players",
        "🧠 Methodology"
    ]
)


# =========================================================
# TAB 1 — VALUE LEADERBOARD
# =========================================================

with tab1:

    st.header("NBA Contract Value Leaderboard")

    st.write(
        """
        This leaderboard ranks players based on how much basketball
        performance they provide relative to their 2026–27 salary.

        Players must have an **Overall Player Score of at least 60**
        to qualify for the main Value Leaderboard.
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
    # SALARY VS PERFORMANCE VALUE QUADRANT
    # =====================================================

    st.divider()

    st.subheader("Salary vs. Player Performance")

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


    # -----------------------------------------------------
    # PREPARE CHART DATA
    # -----------------------------------------------------

    chart_df = master_df[
        [
            "Player",
            "Salary",
            "Overall_Player_Score",
            "Final_Value_Score"
        ]
    ].dropna().copy()

    median_salary = chart_df["Salary"].median()
    median_player_score = chart_df[
        "Overall_Player_Score"
    ].median()

    max_salary = chart_df["Salary"].max()
    min_salary = chart_df["Salary"].min()

    max_score = chart_df["Overall_Player_Score"].max()
    min_score = chart_df["Overall_Player_Score"].min()


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
    # MEDIAN PLAYER SCORE LINE
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
    # QUADRANT LABEL POSITIONS
    # -----------------------------------------------------

    left_x = min_salary + (
        (median_salary - min_salary) * 0.35
    )

    right_x = median_salary + (
        (max_salary - median_salary) * 0.50
    )

    top_y = median_player_score + (
        (max_score - median_player_score) * 0.75
    )

    bottom_y = min_score + (
        (median_player_score - min_score) * 0.25
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
        alt.Chart(quadrant_labels)
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


    # -----------------------------------------------------
    # COMBINE CHART
    # -----------------------------------------------------

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


    # =====================================================
    # TOP 10 CONTRACT VALUES
    # =====================================================

    st.divider()

    st.subheader("Top 10 Contract Values")

    st.write(
        """
        The ten highest-ranked contracts according to the NBA Player
        Value model. Players must have an Overall Player Score of at
        least 60 to qualify.
        """
    )

    top_10 = (
        master_df[
            master_df["Overall_Player_Score"] >= MINIMUM_PLAYER_SCORE
        ]
        .sort_values(
            "Final_Value_Score",
            ascending=False
        )
        .head(10)
        .copy()
    )

    top_10_chart = (
        alt.Chart(top_10)
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
    # ELITE BARGAINS VS LEAST EFFICIENT CONTRACTS
    # =====================================================

    st.divider()

    st.header("Contract Efficiency Analysis")

    st.write(
        """
        Value can mean different things depending on the question.

        **Elite Bargains** identifies players performing in the
        top 20% of the NBA according to the model, then determines
        which of those players provide the greatest contract value.

        **Least Efficient Contracts** identifies highly paid players
        whose performance falls below the league median.
        """
    )


    # =====================================================
    # BUILD THE TWO GROUPS
    # =====================================================

    elite_bargains = (
        master_df[
            master_df["Performance_Percentile"] >= 80
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
            (master_df["Salary_Percentile"] >= 80)
            &
            (master_df["Performance_Percentile"] < 50)
        ]
        .sort_values(
            "Contract_Efficiency_Gap",
            ascending=True
        )
        .head(10)
        .copy()
    )


    # =====================================================
    # TWO COLUMNS
    # =====================================================

    bargain_col, inefficient_col = st.columns(2)


    # =====================================================
    # ELITE BARGAINS
    # =====================================================

    with bargain_col:

        st.subheader("💎 Elite Bargains")

        st.caption(
            "Top-20% performers ranked by Contract Value Score"
        )

        bargain_chart = (
            alt.Chart(elite_bargains)
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


    # =====================================================
    # LEAST EFFICIENT CONTRACTS
    # =====================================================

    with inefficient_col:

        st.subheader("💸 Least Efficient Contracts")

        st.caption(
            "Top-20% salaries with below-median performance"
        )

        inefficient_chart = (
            alt.Chart(least_efficient)
            .mark_bar()
            .encode(

                x=alt.X(
                    "Contract_Efficiency_Gap:Q",
                    title="Performance − Salary Percentile Gap"
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


    # =====================================================
    # EXPLANATION
    # =====================================================

    with st.expander("How are these groups defined?"):

        st.markdown(
            """
            **💎 Elite Bargains**

            1. Player must rank in the **80th percentile or higher**
               in Overall Player Score.
            2. Qualifying players are ranked by the model's
               **Final Value Score**.
            3. This identifies high-level players whose contracts
               provide particularly strong value.

            **💸 Least Efficient Contracts**

            1. Player salary must rank in the **80th percentile
               or higher**.
            2. Player performance must rank **below the 50th
               percentile**.
            3. Players are ranked by the gap between their
               Performance Percentile and Salary Percentile.

            A larger negative gap indicates a greater mismatch
            between salary and measured performance.
            """
        )

# =========================================================
# TAB 2 — PURE PLAYER PERFORMANCE
# =========================================================

with tab2:

    st.header("Overall Player Rankings")

    st.write(
        """
        This ranking ignores salary entirely.

        It answers a different question:

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


    performance_df = performance_df.sort_values(
        "Overall_Player_Score",
        ascending=False
    )


    performance_df["Player_Rank"] = range(
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
        performance_df[column] = (
            performance_df[column]
            .round(2)
        )


    performance_search = st.text_input(
        "Search player rankings",
        placeholder="Example: Nikola Jokic",
        key="performance_search"
    )


    if performance_search:
        performance_df = performance_df[
            performance_df["Player"]
            .str.contains(
                performance_search,
                case=False,
                na=False
            )
        ]


    st.dataframe(
        performance_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 3 — PLAYER EXPLORER
# =========================================================

with tab3:

    st.header("Player Explorer")

    st.write(
        """
        Select any player in the database to see his offensive,
        defensive, availability, performance, salary, and contract
        value information.
        """
    )


    player_list = sorted(
        master_df["Player"]
        .dropna()
        .unique()
    )


    selected_player = st.selectbox(
        "Select a player",
        player_list
    )


    player_data = master_df[
        master_df["Player"] == selected_player
    ].iloc[0]


    st.subheader(selected_player)


    # -----------------------------------------------------
    # PLAYER SCORE CARDS
    # -----------------------------------------------------

    score1, score2, score3, score4 = st.columns(4)


    with score1:
        st.metric(
            "OVS",
            f"{player_data['OVS']:.2f}"
        )


    with score2:
        st.metric(
            "DVS",
            f"{player_data['DVS']:.2f}"
        )


    with score3:
        st.metric(
            "AVS",
            f"{player_data['AVS']:.2f}"
        )


    with score4:
        st.metric(
            "Overall Player Score",
            f"{player_data['Overall_Player_Score']:.2f}"
        )


    # -----------------------------------------------------
    # CONTRACT INFORMATION
    # -----------------------------------------------------

    st.subheader("Contract")

    contract1, contract2, contract3 = st.columns(3)


    with contract1:
        st.metric(
            "Annual Salary",
            f"${player_data['Salary']:,.0f}"
        )


    with contract2:
        st.metric(
            "Salary Per Game",
            f"${player_data['Salary_Per_Game']:,.0f}"
        )


    with contract3:

        if (
            player_data["Overall_Player_Score"]
            >= MINIMUM_PLAYER_SCORE
        ):
            st.metric(
                "Value Score",
                f"{player_data['Final_Value_Score']:.2f}"
            )

        else:
            st.metric(
                "Value Score",
                "Not Qualified"
            )


    st.divider()


    # -----------------------------------------------------
    # UNDERLYING STATISTICS
    # -----------------------------------------------------

    st.subheader("Underlying Statistics")


    offense_col, defense_col, availability_col = st.columns(3)


    # OFFENSE
    with offense_col:

        st.markdown("### 🏀 Offense")

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


    # DEFENSE
    with defense_col:

        st.markdown("### 🛡️ Defense")

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


    # AVAILABILITY
    with availability_col:

        st.markdown("### ⏱️ Availability")

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

    st.header("⚔️ Player Comparison")

    st.write(
        """
        Compare two NBA players across performance, contract cost,
        and contract value.
        """
    )

    player_list = sorted(
        master_df["Player"].dropna().unique()
    )

    select_col1, select_col2 = st.columns(2)

    with select_col1:
        player_1_name = st.selectbox(
            "Player 1",
            player_list,
            index=0,
            key="compare_player_1"
        )

    with select_col2:
        player_2_name = st.selectbox(
            "Player 2",
            player_list,
            index=1,
            key="compare_player_2"
        )

    player_1 = master_df[
        master_df["Player"] == player_1_name
    ].iloc[0]

    player_2 = master_df[
        master_df["Player"] == player_2_name
    ].iloc[0]

    st.divider()


    # =====================================================
    # PLAYER NAMES
    # =====================================================

    name_col1, name_col2 = st.columns(2)

    with name_col1:
        st.subheader(player_1_name)

    with name_col2:
        st.subheader(player_2_name)


    # =====================================================
    # OVERALL PLAYER SCORE
    # =====================================================

    st.markdown("### Overall Player Score")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            player_1_name,
            f"{player_1['Overall_Player_Score']:.2f}"
        )

    with col2:
        st.metric(
            player_2_name,
            f"{player_2['Overall_Player_Score']:.2f}"
        )


    # =====================================================
    # CATEGORY SCORES
    # =====================================================

    st.markdown("### Performance Breakdown")

    comparison_data = pd.DataFrame(
        {
            "Category": [
                "Offense",
                "Defense",
                "Availability"
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

    comparison_long = comparison_data.melt(
        id_vars="Category",
        var_name="Player",
        value_name="Score"
    )

    comparison_chart = (
        alt.Chart(comparison_long)
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


    # =====================================================
    # CONTRACT COMPARISON
    # =====================================================

    st.markdown("### Contract Comparison")

    salary_col1, salary_col2 = st.columns(2)

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


    # =====================================================
    # VALUE SCORE
    # =====================================================

    st.markdown("### Contract Value")

    value_col1, value_col2 = st.columns(2)

    with value_col1:

        if (
            player_1["Overall_Player_Score"]
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
            player_2["Overall_Player_Score"]
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


    # =====================================================
    # RAW STAT COMPARISON
    # =====================================================

    st.divider()

    st.markdown("### Statistical Comparison")

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
                player_1["TS%"],
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
                player_2["TS%"],
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

    stat_comparison[player_1_name] = (
        stat_comparison[player_1_name].round(2)
    )

    stat_comparison[player_2_name] = (
        stat_comparison[player_2_name].round(2)
    )

    st.dataframe(
        stat_comparison,
        use_container_width=True,
        hide_index=True
    )
# =========================================================
# TAB 4 — METHODOLOGY
# =========================================================

with tab5:

    st.header("Methodology")

    st.write(
        """
        The model was designed to answer two separate questions:

        **1. How good was the player?**

        **2. How much value does the team receive relative to
        the player's contract?**
        """
    )

    st.divider()


    # -----------------------------------------------------
    # STATISTICAL BENCHMARKING
    # -----------------------------------------------------

    st.subheader("1. Statistical Benchmarking")

    st.write(
        """
        Each statistic is compared against the **95th percentile
        of NBA players** in the dataset.

        A statistical score of **100** therefore represents
        approximately 95th-percentile NBA performance in that
        statistic.

        Players performing above this benchmark may receive
        scores above 100.

        Individual statistical scores are capped at **115** so
        that one extreme statistic cannot disproportionately
        control an entire category.
        """
    )


    # -----------------------------------------------------
    # OVS
    # -----------------------------------------------------

    st.subheader("2. Offensive Value Score — OVS")

    st.write(
        """
        OVS measures offensive production and efficiency.

        It is the average of:

        - True Shooting Percentage
        - Offensive Win Shares
        - Points Per Game
        - Assists Per Game
        - Offensive Rebounds Per Game
        """
    )


    # -----------------------------------------------------
    # DVS
    # -----------------------------------------------------

    st.subheader("3. Defensive Value Score — DVS")

    st.write(
        """
        DVS measures defensive production.

        It is the average of:

        - Defensive Rebounds Per Game
        - Steals + Blocks Per Game
        - Defensive Win Shares
        """
    )


    # -----------------------------------------------------
    # AVS
    # -----------------------------------------------------

    st.subheader("4. Availability Value Score — AVS")

    st.write(
        """
        AVS evaluates both availability and productive minutes.

        It incorporates:

        - Games Played
        - Minutes Per Game
        - Player Efficiency Rating
        """
    )


    # -----------------------------------------------------
    # OVERALL PLAYER SCORE
    # -----------------------------------------------------

    st.subheader("5. Overall Player Score")

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

    st.write(
        """
        The final basketball performance score therefore assigns:

        - **36% weight to offense**
        - **34% weight to defense**
        - **30% weight to availability and efficiency**
        """
    )


    # -----------------------------------------------------
    # SALARY
    # -----------------------------------------------------

    st.subheader("6. Salary Per Game")

    st.latex(
        r"""
        Salary\ Per\ Game =
        \frac{Annual\ Salary}{82}
        """
    )

    st.write(
        """
        Salary is divided across the NBA's 82 scheduled regular
        season games rather than the player's actual games played.

        Availability is already measured separately through AVS.
        """
    )


    # -----------------------------------------------------
    # VALUE FORMULA
    # -----------------------------------------------------

    st.subheader("7. Final Value Score")

    st.write(
        """
        Simply dividing performance by salary would heavily
        penalize superstar players because NBA salary differences
        are much larger than differences on a bounded performance
        scale.

        To reduce that distortion while still rewarding inexpensive
        contracts, the salary denominator is transformed using an
        exponent of **0.30**.
        """
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
        Players must also have an **Overall Player Score of at
        least 60** to qualify for the primary Value Leaderboard.

        This prevents extremely inexpensive contracts from
        artificially pushing low-performing players to the top
        of the rankings.
        """
    )


    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    st.subheader("8. Data")

    st.write(
        """
        Player performance is based on **2025–26 NBA statistics**.

        Contract value uses **2026–27 salary**, meaning the model
        evaluates each player's upcoming contract cost using his
        most recent full season of performance.

        Player statistics and contract information were collected
        from Basketball-Reference.
        """
    )


    # -----------------------------------------------------
    # LIMITATIONS
    # -----------------------------------------------------

    st.subheader("9. Model Limitations")

    st.write(
        """
        No single numerical model can completely describe an NBA
        player's value.

        Factors such as role, position, lineup context, coaching,
        injuries, playoff performance, contract structure, age,
        and future development are not completely captured by the
        current model.

        The model should therefore be interpreted as a tool for
        comparing statistical production and contract efficiency,
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
