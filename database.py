import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "spam_detector.db")

def init_db():
    """Initialize database with analysis_log table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            email_filename TEXT NOT NULL,
            sender TEXT,
            subject TEXT,
            classification TEXT NOT NULL,
            is_spam INTEGER NOT NULL,
            confidence INTEGER,
            reason TEXT,
            copied_to_folder TEXT,
            success INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def log_analysis(email_filename, parsed_email, spam_result, copy_result):
    """Log email analysis to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO analysis_log 
        (timestamp, email_filename, sender, subject, classification, is_spam, confidence, reason, copied_to_folder, success)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        email_filename,
        parsed_email.get("from", "Unknown"),
        parsed_email.get("subject", "No Subject"),
        spam_result["classification"],
        1 if spam_result["is_spam"] else 0,
        spam_result.get("confidence", 0),
        spam_result["reason"],
        copy_result.get("folder", ""),
        1 if copy_result.get("success", False) else 0
    ))
    
    conn.commit()
    conn.close()

def get_analysis_history(limit=50):
    """Get recent analysis history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, timestamp, email_filename, sender, subject, classification, is_spam, confidence, reason, copied_to_folder
        FROM analysis_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "timestamp": row[1],
            "email_filename": row[2],
            "sender": row[3],
            "subject": row[4],
            "classification": row[5],
            "is_spam": bool(row[6]),
            "confidence": row[7],
            "reason": row[8],
            "copied_to_folder": row[9]
        }
        for row in rows
    ]

def get_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analysis_log WHERE is_spam = 1")
    spam_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM analysis_log WHERE is_spam = 0")
    real_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "spam_count": spam_count,
        "real_count": real_count,
        "total": spam_count + real_count
    }
