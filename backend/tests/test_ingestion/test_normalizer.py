import pandas as pd
import numpy as np
from app.ingestion.normalizer import normalize_ratings_pipeline

def test_normalize_ratings_pipeline_thresholds():
    # Construct a dummy DataFrame
    # 2 seasons, some players meeting threshold (>= 30) and some below (< 30)
    data = {
        'player_id': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6'],
        'season_id': ['S1', 'S1', 'S1', 'S2', 'S2', 'S2'],
        'balls_faced': [40, 50, 10, 100, 20, 0],
        'balls_bowled': [10, 60, 0, 0, 80, 5],
        'raw_batting_rating': [10.0, 20.0, 30.0, 15.0, 25.0, 5.0],
        'raw_bowling_rating': [5.0, 15.0, 25.0, 0.0, 12.0, 8.0]
    }
    df = pd.DataFrame(data)
    
    result = normalize_ratings_pipeline(df, min_threshold=30)
    
    # 1. Check fallback for balls_faced < 30
    # P3 has 10 balls faced -> percentile_batting should be 50
    # P5 has 20 balls faced -> percentile_batting should be 50
    # P6 has 0 balls faced -> percentile_batting should be 50
    assert result.loc[result['player_id'] == 'P3', 'percentile_batting'].values[0] == 50
    assert result.loc[result['player_id'] == 'P5', 'percentile_batting'].values[0] == 50
    assert result.loc[result['player_id'] == 'P6', 'percentile_batting'].values[0] == 50
    
    # 2. Check fallback for balls_bowled < 30
    # P1 has 10 balls bowled -> percentile_bowling should be 50
    # P3 has 0 balls bowled -> percentile_bowling should be 50
    # P4 has 0 balls bowled -> percentile_bowling should be 50
    # P6 has 5 balls bowled -> percentile_bowling should be 50
    assert result.loc[result['player_id'] == 'P1', 'percentile_bowling'].values[0] == 50
    assert result.loc[result['player_id'] == 'P3', 'percentile_bowling'].values[0] == 50
    assert result.loc[result['player_id'] == 'P4', 'percentile_bowling'].values[0] == 50
    assert result.loc[result['player_id'] == 'P6', 'percentile_bowling'].values[0] == 50

    # 3. Check relative percentiles within season for those meeting threshold
    # For Season S1:
    # Batting: P1 (40), P2 (50) meet threshold. Raw batting: P1=10.0, P2=20.0.
    # P1 should be rank 1/2 -> pct rank 0.5 -> 0.5 * 99 = 49.5 -> rounded to 50
    # P2 should be rank 2/2 -> pct rank 1.0 -> 1.0 * 99 = 99 -> rounded to 99
    assert result.loc[result['player_id'] == 'P1', 'percentile_batting'].values[0] == 50
    assert result.loc[result['player_id'] == 'P2', 'percentile_batting'].values[0] == 99

    # Bowling: S1 only P2 (60) meets threshold. Raw bowling: P2=15.0.
    # P2 should be rank 1/1 -> pct rank 1.0 -> 99.0
    assert result.loc[result['player_id'] == 'P2', 'percentile_bowling'].values[0] == 99

    # For Season S2:
    # Batting: only P4 (100) meets threshold. Raw batting: 15.0 -> 99
    assert result.loc[result['player_id'] == 'P4', 'percentile_batting'].values[0] == 99

    # Bowling: only P5 (80) meets threshold. Raw bowling: 12.0 -> 99
    assert result.loc[result['player_id'] == 'P5', 'percentile_bowling'].values[0] == 99


def test_credit_cost_calculation():
    # Test cases mapping specific max percentile to credit cost
    # 4.0 + (max_pct / 99.0) ** 1.8 * 11.0
    
    # 1. max_pct = 99 -> cost should be 15.0
    # 2. max_pct = 50 -> cost should be 7.2
    # 3. max_pct = 0 -> cost should be 4.0
    data = {
        'player_id': ['P1', 'P2', 'P3'],
        'season_id': ['S1', 'S1', 'S1'],
        'balls_faced': [30, 30, 30],
        'balls_bowled': [30, 30, 30],
        # To get specific percentiles, let's just use 1 player per season or control the ranks
    }
    df = pd.DataFrame(data)
    
    # Let's mock/test with manually assigned percentiles to test the cost math directly
    # Since normalizer function recalculates them, let's verify using a dataframe that yields those max percentiles
    # For a single player in a season, they are 1/1, so they get 99.
    df1 = pd.DataFrame({
        'season_id': ['S1'],
        'balls_faced': [100],
        'balls_bowled': [100],
        'raw_batting_rating': [10.0],
        'raw_bowling_rating': [10.0]
    })
    res1 = normalize_ratings_pipeline(df1)
    # max_pct = 99 -> cost = 15.0
    assert res1['percentile_batting'].values[0] == 99
    assert res1['percentile_bowling'].values[0] == 99
    assert res1['credit_cost'].values[0] == 15.0

    # For all players failing thresholds, they get 50 percentile.
    df2 = pd.DataFrame({
        'season_id': ['S1'],
        'balls_faced': [0],
        'balls_bowled': [0],
        'raw_batting_rating': [10.0],
        'raw_bowling_rating': [10.0]
    })
    res2 = normalize_ratings_pipeline(df2)
    # max_pct = 50 -> cost = 7.2
    assert res2['percentile_batting'].values[0] == 50
    assert res2['percentile_bowling'].values[0] == 50
    assert res2['credit_cost'].values[0] == 7.2
