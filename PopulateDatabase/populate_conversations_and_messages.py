import psycopg2
import random
import json
from datetime import datetime, timedelta
from faker import Faker

# --- CONFIG ---
DB_CONFIG = {
    "host": "localhost",
    "database": "customer_support",
    "user": "",
    "password": "",
}

fake = Faker()

# --- HELPERS ---
def random_datetime(start_year=2023, end_year=2025):
    """Generate random datetime."""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                             seconds=random.randint(0, 86400))

# --- DB FUNCTIONS ---
def get_role_id(conn, role_name):
    with conn.cursor() as cur:
        cur.execute("SELECT role_id FROM role WHERE name = %s;", (role_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Role '{role_name}' not found.")
        return row[0]

def get_status_ids(conn):
    """Fetch open and closed status IDs."""
    with conn.cursor() as cur:
        cur.execute("SELECT status_id, name FROM status;")
        rows = cur.fetchall()
        status_map = {r[1].lower(): r[0] for r in rows}
        if "open" not in status_map or "closed" not in status_map:
            raise ValueError("Both 'open' and 'closed' statuses must exist.")
        return status_map["open"], status_map["closed"]

def get_customer_ids(conn, customer_role_id):
    """Fetch all user_ids for customers."""
    with conn.cursor() as cur:
        cur.execute("SELECT user_id FROM users WHERE role_id = %s;", (customer_role_id,))
        return [row[0] for row in cur.fetchall()]

def insert_conversation(conn, status_id):
    """Insert one conversation and return its ID."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO conversations (status_id)
            VALUES (%s)
            RETURNING conversation_id;
        """, (status_id,))
        return cur.fetchone()[0]

def insert_message(conn, conversation_id, user_id, content, created_at):
    """Insert one message record."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO messages (conversation_id, user_id, content, created_at)
            VALUES (%s, %s, %s::jsonb, %s);
        """, (conversation_id, user_id, json.dumps(content), created_at))

# --- MAIN ---
if __name__ == "__main__":
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        # Get IDs
        customer_role_id = get_role_id(conn, "Customer")
        status_open, status_closed = get_status_ids(conn)
        customer_ids = get_customer_ids(conn, customer_role_id)

        print(f"✅ Found {len(customer_ids)} customers.")
        print(f"✅ Status IDs → open: {status_open}, closed: {status_closed}")

        with conn:
            for customer_id in customer_ids:
                # Each customer can have 1–5 conversations
                for _ in range(random.randint(1, 5)):
                    status_id = random.choice([status_open, status_closed])
                    conversation_id = insert_conversation(conn, status_id)

                    # Generate 3–10 messages for this conversation
                    num_messages = random.randint(3, 10)
                    base_time = random_datetime(2024, 2025)

                    for i in range(num_messages):
                        msg_time = base_time + timedelta(minutes=i * random.randint(2, 15))
                        message_content = {"text": fake.sentence(nb_words=random.randint(4, 12))}
                        insert_message(conn, conversation_id, customer_id, message_content, msg_time)

            print("✅ Conversations and messages successfully populated!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
