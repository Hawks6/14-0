import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional

class RawPlayerRecord(BaseModel):
    name: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    role: str = Field(..., min_length=2)  # e.g., BAT, BOWL, ALLROUNDER, WK
    is_overseas: bool
    season_year: int
    season_name: str = Field(..., min_length=1)
    franchise_name: str = Field(..., min_length=1)
    franchise_code: str = Field(..., min_length=1)
    balls_faced: int = 0
    runs_scored: int = 0
    balls_bowled: int = 0
    wickets_taken: int = 0
    raw_batting_rating: float = 0.0
    raw_bowling_rating: float = 0.0

def parse_file_to_dataframe(file_path: str) -> pd.DataFrame:
    """
    Parses a CSV or JSON file into a pandas DataFrame, validating each row 
    against the RawPlayerRecord Pydantic model.
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format. Must be CSV or JSON.")
        
    records = df.to_dict(orient='records')
    validated_records = []
    for record in records:
        # Validate and dump back to dict
        validated = RawPlayerRecord(**record)
        validated_records.append(validated.model_dump())
        
    return pd.DataFrame(validated_records)
