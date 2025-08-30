from neo4j import GraphDatabase
from typing import Union, List, Dict
from wonderwords import RandomWord
from dotenv import load_dotenv
import os
import re
import argparse
import sys

load_dotenv()

# Connection settings (must be admin)
URI = os.getenv("NEO4J_URI")
ADMIN_USER = os.getenv("NEO4J_USERNAME")
ADMIN_PASS = os.getenv("NEO4J_PASSWORD")

# Initialize wonderwords generator
rw = RandomWord()

def sanitize_email(email: str) -> str:
    """
    Converts an email into a valid Neo4j identifier. Neo4j usernames does not take symbols
    Example: john.doe@example.com -> johndotdoeatexampledotcom
    """
    return re.sub(r'[^a-zA-Z0-9@.]', '', email).replace('@', 'AT').replace('.', 'DOT').lower()

def generate_password() -> str:
    """Generate a human-readable password like 'bright-sparrow' using wonderwords."""
    adjective = rw.word(include_parts_of_speech=["adjective"])
    noun = rw.word(include_parts_of_speech=["noun"])
    return f"{adjective}-{noun}"

def provision_users(emails: Union[str, List[str]]) -> List[Dict[str, str]]:
    """
    Provision one or more users:
      - Creates a new database for each email
      - Creates a new user with a random human-readable password
      - Grants full privileges on their own db
      - Grants read/create/update (but no delete) on shared 'neo4j' db
    Returns: list of dicts {email, password}
    """

    if isinstance(emails, str):
        emails = [emails]  # normalize to list

    results = []

    with GraphDatabase.driver(URI, auth=(ADMIN_USER, ADMIN_PASS)) as driver:
        with driver.session(database="system") as session:
            for email in emails:
                db_name = sanitize_email(email)
                user_name = db_name
                password = generate_password()

                # 1. Create database
                session.run(f"CREATE DATABASE {db_name} IF NOT EXISTS")

                # 2. Create user with random password
                session.run(f"""
                    CREATE USER {user_name} IF NOT EXISTS
                    SET PASSWORD '{password}' CHANGE NOT REQUIRED
                """)

                # 3. Create role for the user
                role_name = f"{user_name}"
                session.run(f"CREATE ROLE {role_name} IF NOT EXISTS")
                session.run(f"GRANT ROLE {role_name} TO {user_name}")

                # 4. Restrict access to only neo4j + their db
                session.run(f"DENY ACCESS ON DATABASE * TO {role_name}")
                session.run(f"GRANT ACCESS ON DATABASE neo4j TO {role_name}")
                session.run(f"GRANT ACCESS ON DATABASE {db_name} TO {role_name}")

                # 5. Privileges on their own database
                session.run(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {role_name}")

                # 6. Privileges on shared 'neo4j' db (no delete)
                session.run(f"GRANT ACCESS ON DATABASE neo4j TO {role_name}")
                session.run(f"GRANT MATCH {{*}} ON GRAPH neo4j TO {role_name}")
                session.run(f"GRANT CREATE ON GRAPH neo4j TO {role_name}")
                session.run(f"DENY DELETE ON GRAPH neo4j TO {role_name}")

                # Deny sensitive system access
                session.run(f"DENY SHOW USER ON DBMS TO {role_name}")
                session.run(f"DENY SHOW ROLE ON DBMS TO {role_name}")
                session.run(f"DENY SHOW PRIVILEGE ON DBMS TO {role_name}")

                results.append({"email": email, "db_name": db_name, "user_name": user_name, "password": password})

                print(f"✅ Provisioned user '{user_name}' "
                      f"(db: {db_name}, pw: {password})")

    return results

def remove_users(emails: Union[str, List[str]]) -> List[Dict[str, str]]:
    """
    Remove one or more users:
      - Removes the user
      - Removes the role
      - Removes the database
    Returns: list of dicts {email, db_name}
    """

    if isinstance(emails, str):
        emails = [emails]  # normalize to list

    results = []

    with GraphDatabase.driver(URI, auth=(ADMIN_USER, ADMIN_PASS)) as driver:
        with driver.session(database="system") as session:
            for email in emails:
                db_name = sanitize_email(email)
                user_name = db_name

                # 1. Remove user
                session.run(f"DROP USER {user_name}")

                # 2. Remove database
                session.run(f"DROP DATABASE {db_name}")

                # 3. Remove role
                session.run(f"DROP ROLE {user_name}")

                results.append({"email": email, "db_name": db_name})

                print(f"✅ Removed user '{user_name}' "
                      f"(db: {db_name})")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage Neo4j tenant users')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create the parser for the "add" command
    add_parser = subparsers.add_parser('add', help='Add new users')
    add_parser.add_argument('emails', nargs='+', help='List of email addresses to add')
    
    # Create the parser for the "remove" command
    remove_parser = subparsers.add_parser('remove', help='Remove existing users')
    remove_parser.add_argument('emails', nargs='+', help='List of email addresses to remove')

    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.command == 'add':
        print(f"Adding users: {', '.join(args.emails)}")
        output = provision_users(args.emails)
        print("\nSuccessfully provisioned users:")
        for entry in output:
            print(f"Email: {entry['email']}")
            print(f"  Username: {entry['user_name']}")
            print(f"  Database: {entry['db_name']}")
            print(f"  Password: {entry['password']}")
    
    elif args.command == 'remove':
        print(f"Removing users: {', '.join(args.emails)}")
        output = remove_users(args.emails)
        print("\nSuccessfully removed users:")
        for entry in output:
            print(f"Email: {entry['email']} (Database: {entry['db_name']})")
    
    else:
        parser.print_help()
        sys.exit(1)
