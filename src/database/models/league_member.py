"""
League member model for community reading leagues.

This module defines the LeagueMember data model and related functionality.
"""

from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class LeagueMember:
    """League member data model."""
    
    league_id: int
    user_id: int
    joined_at: datetime
    is_active: bool
    
    def to_dict(self) -> Dict:
        """Convert league member to dictionary."""
        return {
            'league_id': self.league_id,
            'user_id': self.user_id,
            'joined_at': self.joined_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LeagueMember':
        """Create league member from dictionary."""
        return cls(
            league_id=data['league_id'],
            user_id=data['user_id'],
            joined_at=datetime.fromisoformat(data['joined_at']),
            is_active=data['is_active']
        )
    
    @classmethod
    def create(cls, league_id: int, user_id: int) -> 'LeagueMember':
        """Create a new league member."""
        return cls(
            league_id=league_id,
            user_id=user_id,
            joined_at=datetime.now(),
            is_active=True
        )
