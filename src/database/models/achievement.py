"""
Achievement model for gamification system.

This module defines the Achievement model and related data structures.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Achievement:
    """Represents a user achievement."""
    
    id: Optional[int]
    user_id: int
    type: str
    title: str
    description: str
    earned_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    is_notified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'earned_at': self.earned_at.isoformat(),
            'metadata': json.dumps(self.metadata) if self.metadata else None,
            'is_notified': self.is_notified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """Create achievement from dictionary."""
        metadata = None
        if data.get('metadata'):
            try:
                metadata = json.loads(data['metadata'])
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            type=data['type'],
            title=data['title'],
            description=data['description'],
            earned_at=datetime.fromisoformat(data['earned_at']),
            metadata=metadata,
            is_notified=bool(data.get('is_notified', False))
        )


@dataclass
class AchievementDefinition:
    """Represents an achievement definition template."""
    
    id: Optional[int]
    type: str
    title: str
    description: str
    icon: str
    xp_reward: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement definition to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'xp_reward': self.xp_reward,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AchievementDefinition':
        """Create achievement definition from dictionary."""
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = None
        
        return cls(
            id=data.get('id'),
            type=data['type'],
            title=data['title'],
            description=data['description'],
            icon=data['icon'],
            xp_reward=data['xp_reward'],
            is_active=bool(data.get('is_active', True)),
            created_at=created_at
        )


@dataclass
class UserStats:
    """Represents user statistics for gamification."""
    
    user_id: int
    current_streak: int = 0
    longest_streak: int = 0
    total_achievements: int = 0
    level: int = 1
    xp: int = 0
    books_completed: int = 0
    total_pages_read: int = 0
    last_reading_date: Optional[datetime] = None
    streak_start_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user stats to dictionary."""
        return {
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_achievements': self.total_achievements,
            'level': self.level,
            'xp': self.xp,
            'books_completed': self.books_completed,
            'total_pages_read': self.total_pages_read,
            'last_reading_date': self.last_reading_date.date().isoformat() if self.last_reading_date else None,
            'streak_start_date': self.streak_start_date.date().isoformat() if self.streak_start_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStats':
        """Create user stats from dictionary."""
        last_reading_date = None
        if data.get('last_reading_date'):
            try:
                last_reading_date = datetime.fromisoformat(data['last_reading_date'])
            except (ValueError, TypeError):
                last_reading_date = None
        
        streak_start_date = None
        if data.get('streak_start_date'):
            try:
                streak_start_date = datetime.fromisoformat(data['streak_start_date'])
            except (ValueError, TypeError):
                streak_start_date = None
        
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = None
        
        updated_at = None
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                updated_at = None
        
        return cls(
            user_id=data['user_id'],
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            total_achievements=data.get('total_achievements', 0),
            level=data.get('level', 1),
            xp=data.get('xp', 0),
            books_completed=data.get('books_completed', 0),
            total_pages_read=data.get('total_pages_read', 0),
            last_reading_date=last_reading_date,
            streak_start_date=streak_start_date,
            created_at=created_at,
            updated_at=updated_at
        )
