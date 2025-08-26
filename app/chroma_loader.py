# app/chroma_loader.py
import os

USE_CHROMA = os.getenv("USE_CHROMA", "false").lower() == "true"

client = None  # Will be a chromadb.Client or None

def init_chroma():
    global client
    if not USE_CHROMA:
        return None

    # Try to hot-swap sqlite3 with pysqlite3 to satisfy Chroma's >=3.35 requirement
    # Only attempt if import fails or if env CHROMA_FORCE_PYSQLITE3=true
    force_pysqlite3 = os.getenv("CHROMA_FORCE_PYSQLITE3", "true").lower() == "true"
    if force_pysqlite3:
        try:
            __import__("pysqlite3")
            import sys
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
        except Exception:
            # Proceed without swap; Chroma may raise at import if system sqlite3 too old
            pass

    import chromadb
    from chromadb.config import Settings

    # Prefer duckdb+parquet to avoid system sqlite entirely
    impl = os.getenv("CHROMA_DB_IMPL", "duckdb+parquet")
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "/home/site/chroma_data")

    settings = Settings(
        chroma_db_impl=impl,
        persist_directory=persist_dir,
    )
    # For embedded client in‑process:
    client = chromadb.Client(settings)
    return client
