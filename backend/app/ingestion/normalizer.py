import pandas as pd
import numpy as np

def normalize_ratings_pipeline(df: pd.DataFrame, min_threshold: int = 30) -> pd.DataFrame:
    """
    Normalizes raw batting and bowling ratings into season-relative 0-99 percentile ranks.
    Applies the min_threshold constraint (default 30 balls). Players below the threshold 
    get a baseline percentile of 50.
    Computes player credit costs based on an exponential scaling curve.
    """
    df = df.copy()
    
    # Initialize percentiles to baseline
    df['percentile_batting'] = 50
    df['percentile_bowling'] = 50
    
    # Batting percentile rank calculation for players meeting the threshold
    bat_mask = df['balls_faced'] >= min_threshold
    if bat_mask.any():
        df.loc[bat_mask, 'percentile_batting'] = (
            df[bat_mask]
            .groupby('season_id')['raw_batting_rating']
            .transform('rank', pct=True)
            .mul(99)
            .round()
            .astype(int)
        )
        
    # Bowling percentile rank calculation for players meeting the threshold
    bowl_mask = df['balls_bowled'] >= min_threshold
    if bowl_mask.any():
        df.loc[bowl_mask, 'percentile_bowling'] = (
            df[bowl_mask]
            .groupby('season_id')['raw_bowling_rating']
            .transform('rank', pct=True)
            .mul(99)
            .round()
            .astype(int)
        )
        
    # Compute credit cost: adjusted to bring average cost down to ~8.0 so teams can be drafted within 100 limit.
    max_pct = np.maximum(df['percentile_batting'], df['percentile_bowling'])
    df['credit_cost'] = 4.5 + (max_pct / 99.0) ** 2.5 * 7.5
    df['credit_cost'] = df['credit_cost'].round(1)
    
    return df
