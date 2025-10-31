import random
import json
import psycopg2
from datetime import datetime, timedelta

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "customer_support",
    "user": "",
    "password": ""
}

# --- SAMPLE DATA ---
first_names = [
    "Alice", "Liam", "Noah", "Emma", "Olivia", "Ethan", "Sophia", "Mia", "Lucas", "Ava",
    "Sipho", "Lerato", "Thabo", "Nomsa", "Zanele", "Nkosi", "Kabelo", "Nandi", "Sibongile", "Ayanda"
]
last_names = [
    "Smith", "Brown", "Williams", "Taylor", "Jones", "Pillay", "Naidoo", "Dlamini", "Botha", "Nkosi",
    "Moodley", "Campbell", "Adams", "Cooper", "Hughes", "Van der Merwe", "Patel", "Mthembu", "Evans", "Daniels"
]

skills_pool = [
    ["billing", "technical support"],
    ["sales", "customer relations"],
    ["product knowledge", "troubleshooting"],
    ["returns", "account management"],
    ["escalation handling", "complaint resolution"]
]
statuses = ["available", "busy", "offline", "on break"]
departments = ["Customer Support", "Technical Assistance", "Billing", "Sales Support"]
certifications_pool = [
    ["CCNA", "ITIL"],
    ["CompTIA A+", "HDI Support Center Analyst"],
    ["AWS Certified Cloud Practitioner"],
    ["Microsoft 365 Certified"],
    ["Zendesk Expert", "CX Certification"]
]
shifts = [
    {"start": "06:00", "end": "14:00"},
    {"start": "08:00", "end": "16:00"},
    {"start": "09:00", "end": "17:00"},
    {"start": "10:00", "end": "18:00"},
    {"start": "12:00", "end": "20:00"}
]

def random_date(start_year=2018, end_year=2024):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    return (start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime("%Y-%m-%d")

# --- GENERATE AGENTS ---
def generate_agents(n=50):
    agents = []
    for i in range(n):
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@support.com"
        agent = {
            "name": full_name,
            "email": email,
            "skills": random.choice(skills_pool),
            "status": random.choice(statuses),
            "department": random.choice(departments),
            "shift": random.choice(shifts),
            "metadata": {
                "hire_date": random_date(2018, 2024),
                "certifications": random.choice(certifications_pool)
            }
        }
        agents.append(agent)
    return agents

# --- DATABASE FUNCTIONS ---
def get_role_id(conn, role_name):
    with conn.cursor() as cur:
        cur.execute("SELECT role_id FROM role WHERE name = %s;", (role_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Role '{role_name}' not found in role table.")
        return row[0]

def insert_agents(conn, role_id, agents):
    with conn.cursor() as cur:
        for agent in agents:
            cur.execute("""
                INSERT INTO users (role_id, details)
                VALUES (%s, %s::jsonb);
            """, (role_id, json.dumps(agent)))
    conn.commit()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)

        # Fetch role_id for 'Agent'
        role_id = get_role_id(conn, "Agent")
        print(f"✅ Found role_id for 'Agent': {role_id}")

        # Generate 50 agent records
        agents = generate_agents(50)
        print(f"✅ Generated {len(agents)} agents")

        # Insert into users table
        insert_agents(conn, role_id, agents)
        print("✅ Successfully inserted agents into users table")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
