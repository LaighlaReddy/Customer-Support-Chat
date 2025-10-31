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

# --- SAMPLE DATA FOR UK & SA CUSTOMERS ---
first_names = [
    "James", "Oliver", "William", "Noah", "Liam", "Amelia", "Isabella", "Olivia", "Emily", "Sophia",
    "Lerato", "Thabo", "Sipho", "Ayanda", "Nkosi", "Nomsa", "Kabelo", "Zanele", "Mpho", "Sibongile"
]
last_names = [
    "Smith", "Brown", "Jones", "Williams", "Taylor", "Naidoo", "Dlamini", "Mthembu", "Khumalo", "Pillay",
    "Patel", "Botha", "Van der Merwe", "Nkosi", "Moodley", "Adams", "Hughes", "Campbell", "Cooper", "Evans"
]
uk_cities = ["London", "Manchester", "Birmingham", "Liverpool", "Leeds", "Sheffield", "Bristol", "Newcastle", "Glasgow", "Cardiff"]
za_cities = ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "East London", "Polokwane", "Nelspruit", "Kimberley"]
uk_counties = ["Greater London", "West Midlands", "Merseyside", "Yorkshire", "Lancashire", "Surrey"]
za_provinces = ["Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape", "Free State", "Limpopo"]
contact_methods = ["email", "phone"]
languages = ["en", "af", "zu", "xh"]  # English, Afrikaans, Zulu, Xhosa

# --- HELPERS ---
def random_date(start_year=2020, end_year=2025):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    return (start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime("%Y-%m-%d")

def random_postcode(region):
    if region == "UK":
        return f"{random.choice(['SW1A', 'M1', 'B1', 'L1', 'LS1', 'G1'])} {random.randint(1,9)}{random.choice('ABCD')}"
    else:
        return str(random.randint(1000, 9999))

def random_phone(region):
    if region == "UK":
        return f"+44 7{random.randint(100,999)} {random.randint(100000,999999)}"
    else:
        return f"+27 {random.randint(60,83)} {random.randint(100,999)} {random.randint(1000,9999)}"

# --- GENERATE CUSTOMERS ---
def generate_customers(n=100):
    customers = []
    for i in range(n):
        region = random.choice(["UK", "ZA"])
        first = random.choice(first_names)
        last = random.choice(last_names)
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        phone = random_phone(region)
        street_num = random.randint(1, 250)
        street_name = random.choice(["Main Road", "High Street", "Church Lane", "Station Road", "Market Street", "Long Street", "Victoria Road"])
        city = random.choice(uk_cities) if region == "UK" else random.choice(za_cities)
        state = random.choice(uk_counties) if region == "UK" else random.choice(za_provinces)
        postcode = random_postcode(region)
        contact_method = random.choice(contact_methods)
        language = random.choice(languages)

        customer = {
            "name": full_name,
            "email": email,
            "phone": phone,
            "address": {
                "street": f"{street_num} {street_name}",
                "city": city,
                "state": state,
                "zip": postcode
            },
            "preferences": {
                "contact_method": contact_method,
                "language": language
            },
            "metadata": {
                "signup_date": random_date(2020, 2023),
                "last_login": random_date(2024, 2025)
            }
        }
        customers.append(customer)
    return customers

# --- DATABASE FUNCTIONS ---
def get_role_id(conn, role_name):
    with conn.cursor() as cur:
        cur.execute("SELECT role_id FROM role WHERE name = %s;", (role_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Role '{role_name}' not found in role table.")
        return row[0]

def insert_customers(conn, role_id, customers):
    with conn.cursor() as cur:
        for customer in customers:
            cur.execute("""
                INSERT INTO users (role_id, details)
                VALUES (%s, %s::jsonb);
            """, (role_id, json.dumps(customer)))
    conn.commit()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        role_id = get_role_id(conn, "Customer")
        print(f"✅ Found role_id for 'Customer': {role_id}")

        customers = generate_customers(100)
        print(f"✅ Generated {len(customers)} customers")

        insert_customers(conn, role_id, customers)
        print("✅ Successfully inserted customers into users table")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
