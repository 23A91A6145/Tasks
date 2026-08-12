# app/database.py

import sqlite3
import json
from datetime import datetime
from app.config import DATABASE_PATH
from app.models import TicketResult

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_message TEXT NOT NULL,
            category TEXT NOT NULL,
            secondary_category TEXT,
            priority TEXT NOT NULL,
            suggested_agent TEXT NOT NULL,
            confidence REAL NOT NULL,
            summary TEXT NOT NULL,
            reasoning TEXT NOT NULL,
            requires_human_review INTEGER NOT NULL,
            model_used TEXT NOT NULL,
            processing_time_ms INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            original_category TEXT,
            original_priority TEXT,
            is_reclassified INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_classification(message: str, result: TicketResult, model_used: str, processing_time_ms: int) -> int:
    """Saves a ticket classification result into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO tickets (
            ticket_message, category, secondary_category, priority, suggested_agent, confidence, 
            summary, reasoning, requires_human_review, model_used, processing_time_ms, created_at,
            original_category, original_priority, is_reclassified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        message,
        result.category.value,
        result.secondary_category.value if result.secondary_category else None,
        result.priority.value,
        result.suggested_agent.value,
        result.confidence,
        result.summary,
        result.reasoning,
        1 if result.requires_human_review else 0,
        model_used,
        processing_time_ms,
        created_at,
        result.category.value,
        result.priority.value
    ))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def get_tickets(limit: int = 50, offset: int = 0):
    """Fetches classified tickets from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tickets 
        ORDER BY id DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    
    tickets = []
    for row in rows:
        ticket = dict(row)
        ticket['requires_human_review'] = bool(ticket['requires_human_review'])
        ticket['is_reclassified'] = bool(ticket['is_reclassified'])
        tickets.append(ticket)
    return tickets

def get_metrics():
    """Computes key analytics and metric details from the classified tickets database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]
    
    if total_tickets == 0:
        conn.close()
        return {
            "total_tickets": 0,
            "category_distribution": {},
            "priority_distribution": {},
            "requires_human_review_rate": 0.0,
            "average_confidence": 0.0,
            "average_processing_time_ms": 0.0
        }
        
    # Human review rate
    cursor.execute("SELECT SUM(requires_human_review) FROM tickets")
    human_reviews = cursor.fetchone()[0] or 0
    review_rate = round(human_reviews / total_tickets, 4)
    
    # Average confidence
    cursor.execute("SELECT AVG(confidence) FROM tickets")
    avg_confidence = round(cursor.fetchone()[0] or 0.0, 4)
    
    # Average processing time
    cursor.execute("SELECT AVG(processing_time_ms) FROM tickets")
    avg_processing_time = round(cursor.fetchone()[0] or 0.0, 2)
    
    # Category distribution
    cursor.execute("SELECT category, COUNT(*) FROM tickets GROUP BY category")
    category_rows = cursor.fetchall()
    category_dist = {row[0]: row[1] for row in category_rows}
    
    # Priority distribution
    cursor.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
    priority_rows = cursor.fetchall()
    priority_dist = {row[0]: row[1] for row in priority_rows}
    
    conn.close()
    
    return {
        "total_tickets": total_tickets,
        "category_distribution": category_dist,
        "priority_distribution": priority_dist,
        "requires_human_review_rate": review_rate,
        "average_confidence": avg_confidence,
        "average_processing_time_ms": avg_processing_time
    }

def reclassify_ticket_db(ticket_id: int, new_category: str, new_priority: str, new_agent: str) -> bool:
    """Updates classification fields for a ticket and marks it as reclassified."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if ticket exists
    cursor.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,))
    if not cursor.fetchone():
        conn.close()
        return False
        
    cursor.execute("""
        UPDATE tickets
        SET category = ?,
            priority = ?,
            suggested_agent = ?,
            is_reclassified = 1
        WHERE id = ?
    """, (new_category, new_priority, new_agent, ticket_id))
    
    conn.commit()
    conn.close()
    return True
