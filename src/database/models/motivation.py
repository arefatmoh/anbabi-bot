"""
Motivation model for gamification system.

This module defines the MotivationMessage model and related data structures.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class MotivationMessage:
    """Represents a motivation message sent to a user."""
    
    id: Optional[int]
    user_id: int
    message_type: str
    content: str
    sent_at: datetime
    is_read: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert motivation message to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message_type': self.message_type,
            'content': self.content,
            'sent_at': self.sent_at.isoformat(),
            'is_read': self.is_read,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MotivationMessage':
        """Create motivation message from dictionary."""
        metadata = None
        if data.get('metadata'):
            try:
                metadata = json.loads(data['metadata'])
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            message_type=data['message_type'],
            content=data['content'],
            sent_at=datetime.fromisoformat(data['sent_at']),
            is_read=bool(data.get('is_read', False)),
            metadata=metadata
        )


@dataclass
class VisualElement:
    """Represents a visual element (progress bar, badge, certificate)."""
    
    id: Optional[int]
    user_id: int
    element_type: str
    data: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert visual element to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'element_type': self.element_type,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualElement':
        """Create visual element from dictionary."""
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'])
            except (ValueError, TypeError):
                expires_at = None
        
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            element_type=data['element_type'],
            data=data['data'],
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=expires_at,
            is_active=bool(data.get('is_active', True))
        )


# Message types for motivation system
class MessageType:
    """Constants for motivation message types."""
    
    # Achievement messages
    ACHIEVEMENT_EARNED = "achievement_earned"
    STREAK_MILESTONE = "streak_milestone"
    BOOK_COMPLETED = "book_completed"
    
    # Progress messages
    DAILY_GOAL_REACHED = "daily_goal_reached"
    WEEKLY_PROGRESS = "weekly_progress"
    MONTHLY_SUMMARY = "monthly_summary"
    
    # Encouragement messages
    DAILY_MOTIVATION = "daily_motivation"
    STREAK_REMINDER = "streak_reminder"
    COMEBACK_MESSAGE = "comeback_message"
    
    # Social messages
    LEAGUE_UPDATE = "league_update"
    FRIEND_ACHIEVEMENT = "friend_achievement"
    COMMUNITY_CHALLENGE = "community_challenge"


# Visual element types
class VisualElementType:
    """Constants for visual element types."""
    
    PROGRESS_BAR = "progress_bar"
    ACHIEVEMENT_BADGE = "achievement_badge"
    CERTIFICATE = "certificate"
    LEVEL_INDICATOR = "level_indicator"
    STREAK_DISPLAY = "streak_display"
