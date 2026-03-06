from pathlib import Path

from sqlalchemy import text

from .database import Base, engine


def run_migrations() -> None:
    if engine.dialect.name != "sqlite":
        Base.metadata.create_all(bind=engine)
        return

    versions_dir = Path(__file__).resolve().parent.parent / "alembic" / "versions"
    files = sorted(versions_dir.glob("*.sql"))
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(64) PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"))
        applied = {row[0] for row in conn.execute(text("SELECT version FROM schema_migrations"))}
        for file in files:
            version = file.stem
            if version in applied:
                continue
            sql = file.read_text(encoding="utf-8")
            for statement in [s.strip() for s in sql.split(";") if s.strip()]:
                conn.execute(text(statement))
            conn.execute(text("INSERT INTO schema_migrations(version) VALUES (:version)"), {"version": version})
