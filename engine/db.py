"""
Persistent database module for IPC to BNS mapping system using SQLite.

Provides database operations including initialization, CRUD operations,
import/export functionality, and migration from JSON.
"""

import sqlite3
import json
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DB_FILE = os.path.join(_base_dir, "mapping_db.sqlite")
_JSON_FILE = os.path.join(_base_dir, "mapping_db.json")

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(_DB_FILE)

def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create mappings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mappings (
            ipc_section TEXT PRIMARY KEY,
            bns_section TEXT NOT NULL,
            notes TEXT,
            source TEXT,
            category TEXT
        )
    ''')

    # Create metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()

def migrate_from_json():
    """Migrate existing JSON data to database on first run."""
    if not os.path.exists(_JSON_FILE):
        return

    if os.path.exists(_DB_FILE):
        # Already migrated
        return

    initialize_db()

    try:
        with open(_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert metadata
        metadata = data.pop('_metadata', {})
        for key, value in metadata.items():
            cursor.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )

        # Insert mappings
        for ipc_section, mapping in data.items():
            cursor.execute('''
                INSERT INTO mappings (ipc_section, bns_section, notes, source, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ipc_section,
                mapping.get('bns_section', ''),
                mapping.get('notes', ''),
                mapping.get('source', ''),
                mapping.get('category', '')
            ))

        conn.commit()
        conn.close()

        print(f"Successfully migrated {len(data)} mappings from JSON to database.")

    except Exception as e:
        print(f"Error during migration: {e}")

def insert_mapping(ipc_section: str, bns_section: str, notes: str = "",
                  source: str = "user", category: str = "User Added") -> bool:
    """Insert a single mapping into the database.

    Returns True if successful, False if duplicate or error.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO mappings (ipc_section, bns_section, notes, source, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (ipc_section, bns_section, notes, source, category))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        # Duplicate ipc_section
        return False
    except Exception as e:
        print(f"Error inserting mapping: {e}")
        return False

def get_mapping(ipc_section: str) -> Optional[Dict]:
    """Get a single mapping by IPC section."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings WHERE ipc_section = ?", (ipc_section,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'ipc_section': row[0],
                'bns_section': row[1],
                'notes': row[2],
                'source': row[3],
                'category': row[4]
            }
        return None

    except Exception as e:
        print(f"Error getting mapping: {e}")
        return None

def get_all_mappings() -> Dict[str, Dict]:
    """Get all mappings as a dictionary."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings")
        rows = cursor.fetchall()
        conn.close()

        mappings = {}
        for row in rows:
            mappings[row[0]] = {
                'bns_section': row[1],
                'notes': row[2],
                'source': row[3],
                'category': row[4]
            }
        return mappings

    except Exception as e:
        print(f"Error getting all mappings: {e}")
        return {}

def get_mappings_by_category(category: str) -> Dict[str, Dict]:
    """Get mappings by category."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mappings WHERE category = ?", (category,))
        rows = cursor.fetchall()
        conn.close()

        mappings = {}
        for row in rows:
            mappings[row[0]] = {
                'bns_section': row[1],
                'notes': row[2],
                'source': row[3],
                'category': row[4]
            }
        return mappings

    except Exception as e:
        print(f"Error getting mappings by category: {e}")
        return {}

def get_categories() -> List[str]:
    """Get all unique categories."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT category FROM mappings")
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows if row[0]]

    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

def get_mapping_count() -> int:
    """Get total number of mappings."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM mappings")
        count = cursor.fetchone()[0]
        conn.close()

        return count

    except Exception as e:
        print(f"Error getting mapping count: {e}")
        return 0

def get_metadata() -> Dict:
    """Get metadata from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT key, value FROM metadata")
        rows = cursor.fetchall()
        conn.close()

        metadata = {}
        for key, value in rows:
            try:
                metadata[key] = json.loads(value)
            except:
                metadata[key] = value
        return metadata

    except Exception as e:
        print(f"Error getting metadata: {e}")
        return {}

def import_mappings_from_csv(file_path: str) -> Tuple[int, List[str]]:
    """Import mappings from CSV file.

    Returns (success_count, error_messages).
    Expected CSV columns: ipc_section, bns_section, notes, source, category
    """
    errors = []
    success_count = 0

    try:
        df = pd.read_csv(file_path)

        # Validate required columns
        required_cols = ['ipc_section', 'bns_section']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return 0, errors

        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
                ipc_section = str(row['ipc_section']).strip()
                bns_section = str(row['bns_section']).strip()
                notes = str(row.get('notes', '')).strip()
                source = str(row.get('source', 'imported')).strip()
                category = str(row.get('category', 'Imported')).strip()

                cursor.execute('''
                    INSERT OR REPLACE INTO mappings
                    (ipc_section, bns_section, notes, source, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ipc_section, bns_section, notes, source, category))

                success_count += 1

            except Exception as e:
                errors.append(f"Error importing row {len(errors) + success_count + 1}: {e}")

        conn.commit()
        conn.close()

    except Exception as e:
        errors.append(f"Error reading CSV file: {e}")

    return success_count, errors

def import_mappings_from_excel(file_path: str) -> Tuple[int, List[str]]:
    """Import mappings from Excel file.

    Returns (success_count, error_messages).
    Expected columns: ipc_section, bns_section, notes, source, category
    """
    errors = []
    success_count = 0

    try:
        df = pd.read_excel(file_path)

        # Validate required columns
        required_cols = ['ipc_section', 'bns_section']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return 0, errors

        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
                ipc_section = str(row['ipc_section']).strip()
                bns_section = str(row['bns_section']).strip()
                notes = str(row.get('notes', '')).strip()
                source = str(row.get('source', 'imported')).strip()
                category = str(row.get('category', 'Imported')).strip()

                cursor.execute('''
                    INSERT OR REPLACE INTO mappings
                    (ipc_section, bns_section, notes, source, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ipc_section, bns_section, notes, source, category))

                success_count += 1

            except Exception as e:
                errors.append(f"Error importing row {len(errors) + success_count + 1}: {e}")

        conn.commit()
        conn.close()

    except Exception as e:
        errors.append(f"Error reading Excel file: {e}")

    return success_count, errors

def export_mappings_to_json(file_path: str) -> bool:
    """Export all mappings to JSON file."""
    try:
        mappings = get_all_mappings()
        metadata = get_metadata()

        data = {"_metadata": metadata}
        data.update(mappings)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False

def export_mappings_to_csv(file_path: str) -> bool:
    """Export all mappings to CSV file."""
    try:
        mappings = get_all_mappings()

        data = []
        for ipc_section, mapping in mappings.items():
            data.append({
                'ipc_section': ipc_section,
                'bns_section': mapping['bns_section'],
                'notes': mapping['notes'],
                'source': mapping['source'],
                'category': mapping['category']
            })

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        return True

    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

# Initialize database on import
initialize_db()
migrate_from_json()
