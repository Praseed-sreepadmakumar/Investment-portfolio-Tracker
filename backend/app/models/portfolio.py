"""SQLAlchemy models for portfolio holdings owned by application users."""

from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String

from app.database.database import Base


class Portfolio(Base):
    """Persist an individual stock holding for a specific authenticated user."""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    purchase_price = Column(Numeric(18, 2), nullable=False)
    last_live_price = Column(Numeric(18, 2), nullable=True)
    purchase_date = Column(Date, default=date.today, nullable=False)