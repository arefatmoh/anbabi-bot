"""
Admin tools for Read & Revive Bot.

This module provides administrative utilities for data export, system monitoring, and management.
"""

import pandas as pd
from datetime import datetime
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.database.database import db_manager


class AdminTools:
    """Administrative tools for bot management."""
    
    def __init__(self):
        """Initialize admin tools."""
        self.db_manager = db_manager
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export all reading data to Excel file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reading_data_{timestamp}.xlsx"
        
        try:
            # Get all data from database
            data = self._get_all_data()
            
            if not data:
                return "No data to export"
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Reading_Data', index=False)
                
                # Summary statistics sheet
                summary_data = self._create_summary_data()
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
                
                # User statistics sheet
                user_stats = self._create_user_statistics()
                user_stats_df = pd.DataFrame(user_stats)
                user_stats_df.to_excel(writer, sheet_name='User_Statistics', index=False)
            
            return f"Data exported successfully to {filename}"
            
        except Exception as e:
            return f"Error exporting data: {str(e)}"
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export all reading data to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reading_data_{timestamp}.csv"
        
        try:
            data = self._get_all_data()
            
            if not data:
                return "No data to export"
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            
            return f"Data exported successfully to {filename}"
            
        except Exception as e:
            return f"Error exporting data: {str(e)}"
    
    def _get_all_data(self) -> list:
        """Get all reading data from database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        u.username, u.full_name, u.city,
                        b.title, b.author, b.total_pages,
                        ub.pages_read, ub.start_date, ub.last_updated,
                        rs.session_date, rs.pages_read as session_pages,
                        rs.reading_time_minutes
                    FROM users u
                    LEFT JOIN user_books ub ON u.user_id = ub.user_id
                    LEFT JOIN books b ON ub.book_id = b.book_id
                    LEFT JOIN reading_sessions rs ON ub.id = rs.user_id
                    WHERE u.is_active = 1
                    ORDER BY u.full_name, b.title, rs.session_date
                """)
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"Error getting data: {e}")
            return []
    
    def _create_summary_data(self) -> list:
        """Create summary statistics data."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total users
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                total_users = cursor.fetchone()[0]
                
                # Total books
                cursor.execute("SELECT COUNT(*) FROM books")
                total_books = cursor.fetchone()[0]
                
                # Total reading sessions
                cursor.execute("SELECT COUNT(*) FROM reading_sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Total pages read
                cursor.execute("SELECT SUM(pages_read) FROM user_books")
                total_pages = cursor.fetchone()[0] or 0
                
                # Active readers (users with reading sessions in last 30 days)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM reading_sessions 
                    WHERE session_date >= DATE('now', '-30 days')
                """)
                active_readers = cursor.fetchone()[0]
                
                return [{
                    'metric': 'Total Users',
                    'value': total_users,
                    'description': 'Active registered users'
                }, {
                    'metric': 'Total Books',
                    'value': total_books,
                    'description': 'Books in the system'
                }, {
                    'metric': 'Total Sessions',
                    'value': total_sessions,
                    'description': 'Reading sessions recorded'
                }, {
                    'metric': 'Total Pages Read',
                    'value': total_pages,
                    'description': 'Cumulative pages read'
                }, {
                    'metric': 'Active Readers',
                    'value': active_readers,
                    'description': 'Users active in last 30 days'
                }]
                
        except Exception as e:
            return [{'metric': 'Error', 'value': str(e), 'description': 'Failed to get data'}]
    
    def _create_user_statistics(self) -> list:
        """Create user-specific statistics."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        u.full_name,
                        COUNT(DISTINCT ub.book_id) as books_started,
                        SUM(ub.pages_read) as total_pages,
                        COUNT(rs.id) as total_sessions,
                        MAX(rs.session_date) as last_activity
                    FROM users u
                    LEFT JOIN user_books ub ON u.user_id = ub.user_id
                    LEFT JOIN reading_sessions rs ON u.user_id = rs.user_id
                    WHERE u.is_active = 1
                    GROUP BY u.user_id, u.full_name
                    ORDER BY total_pages DESC
                """)
                
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_system_health(self) -> dict:
        """Get system health information."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_mb = (page_count * page_size) / (1024 * 1024)
                
                # Table row counts
                tables = ['users', 'books', 'user_books', 'reading_sessions', 'achievements']
                table_counts = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM reading_sessions 
                    WHERE session_date >= DATE('now', '-7 days')
                """)
                weekly_activity = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM reading_sessions 
                    WHERE session_date >= DATE('now', '-24 hours')
                """)
                daily_activity = cursor.fetchone()[0]
                
                return {
                    'database_size_mb': round(db_size_mb, 2),
                    'table_counts': table_counts,
                    'weekly_activity': weekly_activity,
                    'daily_activity': daily_activity,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> str:
        """Clean up old reading sessions data."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count records to be deleted
                cursor.execute("""
                    SELECT COUNT(*) FROM reading_sessions 
                    WHERE session_date < DATE('now', '-{} days')
                """.format(days_to_keep))
                
                records_to_delete = cursor.fetchone()[0]
                
                if records_to_delete == 0:
                    return "No old data to clean up"
                
                # Delete old records
                cursor.execute("""
                    DELETE FROM reading_sessions 
                    WHERE session_date < DATE('now', '-{} days')
                """.format(days_to_keep))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return f"Cleaned up {deleted_count} old reading session records"
                
        except Exception as e:
            return f"Error cleaning up data: {str(e)}"


def main():
    """Test admin tools functionality."""
    admin = AdminTools()
    
    print("🔧 Admin Tools Test")
    print("=" * 50)
    
    # Test system health
    health = admin.get_system_health()
    print("📊 System Health:")
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Test data export
    print("📤 Testing data export...")
    result = admin.export_to_excel("test_export.xlsx")
    print(f"Result: {result}")
    
    # Clean up test file
    if os.path.exists("test_export.xlsx"):
        os.remove("test_export.xlsx")
        print("🧹 Test file cleaned up")


if __name__ == "__main__":
    main()
