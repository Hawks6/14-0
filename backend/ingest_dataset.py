import asyncio
import os
import sys
import uuid
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Add the backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.models.draft import DraftSession, DraftPick
from app.models.match import Match, MatchEvent

def preprocess_csv(file_path):
    df = pd.read_csv(file_path)
    
    # Map roles
    role_map = {
        'Opener': 'BAT',
        'Batter': 'BAT',
        'Batter (C)': 'BAT',
        'Opener (C)': 'BAT',
        'WK-Batter': 'WK',
        'WK-Batter (C)': 'WK',
        'All-rounder': 'ALLROUNDER',
        'All-rounder (C)': 'ALLROUNDER',
        'Bowler': 'BOWL',
        'Bowler (C)': 'BOWL'
    }
    # drop rows where role is NaN
    df = df.dropna(subset=['Role', 'Player', 'Team'])
    
    # Drop duplicates to prevent uq_player_season_franchise violations
    df = df.drop_duplicates(subset=['Player', 'Season', 'Team'])
    
    df['role'] = df['Role'].map(role_map).fillna('BAT')
    
    df['is_overseas'] = df['Nationality'] != 'Indian'
    df['name'] = df['Player']
    df['country'] = df['Nationality'].fillna('Unknown')
    
    df['season_year'] = df['Season'].astype(int)
    df['season_name'] = "IPL " + df['Season'].astype(str)
    
    df['franchise_name'] = df['Team']
    def get_code(team_name):
        code = "".join([word[0] for word in str(team_name).split()]).upper()
        # Handled explicitly to prevent collisions
        overrides = {
            "Deccan Chargers": "DEC",
            "Delhi Capitals": "DC",
            "Delhi Daredevils": "DD",
            "Punjab Kings": "PBKS",
            "Kings XI Punjab": "KXIP",
            "Sunrisers Hyderabad": "SRH",
            "Rising Pune Supergiant": "RPS",
            "Rising Pune Supergiants": "RPS2",
            "Gujarat Lions": "GL",
            "Gujarat Titans": "GT",
            "Lucknow Super Giants": "LSG",
            "Royal Challengers Bengaluru": "RCBB"
        }
        return overrides.get(team_name, code)
    
    df['franchise_code'] = df['Team'].apply(get_code)
    
    df['balls_faced'] = df['role'].apply(lambda r: 50 if r in ['BAT', 'WK', 'ALLROUNDER'] else 0)
    df['balls_bowled'] = df['role'].apply(lambda r: 50 if r in ['BOWL', 'ALLROUNDER'] else 0)
    
    df['raw_batting_rating'] = df.apply(lambda row: row['Season_Rating'] if row['role'] in ['BAT', 'WK', 'ALLROUNDER'] else 0, axis=1)
    df['raw_bowling_rating'] = df.apply(lambda row: row['Season_Rating'] if row['role'] in ['BOWL', 'ALLROUNDER'] else 0, axis=1)
    
    df['runs_scored'] = 0
    df['wickets_taken'] = 0

    return df

def normalize_ratings(df):
    df = df.copy()
    
    # In this dataset, Season_Rating is roughly the percentile. 
    # Let's map it directly to percentile, or re-calculate it based on group.
    # The normalizer in app/ingestion/normalizer.py does this:
    df['percentile_batting'] = 50
    df['percentile_bowling'] = 50
    
    bat_mask = df['balls_faced'] >= 30
    if bat_mask.any():
        df.loc[bat_mask, 'percentile_batting'] = (
            df[bat_mask]
            .groupby('season_year')['raw_batting_rating']
            .transform('rank', pct=True)
            .mul(99)
            .round()
            .astype(int)
        )
        
    bowl_mask = df['balls_bowled'] >= 30
    if bowl_mask.any():
        df.loc[bowl_mask, 'percentile_bowling'] = (
            df[bowl_mask]
            .groupby('season_year')['raw_bowling_rating']
            .transform('rank', pct=True)
            .mul(99)
            .round()
            .astype(int)
        )
        
    # Override percentile with Season_Rating directly for simplicity and accuracy based on Prime_Rating / Season_Rating
    df.loc[bat_mask, 'percentile_batting'] = df.loc[bat_mask, 'Season_Rating'].astype(int)
    df.loc[bowl_mask, 'percentile_bowling'] = df.loc[bowl_mask, 'Season_Rating'].astype(int)

    max_pct = np.maximum(df['percentile_batting'], df['percentile_bowling'])
    df['credit_cost'] = 4.5 + (max_pct / 99.0) ** 2.5 * 7.5
    df['credit_cost'] = df['credit_cost'].round(1)
    
    return df

