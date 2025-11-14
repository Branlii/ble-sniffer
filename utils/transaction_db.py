import sqlite3
from pathlib import Path
from datetime import datetime

class TransactionDB:
    def __init__(self, db_path='transactions.db', schema_path=None):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.session_id = None
        
        if schema_path is None:
            schema_path = Path(__file__).parent / 'transaction_schema.sql'
        with open(schema_path, 'r') as f:
            schema = f.read()
        self.cursor.executescript(schema)
        self.conn.commit()
        
        # Create a new session on initialization
        self.create_session()

    def create_session(self):
        """Create a new session for this program run."""
        start_timestamp = datetime.now().isoformat()
        self.cursor.execute(
            'INSERT INTO session (start_timestamp) VALUES (?)',
            (start_timestamp,)
        )
        self.conn.commit()
        self.session_id = self.cursor.lastrowid
        return self.session_id

    def end_session(self):
        """Mark the current session as ended."""
        if self.session_id:
            end_timestamp = datetime.now().isoformat()
            self.cursor.execute(
                'UPDATE session SET end_timestamp = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (end_timestamp, self.session_id)
            )
            self.conn.commit()

    def add_transaction(self, timestamp, device_id, device_info):
        """Add a transaction with device information.
        
        Args:
            timestamp: ISO 8601 formatted timestamp
            device_id: Device MAC address
            device_info: Dictionary containing device information
        """
        if self.session_id is None:
            raise RuntimeError("No active session. Call create_session() first.")
        
        import json
        self.cursor.execute(
            'INSERT INTO transactions (session_id, timestamp, device_id, data) VALUES (?, ?, ?, ?)',
            (self.session_id, timestamp, device_id, json.dumps(device_info))
        )
        self.conn.commit()

    def add_scan_report(self, scan_timestamp, device_count, merged_device_count):
        """Add a scan report with device counts
        
        Args:
            scan_timestamp: Timestamp of the scan
            device_count: Total number of active signals (unmerged)
            merged_device_count: Number of merged/logical devices
        """
        if self.session_id is None:
            raise RuntimeError("No active session. Call create_session() first.")
        self.cursor.execute(
            'INSERT INTO report (session_id, scan_timestamp, device_count, merged_device_count) VALUES (?, ?, ?, ?)',
            (self.session_id, scan_timestamp, device_count, merged_device_count)
        )
        self.conn.commit()

    def close(self):
        """Close the database connection and end the session."""
        self.end_session()
        self.conn.close()
