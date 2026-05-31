# etf-performance-automation
-
Project Overview
This project implements an end-to-end quantitative research and data engineering pipeline designed to simulate, clean, and analyze a multi-asset product suite of iShares ETFs: S&P 500 (IVV), MSCI World (URTH), and Core Bond (AGG).
Instead of basic linear tracking, the pipeline models asset price trajectories using Geometric Brownian Motion (GBM) with a log-normal distribution and explicit volatility drag correction (-0.5\sigma^2) to prevent compounding distortions across seed changes.Core Architecture & Features

1. Robust Data Simulation (Geometric Brownian Motion)
Implemented log-returns (\ln) to preserve temporal additivity, converting multiplicative compounding compounding into linear operations.
Integrated Itô calculus drift-correction to ensure simulated asset endpoints match designated annualized targets regardless of random seed variance.

2. Automated QA & Anti-Contamination Data Pipeline
Simulated real-world market data corruption by introducing missing data points (NaN) and an extreme outlier spike (+50% price manipulation) to replicate vendor feed errors.
Engineered a non-contaminating anomaly detection mechanism using a look-back rolling window (3\sigma rule) shifted by t-1 (df.shift(1)). 
This mathematical isolation guarantees that the outlier itself does not poison the rolling mean and standard deviation, preventing structural data leakage.
Automated data healing using a localized forward-fill (ffill) and historical mean interpolation.

3. Financial Analytics & Risk-Adjusted Metrics
Computed precise annualized log-returns and scaled portfolio variance linearly over time (252 trading days).Handled volatility scaling mathematically using the square root of time (\sqrt{252}) to avoid risk overestimation.
Evaluated asset efficiency using the Sharpe Ratio under zero risk-free rate assumptions.

Technical Stack & Competencies Demonstrated
Languages: Python
Data Engineering / Analytics: Pandas, NumPy (Vectorized operations, cumulative statistics, statistical distributions)
Data Visualization: Matplotlib (Production-grade financial reporting charts)
Quantitative Concepts: Geometric Brownian Motion, Volatility Drag, Log-returns, Rolling Statistics (3\sigma Anomaly Detection), Data Leakage/Contamination prevention.
