import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NBA Player Value Analytics",
    page_icon="🏀",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    leaderboard = pd.read_csv("nba_value_leaderboard.csv")
    master = pd.read_csv("nba_value_master_database.csv")
    return leaderboard, master


leaderboard_df, master_df = load_data()


# =========================================================
# HEADER
# =========================================================

st.title("🏀 NBA Player Value Analytics")

st.subheader(
    "Measuring NBA player performance relative to contract cost"
)

st.write(
    """
    NBA Player Value Analytics is a sports business analytics project designed
    to evaluate how much basketball value a player provides relative to the
    money his team is paying him.

    Rather than simply ranking the best players in the NBA, this model separates
    player performance from contract efficiency by combining offensive,
    defensive, and availability metrics with salary data.
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
    top_value_player = leaderboard_df.iloc[0]["Player"]
    st.metric(
        "Best Contract Value",
        top_value_player
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

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "💰 Value Leaderboard",
        "⭐ Player Rankings",
        "🔎 Player Explorer",
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
        This leaderboard ranks players based on how much basketball value they
        provide relative to their 2026–27 salary.

        Players must have an Overall Player Score of at least **60** to qualify.
        """
    )

    search_value = st.text_input(
        "Search for a player",
        placeholder="Example: Stephen Curry",
        key="value_search"
    )

    value_display = leaderboard_df.copy()

    if search_value:
        value_display = value_display[
            value_display["Player"]
            .str.contains(search_value, case=False, na=False)
        ]

    st.dataframe(
        value_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================================
    # SALARY VS PERFORMANCE CHART
    # =====================================================

    st.subheader("Salary vs. Player Performance")

    st.write(
        """
        This chart compares each player's Overall Player Score
        with his annual salary. Players farther toward the
        upper-left provide stronger performance at a lower cost.
        """
    )

    chart_df = master_df[
        [
            "Player",
            "Salary",
            "Overall_Player_Score"
        ]
    ].dropna().copy()

    st.scatter_chart(
        chart_df,
        x="Salary",
        y="Overall_Player_Score",
        size=80
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
            performance_df[column].round(2)
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
        Select any player in the database to view his individual
        offensive, defensive, availability, overall, and salary information.
        """
    )

    player_list = sorted(
        master_df["Player"].dropna().unique()
    )

    selected_player = st.selectbox(
        "Select a player",
        player_list
    )

    player_data = master_df[
        master_df["Player"] == selected_player
    ].iloc[0]

    st.subheader(selected_player)

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

        if player_data["Overall_Player_Score"] >= 60:

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

    st.subheader("Underlying Statistics")


    offense_col, defense_col, availability_col = st.columns(3)


    # -------------------------
    # OFFENSE
    # -------------------------

    with offense_col:

        st.markdown("### 🏀 Offense")

        st.write(
            f"**True Shooting %:** {player_data['TS%']:.3f}"
        )

        st.write(
            f"**Offensive Win Shares:** {player_data['OWS']:.2f}"
        )

        st.write(
            f"**Points Per Game:** {player_data['PPG']:.1f}"
        )

        st.write(
            f"**Assists Per Game:** {player_data['APG']:.1f}"
        )

        st.write(
            f"**Offensive Rebounds/Game:** {player_data['ORPG']:.1f}"
        )


    # -------------------------
    # DEFENSE
    # -------------------------

    with defense_col:

        st.markdown("### 🛡️ Defense")

        st.write(
            f"**Defensive Rebounds/Game:** {player_data['DRPG']:.1f}"
        )

        st.write(
            f"**Steals + Blocks/Game:** {player_data['Steals_Blocks']:.1f}"
        )

        st.write(
            f"**Defensive Win Shares:** {player_data['DWS']:.2f}"
        )


    # -------------------------
    # AVAILABILITY
    # -------------------------

    with availability_col:

        st.markdown("### ⏱️ Availability")

        st.write(
            f"**Games Played:** {player_data['Games_Played']:.0f}"
        )

        st.write(
            f"**Minutes Per Game:** {player_data['Minutes_Per_Game']:.1f}"
        )

        st.write(
            f"**Player Efficiency Rating:** {player_data['PER']:.1f}"
        )


# =========================================================
# TAB 4 — METHODOLOGY
# =========================================================

with tab4:

    st.header("Methodology")

    st.write(
        """
        The model was designed to answer two separate questions:

        **1. How good was the player?**

        **2. How much value did the team receive relative to the player's salary?**
        """
    )

    st.divider()


    # -------------------------
    # 95TH PERCENTILE SYSTEM
    # -------------------------

    st.subheader("1. Statistical Benchmarking")

    st.write(
        """
        Each statistic is compared against the **95th percentile of NBA players**
        in the dataset.

        A statistical score of **100** therefore represents approximately
        95th-percentile NBA performance in that category.

        Players performing above the benchmark can receive scores above 100.
        Individual statistic scores are capped at **115** to prevent one extreme
        statistic from disproportionately controlling an entire category.
        """
    )


    # -------------------------
    # OVS
    # -------------------------

    st.subheader("2. Offensive Value Score — OVS")

    st.write(
        """
        OVS is the average of five offensive components:

        - True Shooting Percentage
        - Offensive Win Shares
        - Points Per Game
        - Assists Per Game
        - Offensive Rebounds Per Game
        """
    )


    # -------------------------
    # DVS
    # -------------------------

    st.subheader("3. Defensive Value Score — DVS")

    st.write(
        """
        DVS is the average of three defensive components:

        - Defensive Rebounds Per Game
        - Steals + Blocks Per Game
        - Defensive Win Shares
        """
    )


    # -------------------------
    # AVS
    # -------------------------

    st.subheader("4. Availability Value Score — AVS")

    st.write(
        """
        AVS evaluates the amount and efficiency of basketball a player
        provides through:

        - Games Played
        - Minutes Per Game
        - Player Efficiency Rating
        """
    )


    # -------------------------
    # PLAYER SCORE
    # -------------------------

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
        The model therefore assigns:

        - **36% weight to offense**
        - **34% weight to defense**
        - **30% weight to availability and efficiency**
        """
    )


    # -------------------------
    # SALARY
    # -------------------------

    st.subheader("6. Salary Per Game")

    st.latex(
        r"""
        Salary\ Per\ Game =
        \frac{Annual\ Salary}{82}
        """
    )


    # -------------------------
    # VALUE SCORE
    # -------------------------

    st.subheader("7. Final Value Score")

    st.write(
        """
        A linear salary denominator would severely penalize superstar players
        because NBA salaries increase much faster than measurable player
        performance.

        To reduce this distortion while still rewarding inexpensive contracts,
        salary is adjusted using an exponent of **0.30**.
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
        Players must have an **Overall Player Score of at least 60**
        to qualify for the main Value Leaderboard.

        This prevents extremely low salaries from causing low-performing
        players to appear artificially valuable.
        """
    )


    # -------------------------
    # DATA
    # -------------------------

    st.subheader("8. Data")

    st.write(
        """
        Player performance is based on **2025–26 NBA statistics**.

        Contract value uses **2026–27 player salary**, allowing the model
        to evaluate future contract cost using the player's most recent
        season of performance.

        Statistical data and contract information were collected from
        Basketball-Reference.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "NBA Player Value Analytics — Independent sports business analytics project"
)
