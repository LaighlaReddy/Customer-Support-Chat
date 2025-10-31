import psycopg2
import random
import json
from datetime import timedelta
from faker import Faker

# --- CONFIG ---
DB_CONFIG = {
    "host": "localhost",
    "database": "customer_support",
    "user": "",
    "password": "",
}

fake = Faker()

# --- DB HELPERS ---
def get_role_id(conn, role_name):
    with conn.cursor() as cur:
        cur.execute("SELECT role_id FROM role WHERE name = %s;", (role_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Role '{role_name}' not found.")
        return row[0]

def get_user_ids(conn, role_id):
    """Return list of user_ids for a given role."""
    with conn.cursor() as cur:
        cur.execute("SELECT user_id FROM users WHERE role_id = %s;", (role_id,))
        return [row[0] for row in cur.fetchall()]

def get_conversations_with_messages(conn):
    """Fetch conversation_id with the most recent message timestamp and user_id."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT m.conversation_id, MAX(m.created_at) AS last_time
            FROM messages m
            GROUP BY m.conversation_id;
        """)
        return cur.fetchall()

def insert_message(conn, conversation_id, user_id, content, created_at):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO messages (conversation_id, user_id, content, created_at)
            VALUES (%s, %s, %s::jsonb, %s);
        """, (conversation_id, user_id, json.dumps(content), created_at))

# --- MAIN ---
if __name__ == "__main__":
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        # Fetch roles
        agent_role_id = get_role_id(conn, "Agent")
        customer_role_id = get_role_id(conn, "Customer")

        # Fetch users by role
        agent_ids = get_user_ids(conn, agent_role_id)
        customer_ids = get_user_ids(conn, customer_role_id)

        print(f"✅ Found {len(agent_ids)} agents and {len(customer_ids)} customers.")

        # Fetch conversations with their last message timestamp
        conversations = get_conversations_with_messages(conn)
        print(f"✅ Found {len(conversations)} conversations to add agent responses to.")

        with conn:
            for convo_id, last_msg_time in conversations:
                # Pick one customer and one agent randomly for this conversation
                customer_id = random.choice(customer_ids)
                agent_id = random.choice(agent_ids)

                # Generate 2–6 new messages alternating between customer and agent
                num_new_messages = random.randint(2, 6)
                next_time = last_msg_time + timedelta(minutes=random.randint(1, 10))

                for i in range(num_new_messages):
                    sender_id = customer_id if i % 2 == 0 else agent_id
                    content = {
                        "text": fake.sentence(nb_words=random.randint(5, 12))
                    }

                    insert_message(conn, convo_id, sender_id, content, next_time)
                    next_time += timedelta(minutes=random.randint(1, 15))

        print("✅ Agent-customer two-way chats successfully populated!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
