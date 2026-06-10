import uuid
import pytest
from sqlalchemy import text
from app.ingestion.loader import bulk_copy_records

pytestmark = pytest.mark.anyio

async def test_bulk_copy_loader_and_matchups(db_engine):
    """Test that bulk loader function inserts player and season records, 
    and that their schema relationships (matchups) can be correctly queried via joins."""
    
    # Clean slate: Truncate tables using a short-lived transaction on the engine
    async with db_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE player_seasons, players, seasons, franchises CASCADE"))
    
    # 1. Generate unique UUIDs
    season_id = uuid.uuid4()
    franchise_id = uuid.uuid4()
    player_id_1 = uuid.uuid4()
    player_id_2 = uuid.uuid4()
    
    # 2. Insert test seasons
    seasons_columns = ["id", "year", "name"]
    seasons_records = [
        (season_id, 2025, "IPL 2025")
    ]
    await bulk_copy_records(db_engine, "seasons", seasons_columns, seasons_records)
    
    # 3. Insert test franchises
    franchises_columns = ["id", "name", "code"]
    franchises_records = [
        (franchise_id, "Chennai Super Kings", "CSK")
    ]
    await bulk_copy_records(db_engine, "franchises", franchises_columns, franchises_records)
    
    # 4. Insert test players
    players_columns = ["id", "name", "country", "role", "is_overseas"]
    players_records = [
        (player_id_1, "Ruturaj Gaikwad", "India", "BAT", False),
        (player_id_2, "Matheesha Pathirana", "Sri Lanka", "BOWL", True)
    ]
    await bulk_copy_records(db_engine, "players", players_columns, players_records)
    
    # 5. Insert test player season performance metrics
    player_seasons_columns = [
        "id", "player_id", "season_id", "franchise_id", 
        "balls_faced", "runs_scored", "balls_bowled", "wickets_taken",
        "raw_batting_rating", "raw_bowling_rating", 
        "percentile_batting", "percentile_bowling", "credit_cost"
    ]
    ps_id_1 = uuid.uuid4()
    ps_id_2 = uuid.uuid4()
    player_seasons_records = [
        (ps_id_1, player_id_1, season_id, franchise_id, 400, 580, 0, 0, 80.2, 0.0, 90, 50, 11.2),
        (ps_id_2, player_id_2, season_id, franchise_id, 5, 2, 280, 22, 5.0, 92.5, 50, 95, 13.8)
    ]
    await bulk_copy_records(db_engine, "player_seasons", player_seasons_columns, player_seasons_records)
    
    # 6. Query them back using standard SELECT queries with JOINs to verify mapping and relations
    query = text("""
        SELECT 
            p.name, 
            p.country,
            p.role,
            p.is_overseas,
            s.year, 
            f.code, 
            ps.runs_scored, 
            ps.wickets_taken, 
            ps.percentile_batting, 
            ps.percentile_bowling, 
            ps.credit_cost
        FROM player_seasons ps
        JOIN players p ON ps.player_id = p.id
        JOIN seasons s ON ps.season_id = s.id
        JOIN franchises f ON ps.franchise_id = f.id
        ORDER BY p.name ASC
    """)
    
    async with db_engine.connect() as conn:
        result = await conn.execute(query)
        rows = result.fetchall()
    
    assert len(rows) == 2
    
    # Row 1: Matheesha Pathirana
    pathirana = rows[0]
    assert pathirana.name == "Matheesha Pathirana"
    assert pathirana.country == "Sri Lanka"
    assert pathirana.role == "BOWL"
    assert pathirana.is_overseas is True
    assert pathirana.year == 2025
    assert pathirana.code == "CSK"
    assert pathirana.runs_scored == 2
    assert pathirana.wickets_taken == 22
    assert pathirana.percentile_batting == 50
    assert pathirana.percentile_bowling == 95
    assert pathirana.credit_cost == 13.8
    
    # Row 2: Ruturaj Gaikwad
    gaikwad = rows[1]
    assert gaikwad.name == "Ruturaj Gaikwad"
    assert gaikwad.country == "India"
    assert gaikwad.role == "BAT"
    assert gaikwad.is_overseas is False
    assert gaikwad.year == 2025
    assert gaikwad.code == "CSK"
    assert gaikwad.runs_scored == 580
    assert gaikwad.wickets_taken == 0
    assert gaikwad.percentile_batting == 90
    assert gaikwad.percentile_bowling == 50
    assert gaikwad.credit_cost == 11.2
