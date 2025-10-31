import psycopg2
from psycopg2 import sql

# --- Database configuration ---
DB_CONFIG = {
    "host": "localhost",
    "database": "customer_support",
    "user": "",
    "password": "",
    "port": 5432  # Default PostgreSQL port
}

INSERT_ROLES_SQL = """
INSERT INTO role (name)
VALUES (%s)
ON CONFLICT (name) DO NOTHING;
"""

# --- Main execution ---
def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        # 4. Insert roles
        roles = ["Customer", "Agent"]
        for role in roles:
            cur.execute(INSERT_ROLES_SQL, (role,))
        print("✅ Roles inserted (Customer, Agent).")

        cur.close()
        conn.close()
        print("🎉 Setup complete.")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
