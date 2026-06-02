"""
Database Initializer for Academic Management System
Run this script once to create the database, all tables, and seed data.
Usage: python init_db.py
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from config import Config

def init_database():
    """Create the database and all tables from schema.sql"""
    try:
        # Connect without specifying a database first
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS academic_management")
        cursor.execute("USE academic_management")
        print("[OK] Database 'academic_management' created/verified.")

        # Read and execute schema.sql
        with open('database/schema.sql', 'r') as f:
            sql_content = f.read()

        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        for statement in statements:
            # Skip comments-only blocks and CREATE DATABASE / USE statements
            lines = [l for l in statement.split('\n') if not l.strip().startswith('--')]
            clean = ' '.join(lines).strip()
            if not clean:
                continue
            if clean.upper().startswith('CREATE DATABASE') or clean.upper().startswith('USE '):
                continue
            try:
                cursor.execute(statement)
            except mysql.connector.Error as e:
                # Ignore "table already exists" and "duplicate entry" errors
                if e.errno not in (1050, 1062):
                    print(f"[WARN] {e.msg}")

        conn.commit()
        print("[OK] All tables created successfully.")

        # Seed the admin user with a proper password hash
        admin_hash = generate_password_hash('admin123')
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ('admin', admin_hash, 'admin')
            )
            conn.commit()
            print("[OK] Default admin user created (username: admin, password: admin123)")
        except mysql.connector.Error as e:
            if e.errno == 1062:
                print("[OK] Admin user already exists, skipping.")
            else:
                print(f"[WARN] Could not create admin: {e.msg}")

        cursor.close()
        conn.close()
        print("\n=== Database initialization complete! ===")
        print("You can now run the app with: python app.py")

    except Error as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        print("Make sure MySQL is running and the credentials in config.py are correct.")
        print(f"  Host: {Config.MYSQL_HOST}")
        print(f"  User: {Config.MYSQL_USER}")
        print(f"  Password: {'*' * len(Config.MYSQL_PASSWORD)}")

if __name__ == '__main__':
    init_database()