async def ingest_data(file_path: str):
    print(f"Reading dataset from {file_path}")
    df = preprocess_csv(file_path)
    print(f"Loaded {len(df)} records. Normalizing data...")
    df = normalize_ratings(df)
    
    async with SessionLocal() as db_session:
        print("Clearing existing tables (draft picks, sessions, player/franchise seasons, players, franchises, seasons)...")
        await db_session.execute(text("TRUNCATE TABLE draft_picks CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE draft_sessions CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE player_seasons CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE franchise_seasons CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE players CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE franchises CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE seasons CASCADE"))
        await db_session.commit()

        # 1. Seasons
        print("Inserting Seasons...")
        seasons_df = df[['season_year', 'season_name']].drop_duplicates()
        season_map = {}
        for _, row in seasons_df.iterrows():
            season = Season(id=uuid.uuid4(), year=row['season_year'], name=row['season_name'])
            db_session.add(season)
            season_map[row['season_year']] = season.id
        await db_session.flush()

        # 2. Franchises
        print("Inserting Franchises...")
        franchises_df = df[['franchise_name', 'franchise_code']].drop_duplicates()
        franchise_map = {}
        for _, row in franchises_df.iterrows():
            franchise = Franchise(id=uuid.uuid4(), name=row['franchise_name'], code=row['franchise_code'])
            db_session.add(franchise)
            franchise_map[row['franchise_code']] = franchise.id
        await db_session.flush()

        # 3. FranchiseSeasons
        print("Inserting FranchiseSeasons...")
        fs_df = df[['franchise_code', 'season_year']].drop_duplicates()
        fs_map = {}
        for _, row in fs_df.iterrows():
            fs = FranchiseSeason(
                id=uuid.uuid4(),
                franchise_id=franchise_map[row['franchise_code']],
                season_id=season_map[row['season_year']]
            )
            db_session.add(fs)
            fs_map[(row['franchise_code'], row['season_year'])] = fs.id
        await db_session.flush()

        # 4. Players
        print("Inserting Players...")
        players_df = df[['name', 'country', 'role', 'is_overseas']].drop_duplicates(subset=['name', 'country'])
        player_map = {}
        for _, row in players_df.iterrows():
            player = Player(
                id=uuid.uuid4(),
                name=row['name'],
                country=row['country'],
                role=row['role'],
                is_overseas=bool(row['is_overseas'])
            )
            db_session.add(player)
            player_map[(row['name'], row['country'])] = player.id
        await db_session.flush()

        # 5. PlayerSeasons
        print("Inserting PlayerSeasons...")
        ps_list = []
        for _, row in df.iterrows():
            ps = PlayerSeason(
                id=uuid.uuid4(),
                player_id=player_map[(row['name'], row['country'])],
                season_id=season_map[row['season_year']],
                franchise_id=franchise_map[row['franchise_code']],
                balls_faced=int(row['balls_faced']),
                runs_scored=int(row['runs_scored']),
                balls_bowled=int(row['balls_bowled']),
                wickets_taken=int(row['wickets_taken']),
                raw_batting_rating=float(row['raw_batting_rating']),
                raw_bowling_rating=float(row['raw_bowling_rating']),
                percentile_batting=int(row['percentile_batting']),
                percentile_bowling=int(row['percentile_bowling']),
                credit_cost=float(row['credit_cost']),
                prime_rating=int(row['Prime_Rating']) if pd.notnull(row.get('Prime_Rating')) else 50,
                season_rating=int(row['Season_Rating']) if pd.notnull(row.get('Season_Rating')) else 50
            )
            ps_list.append(ps)
        db_session.add_all(ps_list)
        await db_session.commit()
        print(f"Database seeded successfully with {len(ps_list)} player seasons!")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_dataset.py <path_to_csv>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    await ingest_data(file_path)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
