import sqlite3
from datetime import datetime

# ==========================================
# DATABASE CONNECTION
# ==========================================

conn = sqlite3.connect(
    "chat_history.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ==========================================
# CREATE TABLES
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_sessions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    created_at TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    session_id INTEGER,

    role TEXT,

    message TEXT,

    FOREIGN KEY(session_id)
    REFERENCES chat_sessions(id)

)
""")

conn.commit()

# ==========================================
# CREATE NEW CHAT
# ==========================================

def create_chat(title="New Chat"):

    cursor.execute(
        """
        INSERT INTO chat_sessions(title, created_at)
        VALUES (?, ?)
        """,
        (
            title,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()

    return cursor.lastrowid


# ==========================================
# GET ALL CHATS
# ==========================================

def get_chats():

    cursor.execute(
        """
        SELECT id, title
        FROM chat_sessions
        ORDER BY id DESC
        """
    )

    return cursor.fetchall()


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(session_id, role, message):

    cursor.execute(
        """
        INSERT INTO messages(session_id, role, message)
        VALUES (?, ?, ?)
        """,
        (
            session_id,
            role,
            message
        )
    )

    conn.commit()


# ==========================================
# LOAD MESSAGES
# ==========================================

def load_messages(session_id):

    cursor.execute(
        """
        SELECT role, message
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,)
    )

    return cursor.fetchall()


# ==========================================
# DELETE CHAT
# ==========================================

def delete_chat(session_id):

    cursor.execute(
        """
        DELETE FROM messages
        WHERE session_id = ?
        """,
        (session_id,)
    )

    cursor.execute(
        """
        DELETE FROM chat_sessions
        WHERE id = ?
        """,
        (session_id,)
    )

    conn.commit()


# ==========================================
# UPDATE CHAT TITLE
# ==========================================

def update_chat_title(session_id, title):

    cursor.execute(
        """
        UPDATE chat_sessions
        SET title = ?
        WHERE id = ?
        """,
        (
            title,
            session_id
        )
    )

    conn.commit()