"""
Service factory to create service instances with proper dependencies.
"""

from src.database.database import db_manager
from src.database.repositories.league_repository import LeagueRepository
from src.services.league_service import LeagueService


def get_league_service() -> LeagueService:
    """Create a LeagueService with a fresh DB connection."""
    conn = db_manager.get_connection()
    repo = LeagueRepository(conn)
    return LeagueService(repo)
