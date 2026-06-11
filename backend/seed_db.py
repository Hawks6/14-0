import asyncio
import os
import uuid
import sys

# Add the backend directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.player import Season, Franchise, Player, PlayerSeason
from app.models.squad import FranchiseSeason
from app.models.draft import DraftSession, DraftPick
from app.models.match import Match, MatchEvent


async def seed_data():
    async with SessionLocal() as db_session:
        print("Clearing existing tables...")
        await db_session.execute(text("TRUNCATE TABLE draft_picks CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE draft_sessions CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE player_seasons CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE franchise_seasons CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE players CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE franchises CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE seasons CASCADE"))
        await db_session.commit()

        print("Creating Seasons...")
        season_2015 = Season(id=uuid.uuid4(), year=2015, name="IPL 2015")
        season_2016 = Season(id=uuid.uuid4(), year=2016, name="IPL 2016")
        db_session.add_all([season_2015, season_2016])
        
        print("Creating Franchises...")
        dc = Franchise(id=uuid.uuid4(), name="Delhi Capitals", code="DC")
        rcb = Franchise(id=uuid.uuid4(), name="Royal Challengers Bangalore", code="RCB")
        mi = Franchise(id=uuid.uuid4(), name="Mumbai Indians", code="MI")
        db_session.add_all([dc, rcb, mi])
        await db_session.flush()
        
        print("Creating FranchiseSeasons...")
        fs_dc_2015 = FranchiseSeason(id=uuid.uuid4(), franchise_id=dc.id, season_id=season_2015.id)
        fs_rcb_2016 = FranchiseSeason(id=uuid.uuid4(), franchise_id=rcb.id, season_id=season_2016.id)
        fs_mi_2015 = FranchiseSeason(id=uuid.uuid4(), franchise_id=mi.id, season_id=season_2015.id)
        db_session.add_all([fs_dc_2015, fs_rcb_2016, fs_mi_2015])
        
        print("Creating Players and PlayerSeasons...")
        players_data = [
            # DC 2015 Squad
            ("Shreyas Iyer", "India", "BAT", False, 10.0, 90, 5, fs_dc_2015),
            ("Rishabh Pant", "India", "WK", False, 11.0, 95, 5, fs_dc_2015),
            ("Amit Mishra", "India", "BOWL", False, 8.5, 10, 85, fs_dc_2015),
            ("Imran Tahir", "South Africa", "BOWL", True, 9.5, 5, 90, fs_dc_2015),
            ("JP Duminy", "South Africa", "ALLROUNDER", True, 9.0, 80, 70, fs_dc_2015),
            ("Quinton de Kock", "South Africa", "WK", True, 10.5, 92, 5, fs_dc_2015),
            ("Zaheer Khan", "India", "BOWL", False, 9.0, 5, 88, fs_dc_2015),
            ("Shahbaz Nadeem", "India", "BOWL", False, 7.5, 10, 75, fs_dc_2015),
            ("Mayank Agarwal", "India", "BAT", False, 8.0, 82, 5, fs_dc_2015),
            ("Nathan Coulter-Nile", "Australia", "BOWL", True, 8.5, 20, 82, fs_dc_2015),
            ("Yuvraj Singh", "India", "ALLROUNDER", False, 10.5, 85, 60, fs_dc_2015),
            ("Angelo Mathews", "Sri Lanka", "ALLROUNDER", True, 9.5, 80, 75, fs_dc_2015),

            # RCB 2016 Squad
            ("Virat Kohli", "India", "BAT", False, 12.0, 99, 10, fs_rcb_2016),
            ("AB de Villiers", "South Africa", "BAT", True, 11.5, 98, 5, fs_rcb_2016),
            ("Chris Gayle", "West Indies", "BAT", True, 10.5, 95, 20, fs_rcb_2016),
            ("KL Rahul", "India", "WK", False, 10.0, 92, 5, fs_rcb_2016),
            ("Shane Watson", "Australia", "ALLROUNDER", True, 10.5, 88, 85, fs_rcb_2016),
            ("Yuzvendra Chahal", "India", "BOWL", False, 9.5, 5, 92, fs_rcb_2016),
            ("Stuart Binny", "India", "ALLROUNDER", False, 8.0, 70, 65, fs_rcb_2016),
            ("Sreenath Aravind", "India", "BOWL", False, 7.5, 5, 78, fs_rcb_2016),
            ("Varun Aaron", "India", "BOWL", False, 8.0, 5, 80, fs_rcb_2016),
            ("Chris Jordan", "England", "BOWL", True, 8.5, 15, 82, fs_rcb_2016),
            ("Kedar Jadhav", "India", "WK", False, 8.5, 85, 20, fs_rcb_2016),
            ("Iqbal Abdulla", "India", "BOWL", False, 7.5, 15, 75, fs_rcb_2016),

            # MI 2015 Squad
            ("Rohit Sharma", "India", "BAT", False, 11.5, 95, 5, fs_mi_2015),
            ("Kieron Pollard", "West Indies", "ALLROUNDER", True, 10.5, 90, 70, fs_mi_2015),
            ("Lasith Malinga", "Sri Lanka", "BOWL", True, 11.0, 5, 97, fs_mi_2015),
            ("Harbhajan Singh", "India", "BOWL", False, 9.5, 20, 90, fs_mi_2015),
            ("Ambati Rayudu", "India", "WK", False, 9.0, 85, 5, fs_mi_2015),
            ("Lendl Simmons", "West Indies", "BAT", True, 9.5, 88, 10, fs_mi_2015),
            ("Hardik Pandya", "India", "ALLROUNDER", False, 9.5, 88, 80, fs_mi_2015),
            ("Mitchell McClenaghan", "New Zealand", "BOWL", True, 9.0, 10, 88, fs_mi_2015),
            ("Parthiv Patel", "India", "WK", False, 8.5, 82, 5, fs_mi_2015),
            ("Vinay Kumar", "India", "BOWL", False, 8.0, 15, 78, fs_mi_2015),
            ("Jagadeesha Suchith", "India", "BOWL", False, 7.5, 15, 75, fs_mi_2015),
            ("Corey Anderson", "New Zealand", "ALLROUNDER", True, 9.0, 85, 75, fs_mi_2015),
        ]
        
        for name, country, role, is_overseas, cost, bat_pct, bowl_pct, fs in players_data:
            p = Player(id=uuid.uuid4(), name=name, country=country, role=role, is_overseas=is_overseas)
            db_session.add(p)
            await db_session.flush()
            
            ps = PlayerSeason(
                id=uuid.uuid4(),
                player_id=p.id,
                season_id=fs.season_id,
                franchise_id=fs.franchise_id,
                credit_cost=cost,
                percentile_batting=bat_pct,
                percentile_bowling=bowl_pct
            )
            db_session.add(ps)
            
        await db_session.commit()
        print("Database seeded successfully!")
        
async def main():
    await seed_data()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
