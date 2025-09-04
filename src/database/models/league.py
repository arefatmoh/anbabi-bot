"""
League model for community reading leagues.

This module defines the League data model and related functionality.
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from src.config.constants import LeagueStatus


@dataclass
class League:
    """League data model."""
    
    league_id: Optional[int]
    name: str
    description: Optional[str]
    admin_id: int
    current_book_id: Optional[int]
    start_date: date
    end_date: date
    daily_goal: int
    max_members: int
    status: LeagueStatus
    created_at: datetime
    
    def __post_init__(self):
        """Validate league data after initialization."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        
        if self.daily_goal <= 0:
            raise ValueError("Daily goal must be positive")
        
        if self.max_members <= 0:
            raise ValueError("Max members must be positive")
    
    @property
    def duration_days(self) -> int:
        """Calculate league duration in days."""
        # Handle both string and date objects
        if isinstance(self.start_date, str):
            start_date = date.fromisoformat(self.start_date)
        else:
            start_date = self.start_date
            
        if isinstance(self.end_date, str):
            end_date = date.fromisoformat(self.end_date)
        else:
            end_date = self.end_date
            
        return (end_date - start_date).days
    
    @property
    def is_active(self) -> bool:
        """Check if league is currently active."""
        today = date.today()
        
        # Handle both string and date objects
        if isinstance(self.start_date, str):
            start_date = date.fromisoformat(self.start_date)
        else:
            start_date = self.start_date
            
        if isinstance(self.end_date, str):
            end_date = date.fromisoformat(self.end_date)
        else:
            end_date = self.end_date
        
        # For reading leagues, consider active if:
        # 1. Status is ACTIVE
        # 2. We haven't passed the end date yet
        # 3. Start date can be in the future (for registration period)
        return (
            self.status == LeagueStatus.ACTIVE and
            today <= end_date
        )
    
    @property
    def is_full(self) -> bool:
        """Check if league has reached maximum members."""
        # This will be calculated when we implement member counting
        return False
    
    @property
    def progress_percentage(self) -> float:
        """Calculate league progress percentage."""
        if not self.is_active:
            return 100.0 if self.status == LeagueStatus.COMPLETED else 0.0
        
        total_days = self.duration_days
        
        # Handle both string and date objects
        if isinstance(self.start_date, str):
            start_date = date.fromisoformat(self.start_date)
        else:
            start_date = self.start_date
            
        elapsed_days = (date.today() - start_date).days
        
        return min(100.0, max(0.0, (elapsed_days / total_days) * 100))
    
    def to_dict(self) -> Dict:
        """Convert league to dictionary."""
        # Handle date/datetime objects that might be strings from database
        def format_date(date_obj):
            if isinstance(date_obj, str):
                return date_obj
            elif hasattr(date_obj, 'isoformat'):
                return date_obj.isoformat()
            else:
                return str(date_obj)
        
        return {
            'league_id': self.league_id,
            'name': self.name,
            'description': self.description,
            'admin_id': self.admin_id,
            'current_book_id': self.current_book_id,
            'start_date': format_date(self.start_date),
            'end_date': format_date(self.end_date),
            'daily_goal': self.daily_goal,
            'max_members': self.max_members,
            'status': self.status.value,
            'created_at': format_date(self.created_at),
            'duration_days': self.duration_days,
            'is_active': self.is_active,
            'progress_percentage': self.progress_percentage
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'League':
        """Create league from dictionary."""
        return cls(
            league_id=data.get('league_id'),
            name=data['name'],
            description=data.get('description'),
            admin_id=data['admin_id'],
            current_book_id=data.get('current_book_id'),
            start_date=date.fromisoformat(data['start_date']),
            end_date=date.fromisoformat(data['end_date']),
            daily_goal=data['daily_goal'],
            max_members=data['max_members'],
            status=LeagueStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    @classmethod
    def create(
        cls,
        name: str,
        admin_id: int,
        current_book_id: int,
        start_date: date,
        end_date: date,
        daily_goal: int = 20,
        max_members: int = 50,
        description: Optional[str] = None
    ) -> 'League':
        """Create a new league."""
        return cls(
            league_id=None,
            name=name,
            description=description,
            admin_id=admin_id,
            current_book_id=current_book_id,
            start_date=start_date,
            end_date=end_date,
            daily_goal=daily_goal,
            max_members=max_members,
            status=LeagueStatus.ACTIVE,
            created_at=datetime.now()
        )
