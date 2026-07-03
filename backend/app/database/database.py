"""Database engine, session factory, and lightweight startup initialization."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///./portfolio.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30}
)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)
Base = declarative_base()


def initialize_database() -> None:
    """Create tables and reconcile older SQLite user schemas in place."""
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        inspector = inspect(connection)
        tables = inspector.get_table_names()
        if "users" not in tables:
            return

        columns = {column["name"] for column in inspector.get_columns("users")}

        if "password_hash" not in columns:
            # Older local databases stored the bcrypt hash under `password`.
            connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            if "password" in columns:
                connection.execute(
                    text(
                        "UPDATE users SET password_hash = password WHERE password_hash IS NULL"
                    )
                )

        if "created_at" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
            connection.execute(
                text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            )

        if "portfolios" in tables:
            portfolio_columns = {
                column["name"] for column in inspector.get_columns("portfolios")
            }
            if "last_live_price" not in portfolio_columns:
                connection.execute(
                    text("ALTER TABLE portfolios ADD COLUMN last_live_price NUMERIC(18, 2)")
                )

        # Keep lookups and duplicate checks fast even on upgraded databases.
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)"
            )
        )
        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")
        )


def get_db():
    """Yield a scoped SQLAlchemy session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()