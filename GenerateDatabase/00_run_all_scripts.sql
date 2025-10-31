-- Master script to run all other SQL scripts in order

-- 2. Create Agent Table
\i 'GenerateDatabase/02_create_roles_table.sql'

-- 3. Create Customer Table
\i 'GenerateDatabase/03_create_users_table.sql'

-- 4. Create Conversations Table
\i 'GenerateDatabase/04_create_status_table.sql'

-- 5. Create Messages Table
\i 'GenerateDatabase/05_create_conversations_table.sql'

-- Optional: Insert sample data
\i 'GenerateDatabase/06_create_messages_table.sql'