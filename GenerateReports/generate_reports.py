import psycopg2
import pandas as pd
from datetime import datetime

# --- CONFIG ---
DB_CONFIG = {
    "host": "localhost",
    "database": "customer_support",
    "user": "",
    "password": "",
}

# --- QUERIES ---
QUERIES = {
    "Active Conversations": """
        SELECT c.conversation_id, cu.details->>'name' AS customer_name,
               ag.details->>'name' AS agent_name, s.name AS status
        FROM conversations c
        JOIN status s ON c.status_id = s.status_id
        LEFT JOIN messages m_c ON m_c.conversation_id = c.conversation_id
        LEFT JOIN users cu ON m_c.user_id = cu.user_id AND cu.role_id = (SELECT role_id FROM role WHERE name = 'Customer')
        LEFT JOIN messages m_a ON m_a.conversation_id = c.conversation_id
        LEFT JOIN users ag ON m_a.user_id = ag.user_id AND ag.role_id = (SELECT role_id FROM role WHERE name = 'Agent')
        WHERE s.name = 'open'
        GROUP BY c.conversation_id, cu.details->>'name', ag.details->>'name', s.name;
    """,

    "Message Volume": """
        SELECT u.details->>'name' AS customer_name,
               COUNT(m.message_id) AS message_count
        FROM messages m
        JOIN users u ON m.user_id = u.user_id
        WHERE u.role_id = (SELECT role_id FROM role WHERE name = 'Customer')
          AND m.created_at BETWEEN NOW() - INTERVAL '30 days' AND NOW()
        GROUP BY u.details->>'name'
        ORDER BY message_count DESC;
    """,

    "Agent Conversations": """
        SELECT a.details->>'name' AS agent_name,
               COUNT(DISTINCT m.conversation_id) AS conversations_handled
        FROM messages m
        JOIN users a ON m.user_id = a.user_id
        WHERE a.role_id = (SELECT role_id FROM role WHERE name = 'Agent')
        GROUP BY a.details->>'name'
        ORDER BY conversations_handled DESC;
    """,

    "Agent Response Times": """
        WITH ordered_msgs AS (
            SELECT
                m.conversation_id, m.user_id, m.created_at,
                LAG(m.created_at) OVER (PARTITION BY m.conversation_id ORDER BY m.created_at) AS prev_time,
                LAG(u.role_id) OVER (PARTITION BY m.conversation_id ORDER BY m.created_at) AS prev_role
            FROM messages m
            JOIN users u ON m.user_id = u.user_id
        )
        SELECT
            u.details->>'name' AS agent_name,
            ROUND(MIN(EXTRACT(EPOCH FROM (o.created_at - o.prev_time)))/60, 2) AS min_response_min,
            ROUND(MAX(EXTRACT(EPOCH FROM (o.created_at - o.prev_time)))/60, 2) AS max_response_min,
            ROUND(AVG(EXTRACT(EPOCH FROM (o.created_at - o.prev_time)))/60, 2) AS avg_response_min
        FROM ordered_msgs o
        JOIN users u ON o.user_id = u.user_id
        WHERE u.role_id = (SELECT role_id FROM role WHERE name = 'Agent')
          AND o.prev_role = (SELECT role_id FROM role WHERE name = 'Customer')
        GROUP BY u.details->>'name';
    """,

    "Customer Engagement": """
        SELECT u.details->>'name' AS customer_name,
               COUNT(DISTINCT m.conversation_id) AS conversations,
               COUNT(m.message_id) AS total_messages
        FROM messages m
        JOIN users u ON m.user_id = u.user_id
        WHERE u.role_id = (SELECT role_id FROM role WHERE name = 'Customer')
          AND m.created_at >= NOW() - INTERVAL '1 month'
        GROUP BY u.details->>'name'
        ORDER BY total_messages DESC
        LIMIT 10;
    """,

    "Conversation Duration": """
        WITH convo_times AS (
            SELECT c.conversation_id,
                   MIN(m.created_at) AS start_time,
                   MAX(m.created_at) AS end_time
            FROM conversations c
            JOIN messages m ON c.conversation_id = m.conversation_id
            JOIN status s ON c.status_id = s.status_id
            WHERE s.name = 'closed'
            GROUP BY c.conversation_id
        )
        SELECT conversation_id, start_time, end_time,
               ROUND(EXTRACT(EPOCH FROM (end_time - start_time))/60, 2) AS duration_minutes
        FROM convo_times
        ORDER BY duration_minutes DESC;
    """
}

# --- RUN REPORTS ---
conn = psycopg2.connect(**DB_CONFIG)
excel_filename = f"chat_reports_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

with pd.ExcelWriter(excel_filename) as writer:
    for sheet, query in QUERIES.items():
        df = pd.read_sql_query(query, conn)
        df.to_excel(writer, index=False, sheet_name=sheet)
        print(f"✅ Wrote {sheet} ({len(df)} rows)")

conn.close()
print(f"\n📊 Reports saved to: {excel_filename}")
