# 🏀 NBA Player Value Analytics

### Measuring what NBA players produce — and what teams pay for it.

**NBA Player Value Analytics** is an independent sports analytics project designed to answer a simple question:

> **Which NBA players provide the most on-court value relative to what they are being paid?**

Traditional player rankings measure performance. Salary rankings measure cost.

This project connects the two.

Using 2025–26 NBA player performance and 2026–27 salary commitments, I developed a scoring model that evaluates offensive production, defensive impact, availability, overall performance, contract value, and front-office payroll efficiency.

The result is an interactive analytics platform for exploring both **player value** and **organizational spending efficiency**.

## 🌐 Live Website

**[Launch NBA Player Value Analytics](https://nba-player-value-analytics.streamlit.app/)**

---

# The Idea

A player's salary tells us how much a team values him.

His statistics tell us what he produces.

But neither number alone answers the more interesting question:

> **How much basketball performance is a team actually getting for its money?**

That question became the foundation of this project.

Rather than ranking players purely by points, salary, or one advanced statistic, I built a multi-stage model that first evaluates a player's basketball performance independently of salary.

Only after establishing player quality does the model introduce contract cost.

This separates two fundamentally different questions:

1. **How good is the player?**
2. **How valuable is his production relative to his contract?**

---

# 📊 The Player Model

Player performance is divided into three categories:

## 🏀 OVS — Offensive Value Score

OVS evaluates offensive production and efficiency using:

- True Shooting Percentage (TS%)
- Offensive Win Shares (OWS)
- Points Per Game (PPG)
- Assists Per Game (APG)
- Offensive Rebounds Per Game (ORPG)

---

## 🛡️ DVS — Defensive Value Score

DVS evaluates defensive production using:

- Defensive Rebounds Per Game (DRPG)
- Steals + Blocks Per Game
- Defensive Win Shares (DWS)

---

## ⏱️ AVS — Availability Value Score

AVS incorporates a player's ability to remain on the floor and contribute consistently using:

- Games Played
- Minutes Per Game
- Player Efficiency Rating (PER)

---

# 📐 Statistical Normalization

Raw NBA statistics operate on completely different scales.

For example, True Shooting Percentage cannot be directly compared with Points Per Game or Defensive Win Shares.

To solve this, each statistic is benchmarked against the **95th percentile of players in the dataset**.

A normalized score of approximately **100** therefore represents 95th-percentile performance in that statistic.

Individual statistical scores are capped at **115** to prevent an extreme result in one category from disproportionately controlling a player's overall rating.

This creates a common scale across otherwise incomparable statistics.

---

# ⭐ Overall Player Score

OVS, DVS, and AVS are combined into one measure of overall player performance:

```text
Overall Player Score =
0.36(OVS) + 0.34(DVS) + 0.30(AVS)
```

### Model Weights

| Category | Weight |
|---|---:|
| Offensive Value Score | 36% |
| Defensive Value Score | 34% |
| Availability Value Score | 30% |

Salary has **no influence** on Overall Player Score.

This allows the model to evaluate player quality before considering contract cost.

---

# 💰 Contract Value

Once player performance has been established, salary is introduced.

Annual 2026–27 salary is converted into salary per scheduled NBA game:

```text
Salary Per Game = Annual Salary / 82
```

The final contract-value model is:

```text
Final Value Score =
Overall Player Score
/
(Salary Per Game in $100K)^0.30
```

The exponent **α = 0.30** dampens the effect of salary.

Without this adjustment, extremely inexpensive contracts could dominate the rankings simply because they are cheap. The model instead attempts to balance **basketball quality and financial efficiency**.

Players must have an **Overall Player Score of at least 60** to qualify for the primary Value Leaderboard.

This prevents low-performing players on inexpensive contracts from being classified as elite values simply because of their salary.

---

# 💎 Elite Bargains

The model also identifies players who combine elite performance with strong contract value.

To qualify as an **Elite Bargain**, a player must rank in the:

> **80th percentile or higher in overall player performance**

Qualifying players are then ranked by Final Value Score.

This ensures that the bargain analysis rewards inexpensive contracts **without sacrificing player quality**.

---

# 💸 Least Efficient Contracts

The opposite analysis identifies expensive contracts that are not being matched by comparable player performance.

A player qualifies when:

- Salary ranks in the **80th percentile or higher**
- Overall performance ranks **below the 50th percentile**

The model then compares:

```text
Contract Efficiency Gap =
Performance Percentile - Salary Percentile
```

A large negative gap indicates that a player's salary ranking substantially exceeds his performance ranking.

---

# 🏢 Front Office Efficiency

Player value is only one side of roster construction.

The project also asks a broader question:

> **Which NBA front offices are converting payroll into player performance most efficiently?**

For this analysis, players are assigned to the team responsible for their **2026–27 contract**, while their performance is measured using **2025–26 statistics**.

This creates a forward-looking roster construction question:

> Based on what these players most recently produced, how efficiently is each organization allocating its upcoming payroll?

---

# ⏱️ Minutes-Weighted Team Performance

Simply averaging every player's score would give an end-of-bench player the same influence as a starter playing 35 minutes per game.

Instead, team performance is minutes-weighted:

```text
Minutes-Weighted Team Performance =
Σ(Player Score × Minutes Per Game)
/
Σ(Minutes Per Game)
```

Players receiving larger roles therefore have greater influence on the team's performance rating.

---

# 🏦 Front Office Efficiency Gap

Each organization receives both a:

- **Payroll Percentile**
- **Performance Percentile**

Front Office Efficiency is then measured as:

```text
Front Office Efficiency Gap =
Performance Percentile - Payroll Percentile
```

### Interpretation

**Positive Efficiency Gap**

The team's performance ranks higher than its payroll.

→ The organization is generating comparatively strong performance for its spending level.

**Negative Efficiency Gap**

The team's payroll ranks higher than its performance.

→ The organization is spending at a higher level than its player performance would suggest.

This allows teams with very different payrolls to be compared on the same relative scale.

---

# 🔎 Interactive Features

The website contains six major sections:

### 💰 Value Leaderboard
Ranks qualifying NBA players by contract value.

### ⭐ Player Rankings
Ranks players purely by basketball performance, independent of salary.

### 🔎 Player Explorer
Provides an individual breakdown of OVS, DVS, AVS, Overall Player Score, percentiles, salary, contract value, and underlying statistics.

### ⚔️ Player Comparison
Allows any two players in the database to be compared across performance, statistics, salary, and contract value.

### 🏢 Front Office Efficiency
Analyzes organizational payroll allocation through:

- Front Office Efficiency rankings
- Highest and lowest payroll analysis
- Payroll vs. team performance
- Most and least efficient organizations
- Front Office Comparison

### 🧠 Methodology
Explains the model, formulas, assumptions, qualification rules, and limitations.

---

# 🗂️ Data

The model combines:

**2025–26 NBA player performance data**

with

**2026–27 NBA salary and contract-team data**

Player performance statistics were collected from Basketball-Reference, while 2026–27 salary and contract-team data were collected from HoopsHype. These sources were cleaned, matched, and transformed into a structured player-level analytics database.
The final dataset connects each player's most recent performance with the organization responsible for his upcoming contract.

---

# 🛠️ Technology

The project was built using:

- **Python**
- **Pandas** — data cleaning, transformation, aggregation, ranking, and model calculations
- **Altair** — interactive data visualization
- **Streamlit** — interactive web application
- **Google Colab** — data processing and model development
- **GitHub** — version control and project hosting

---

# 🧠 What This Project Explores

Beyond ranking NBA players, this project explores several broader analytics questions:

- How should statistics measured on different scales be combined?
- How can player performance be separated from financial value?
- How much should salary influence a value model?
- How can inexpensive contracts be rewarded without allowing low-performing players to dominate?
- How should player availability influence value?
- How can individual player value be aggregated into organizational efficiency?
- Which teams generate the most performance relative to their spending?
- When does a large payroll represent worthwhile investment versus inefficient allocation?

These questions required choices about **normalization, weighting, thresholds, aggregation, and model design**, rather than simply displaying existing NBA statistics.

---

# ⚠️ Model Limitations

No numerical model can completely describe an NBA player's value.

The current model does not fully capture factors such as:

- Player role and lineup context
- Position-specific responsibilities
- Coaching systems
- Injuries and injury severity
- Playoff performance
- Age and future development
- Contract length and future guarantees
- Leadership and chemistry
- Matchup-specific defensive impact

Defensive performance is particularly difficult to represent using publicly available box-score statistics alone.

For these reasons, NBA Player Value Analytics should be interpreted as an **analytical framework for comparing production, contracts, and payroll efficiency — not a definitive ranking of NBA talent.**

---

# 🚀 Future Development

Potential future versions of the model could incorporate:

- Position-adjusted player value
- Age and development curves
- Multi-year contract analysis
- More advanced defensive metrics
- Expected future performance
- Injury-adjusted availability
- Team success and playoff performance
- Replacement-level player value
- Historical season comparisons

These additions could move the model from evaluating current contract efficiency toward predicting **future player and contract value**.

---

# 🏀 NBA Player Value Analytics

**Performance tells us how good a player is.**

**Salary tells us what he costs.**

**Value comes from understanding both.**

➡️ **[Explore the live analytics platform](https://nba-player-value-analytics.streamlit.app/)**
