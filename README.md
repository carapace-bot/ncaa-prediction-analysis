# NCAA March Madness Prediction Market Analysis

An autonomous research and trading system for NCAA Tournament prediction markets on Polymarket.

## Overview

This repository contains tools and analysis for evaluating NCAA March Madness prediction markets. The system:
- Tracks team performance metrics and historical tournament data
- Analyzes betting markets for mispricings
- Provides data-driven tournament projections
- Monitors market movements and identifies value opportunities

## Features

- **Data Collection**: Automated scraping of team statistics, tournament history, and betting odds
- **Statistical Models**: ELO ratings, strength of schedule, and tournament simulation
- **Market Analysis**: Comparison of model projections vs. market-implied probabilities
- **Position Tracking**: Monitor active positions and performance

## Project Structure

```
ncaa-prediction-analysis/
├── data/              # Raw and processed data
├── src/               # Source code
│   ├── scraping/      # Data collection scripts
│   ├── analysis/      # Statistical models and analysis
│   └── markets/       # Market monitoring and comparison
├── notebooks/         # Jupyter notebooks for exploration
└── output/            # Generated reports and visualizations
```

## Approach

This is a research-first system. Every position taken is backed by:
1. Clear statistical edge vs. market prices
2. Multiple data sources and cross-validation
3. Documented reasoning and assumptions
4. Proper position sizing relative to conviction level

## Data Sources

- Team performance statistics
- Historical tournament results
- Advanced metrics (offensive/defensive efficiency, tempo, etc.)
- Injury reports and roster changes
- Betting market data from multiple sources

## Usage

Scripts and analysis tools are designed to be run independently. Each module includes documentation on inputs, outputs, and methodology.

## Risk Management

All trading follows strict position sizing rules:
- Maximum 5% of bankroll per position
- Positions scaled to conviction level
- Total exposure capped at 40% of bankroll

## License

MIT License - This is public research. Use at your own risk.
