import os

def init_chroma():
    # Only called when USE_CHROMA=true
    import chromadb
    from chromadb.config import Settings
    settings = Settings(
        chroma_db_impl=os.getenv("CHROMA_DB_IMPL", "duckdb+parquet"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIR", "/home/site/chroma_data"),
    )
    return chromadb.Client(settings)
