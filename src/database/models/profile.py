"""
User profile model for personal information and preferences.

This module defines the UserProfile model and related data structures.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, Any
import json


@dataclass
class UserProfile:
    """Represents a user's profile information."""
    
    user_id: int
    display_name: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    reading_goal_pages_per_day: int = 20
    preferred_reading_time: Optional[str] = None  # e.g., "morning", "evening", "anytime"
    favorite_genres: Optional[str] = None  # JSON string of list
    reading_level: Optional[str] = None  # e.g., "beginner", "intermediate", "advanced"
    privacy_level: str = "public"  # "public", "friends", "private"
    show_achievements: bool = True
    show_reading_stats: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            'user_id': self.user_id,
            'display_name': self.display_name,
            'nickname': self.nickname,
            'bio': self.bio,
            'reading_goal_pages_per_day': self.reading_goal_pages_per_day,
            'preferred_reading_time': self.preferred_reading_time,
            'favorite_genres': self.favorite_genres,
            'reading_level': self.reading_level,
            'privacy_level': self.privacy_level,
            'show_achievements': self.show_achievements,
            'show_reading_stats': self.show_reading_stats,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from dictionary."""
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
            display_name=data.get('display_name'),
            nickname=data.get('nickname'),
            bio=data.get('bio'),
            reading_goal_pages_per_day=data.get('reading_goal_pages_per_day', 20),
            preferred_reading_time=data.get('preferred_reading_time'),
            favorite_genres=data.get('favorite_genres'),
            reading_level=data.get('reading_level'),
            privacy_level=data.get('privacy_level', 'public'),
            show_achievements=bool(data.get('show_achievements', True)),
            show_reading_stats=bool(data.get('show_reading_stats', True)),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class ProfileStatistics:
    """Represents comprehensive user reading statistics."""
    
    user_id: int
    total_books_read: int
    total_pages_read: int
    current_streak: int
    longest_streak: int
    total_reading_days: int
    average_pages_per_day: float
    average_pages_per_book: float
    reading_speed_pages_per_hour: float
    favorite_reading_day: str
    favorite_reading_time: str
    most_productive_month: str
    reading_consistency_score: float  # 0-100
    level: int
    xp: int
    total_achievements: int
    join_date: date
    last_reading_date: Optional[date]
    streak_start_date: Optional[date]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return {
            'user_id': self.user_id,
            'total_books_read': self.total_books_read,
            'total_pages_read': self.total_pages_read,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_reading_days': self.total_reading_days,
            'average_pages_per_day': self.average_pages_per_day,
            'average_pages_per_book': self.average_pages_per_book,
            'reading_speed_pages_per_hour': self.reading_speed_pages_per_hour,
            'favorite_reading_day': self.favorite_reading_day,
            'favorite_reading_time': self.favorite_reading_time,
            'most_productive_month': self.most_productive_month,
            'reading_consistency_score': self.reading_consistency_score,
            'level': self.level,
            'xp': self.xp,
            'total_achievements': self.total_achievements,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'last_reading_date': self.last_reading_date.isoformat() if self.last_reading_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None
        }
