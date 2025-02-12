# database.py

import sqlite3
import os

from colorama import Fore, Style

def create_project_database(db_file):
    """
    For SQLite, simply check if the database file exists. Connecting to it will create it if not.
    """
    if os.path.exists(db_file):
        print(f"{Fore.YELLOW}Database '{db_file}' already exists.{Style.RESET_ALL}")
    else:
        # Creating the file by connecting to it.
        conn = sqlite3.connect(db_file)
        conn.close()
        print(f"{Fore.GREEN}Database '{db_file}' created successfully.{Style.RESET_ALL}")

def initialize_project_schema(db_file):
    """
    Connects to the specified SQLite database file and initializes the schema for a book project.
    Creates tables for projects, chapters, and feedback if they don't already exist,
    and adds missing columns if necessary.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table for projects if it doesn't exist.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        setting TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Ensure 'status' column exists.
    cursor.execute("PRAGMA table_info(projects);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    if "status" not in column_names:
        print(f"{Fore.YELLOW}Adding 'status' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'in_progress';")
    # Ensure 'outline' column exists.
    if "outline" not in column_names:
        print(f"{Fore.YELLOW}Adding 'outline' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN outline TEXT DEFAULT '';")
    # New columns for resume support.
    if "global_summary" not in column_names:
        print(f"{Fore.YELLOW}Adding 'global_summary' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN global_summary TEXT DEFAULT '';")
    if "final_chapter" not in column_names:
        print(f"{Fore.YELLOW}Adding 'final_chapter' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN final_chapter TEXT DEFAULT '';")
    if "characters" not in column_names:
        print(f"{Fore.YELLOW}Adding 'characters' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN characters TEXT DEFAULT '';")
    if "book_summary" not in column_names:
        print(f"{Fore.YELLOW}Adding 'book_summary' column to 'projects' table.{Style.RESET_ALL}")
        cursor.execute("ALTER TABLE projects ADD COLUMN book_summary TEXT DEFAULT '';")

    # Create table for chapters.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        chapter_number INTEGER,
        chapter_title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    );
    """)

    # Create table for feedback.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_id INTEGER,
        feedback_agent TEXT,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chapter_id) REFERENCES chapters(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"{Fore.GREEN}Schema initialized successfully in SQLite database '{db_file}'.{Style.RESET_ALL}")

def save_project(db_file, project_name, setting, description, status="in_progress"):
    """
    Inserts a new project record into the projects table and returns the project ID.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (project_name, setting, description, status)
        VALUES (?, ?, ?, ?)
    """, (project_name, setting, description, status))
    conn.commit()
    project_id = cursor.lastrowid
    cursor.close()
    conn.close()
    print(f"{Fore.GREEN}Project '{project_name}' saved with ID {project_id}.{Style.RESET_ALL}")
    return project_id

def update_project_outline(db_file, project_id, outline):
    """
    Updates the project's outline.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET outline=? WHERE id=?", (outline, project_id))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{Fore.CYAN}Project ID {project_id} outline updated.{Style.RESET_ALL}")

def update_project_story_details(db_file, project_id, global_summary, final_chapter, characters, book_summary=""):
    """
    Updates the project's story details.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE projects
        SET global_summary=?, final_chapter=?, characters=?, book_summary=?
        WHERE id=?
    """, (global_summary, final_chapter, characters, book_summary, project_id))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{Fore.CYAN}Project ID {project_id} story details updated.{Style.RESET_ALL}")

def get_project_details(db_file, project_id):
    """
    Returns the project's story details.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT global_summary, final_chapter, characters, book_summary
        FROM projects WHERE id=?
    """, (project_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {"global_summary": row[0], "final_chapter": row[1], "characters": row[2], "book_summary": row[3]}
    return {}

def get_project_outline(db_file, project_id):
    """
    Returns the saved outline of the project.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT outline FROM projects WHERE id=?", (project_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else ""

def save_chapter(db_file, project_id, chapter_number, chapter_title, content):
    """
    Inserts a new chapter record into the chapters table.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chapters (project_id, chapter_number, chapter_title, content)
        VALUES (?, ?, ?, ?)
    """, (project_id, chapter_number, chapter_title, content))
    conn.commit()
    chapter_id = cursor.lastrowid
    cursor.close()
    conn.close()
    print(f"{Fore.GREEN}Chapter {chapter_number} ('{chapter_title}') saved with ID {chapter_id}.{Style.RESET_ALL}")
    return chapter_id

def retrieve_saved_chapter(db_file, project_id, chapter_number):
    """
    Retrieves the saved content of a specific chapter for a project.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content FROM chapters
        WHERE project_id=? AND chapter_number=?
        ORDER BY id ASC
    """, (project_id, chapter_number))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        print(f"{Fore.GREEN}Retrieved saved Chapter {chapter_number} for project ID {project_id}.{Style.RESET_ALL}")
        return row[0]
    print(f"{Fore.YELLOW}No saved content found for Chapter {chapter_number}.{Style.RESET_ALL}")
    return ""

def update_project_status(db_file, project_id, status):
    """
    Updates the status of the project (e.g., 'in_progress', 'completed').
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE projects SET status=? WHERE id=?", (status, project_id))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{Fore.CYAN}Project ID {project_id} status updated to '{status}'.{Style.RESET_ALL}")

def get_incomplete_projects(db_file):
    """
    Returns a list of projects with status 'in_progress'.
    """
    conn = sqlite3.connect(db_file)
    # Set the row factory to produce dict-like rows
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, setting, description, status, outline FROM projects WHERE status='in_progress'")
    projects = [dict(row) for row in cursor.fetchall()]  # Convert rows to dictionaries
    cursor.close()
    conn.close()
    return projects

def get_project_by_id(db_file, project_id):
    """
    Returns the project record for the given ID.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, project_name, setting, description, status, outline FROM projects WHERE id=?", (project_id,))
    project = cursor.fetchone()
    cursor.close()
    conn.close()
    return project

def get_chapter_count(db_file, project_id):
    """
    Returns the number of chapters already saved for the project.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chapters WHERE project_id=?", (project_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count
