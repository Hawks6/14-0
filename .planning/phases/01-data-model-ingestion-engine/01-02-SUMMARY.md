# Phase 1 Plan 2 Summary: Ingestion Pipeline & Bulk Loader

## Changes Made
1. **Created Rating Normalization Pipeline (`backend/app/ingestion/normalizer.py`)**:
   - Implemented `normalize_ratings_pipeline(df, min_threshold)` which calculates season-relative 0-99 percentile ranks for batting and bowling separately.
   - Enforced a 30-ball threshold (assigning a fallback of 50 for sub-threshold players).
   - Applied the exponential scaling cost curve: `credit_cost = 4.0 + (max(percentile_batting, percentile_bowling) / 99.0) ** 1.8 * 11.0` (rounded to 1 decimal place).
2. **Built Raw Data Parser (`backend/app/ingestion/parser.py`)**:
   - Implemented `parse_file_to_dataframe(file_path)` supporting JSON and CSV formats.
   - Leveraged Pydantic validation (`RawPlayerRecord`) to validate dataset records before converting them into pandas DataFrames.
3. **Implemented High-Speed Bulk COPY Loader (`backend/app/ingestion/loader.py`)**:
   - Implemented `bulk_copy_records(db_engine, table_name, columns, records)` to acquire a raw connection from the SQLAlchemy async engine and stream records directly using asyncpg's optimized binary `copy_records_to_table` inside a transaction.

## Verification Results
- Verified imports from both files in the `uv` environment:
  - `uv run python -c "import sys; sys.path.append('.'); from app.ingestion.normalizer import normalize_ratings_pipeline; print('Normalizer imports')"` -> Success (`Normalizer imports`)
  - `uv run python -c "import sys; sys.path.append('.'); from app.ingestion.loader import bulk_copy_records; print('Loader imports')"` -> Success (`Loader imports`)
  - `uv run python -c "import sys; sys.path.append('.'); from app.ingestion.parser import parse_file_to_dataframe; print('Parser imports')"` -> Success (`Parser imports`)
