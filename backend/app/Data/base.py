"""
Jarvis AIOS
-----------
Data Layer Base Model

Provides the SQLAlchemy DeclarativeBase for all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in Jarvis AIOS."""
    pass
