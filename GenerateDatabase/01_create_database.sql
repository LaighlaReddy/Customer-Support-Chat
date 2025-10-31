--PostgresSQL Database Creation Script

--Create the new database
CREATE DATABASE customer_support
       WITH
       OWNER = lubi
       ENCODING = 'UTF8'
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       TEMPLATE = template0;

