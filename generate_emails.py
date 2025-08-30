from faker import Faker
import csv
from typing import List

def generate_emails(count: int) -> List[str]:
    """
    Generate a list of unique mock email addresses using Faker.
    
    Args:
        count: Number of email addresses to generate
        
    Returns:
        List of unique email addresses
    """
    fake = Faker()
    emails = set()
    
    while len(emails) < count:
        email = fake.unique.email()
        emails.add(email)
        
    return list(emails)

def save_emails_to_csv(emails: List[str], filename: str = 'emails.csv') -> None:
    """
    Save a list of emails to a CSV file with an 'email' header.
    
    Args:
        emails: List of email addresses
        filename: Output CSV filename
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email'])  # Write header
        writer.writerows([[email] for email in emails])
    print(f"Saved {len(emails)} emails to {filename}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate mock email addresses')
    parser.add_argument('count', type=int, help='Number of emails to generate')
    parser.add_argument('--output', '-o', default='emails.csv', 
                       help='Output CSV filename (default: emails.csv)')
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} unique email addresses...")
    emails = generate_emails(args.count)
    save_emails_to_csv(emails, args.output)