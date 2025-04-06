#!/usr/bin/env python3

"""
smtp_email_verifier.py
----------------------
This script reads email addresses from emails.txt (one per line),
attempts to verify each address by:
1) Checking basic syntax.
2) Resolving the domain's MX record via dnspython.
3) Performing an SMTP handshake to see if the server will accept mail for that address.
"""

import re
import dns.resolver
import smtplib
import socket

def is_valid_syntax(email: str) -> bool:
    """
    Basic email syntax check using a simple regex.
    This won't catch all edge cases, but it's usually enough for typical usage.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None

def get_mx_records(domain: str):
    """
    Returns a list of MX records for the given domain, sorted by priority.
    If no MX records found, or an error occurs, returns an empty list.
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        # Each answer has a preference (priority) and exchange
        mx_records = sorted(
            [(r.preference, str(r.exchange).rstrip('.')) for r in answers],
            key=lambda record: record[0]
        )
        return [exchange for (_, exchange) in mx_records]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return []
    except Exception as e:
        print(f"Error resolving MX for domain {domain}: {e}")
        return []

def verify_smtp(email: str) -> bool:
    """
    Verifies if the email is deliverable by:
    1) Extracting the domain
    2) Querying MX record
    3) Attempting an SMTP handshake (MAIL FROM -> RCPT TO)
    """
    # 1) Basic syntax check first
    if not is_valid_syntax(email):
        return False

    # 2) Get domain from email
    domain = email.split('@')[-1]

    # 3) Retrieve MX records
    mx_hosts = get_mx_records(domain)
    if not mx_hosts:
        # If no MX records found, fallback to domain as a last resort
        # or simply consider invalid.
        return False

    # 4) Try connecting to each MX server in order until one responds
    from_address = "test@example.com"  # Could be any valid or invalid sender
    for mx_host in mx_hosts:
        try:
            # 4a) Connect to mail server (port 25 by default)
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host, 25)
            server.helo("test.com")
            
            # Some servers require a mail from to continue
            server.mail(from_address)
            code, msg = server.rcpt(email)
            
            # 4b) If code == 250, the server accepted the recipient
            server.quit()
            if code == 250:
                return True
            else:
                # Try the next MX record if this fails
                continue
        except (socket.error, smtplib.SMTPException) as e:
            # Connection failed, try next MX
            # print(f"Error connecting to {mx_host}: {e}")
            continue

    # If all MX servers failed or returned a bad code, it's probably invalid
    return False

def main():
    input_file = "emails.txt"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            emails = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERROR: File '{input_file}' not found.")
        return

    valid_count = 0
    invalid_count = 0

    for email in emails:
        is_valid = verify_smtp(email)
        status_msg = "VALID" if is_valid else "INVALID"
        print(f"{email} -> {status_msg}")
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    print("\n--- Summary ---")
    print(f"Total emails processed: {len(emails)}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")

if __name__ == "__main__":
    main()
