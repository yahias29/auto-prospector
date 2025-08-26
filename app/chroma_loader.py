# app/chroma_loader.py
import os

USE_CHROMA = os.getenv("USE_CHROMA", "false").lower() == "true"

client = None

def init_chroma():
    global client
    if not USE_CHROMA:
        return None

    # Optional shim if later enabling sqlite-backed modes
    if os.getenv("CHROMA_FORCE_PYSQLITE3", "true").lower() == "true":
        try:
            __import__("pysqlite3")
            import sys
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
        except Exception:
            pass

    import chromadb
    from chromadb.config import Settings
    settings = Settings(
        chroma_db_impl=os.getenv("CHROMA_DB_IMPL", "duckdb+parquet"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIR", "/home/site/chroma_data"),
    )
    client = chromadb.Client(settings)
    return client
