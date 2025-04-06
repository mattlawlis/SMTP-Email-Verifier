# SMTP Email Verifier

A Python script to check the deliverability of email addresses by:
1. Performing a quick syntax check.  
2. Resolving the domain’s MX records (via [dnspython](https://pypi.org/project/dnspython/)).  
3. Attempting an SMTP handshake to see if the mail server will accept the recipient.

---

## Table of Contents
1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [How It Works](#how-it-works)  
6. [Caveats](#caveats)  
7. [FAQ](#faq)  
8. [License](#license)  

---

## Features
- **Syntax Validation**: Uses a simple regular expression to ensure the email follows standard `local@domain.tld` format.  
- **MX Record Lookup**: Tries to locate the mail exchanger (MX) for the domain.  
- **SMTP Handshake**: Connects to the mail server on port 25 and checks if it will accept the email address via `MAIL FROM` → `RCPT TO` commands.  

---

## Prerequisites
- **Python 3.6+** (Recommended: Python 3.10 or higher)
- **pip** or another package manager for Python.
- **[dnspython](https://pypi.org/project/dnspython/)** library for DNS lookups.

> **Note**: Some ISPs or hosting environments block port 25 (SMTP). If that is the case, the script may fail to connect to mail servers, resulting in false `INVALID` outcomes.

---

## Installation

1. **Clone or Download the Repository**  
   ```bash
   git clone https://github.com/YourUsername/your-repo.git
   cd your-repo
   ```

2. **Install Dependencies**  
   ```bash
   # Option 1: Install globally
   pip3 install dnspython

   # Option 2: Use a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install dnspython
   ```

3. **Verify Installation**  
   ```bash
   pip3 show dnspython
   ```
   You should see dnspython’s version, location, and other info.

---

## Usage

1. **Prepare `emails.txt`**  
   - In the same folder as `smtp_email_verifier.py`, create (or update) a file named `emails.txt`.  
   - Put one email address per line, for example:  
     ```
     example1@gmail.com
     user2@domain.org
     alice@unknown-domain.example
     ```

2. **Run the Script**  
   - Open a terminal and navigate to the script’s directory:
     ```bash
     python3 smtp_email_verifier.py
     ```
   - If using a virtual environment:
     ```bash
     source venv/bin/activate
     python smtp_email_verifier.py
     ```

3. **View the Results**  
   - The script prints each email address followed by `VALID` or `INVALID`.  
   - A summary of valid vs. invalid emails is displayed at the end.

**Example Output**:
```
example1@gmail.com -> VALID
user2@domain.org -> INVALID
alice@unknown-domain.example -> INVALID

--- Summary ---
Total emails processed: 3
Valid: 1
Invalid: 2
```

---

## How It Works

1. **Basic Syntax Check**  
   A simple regular expression validates the format `local-part@domain.tld`.

2. **MX Record Lookup**  
   - The script extracts the domain (everything after `@`).  
   - Uses `dns.resolver.resolve(domain, 'MX')` to fetch and sort MX records by priority.

3. **SMTP Handshake**  
   - Attempts to connect to each MX server on port 25.  
   - Sends:
     1. `EHLO` or `HELO`  
     2. `MAIL FROM:`  
     3. `RCPT TO:`  
   - If the server returns a `250` code for `RCPT TO`, the email is considered **VALID**. Otherwise, it tries the next MX server or marks as **INVALID**.

---

## Caveats

1. **Port 25 Blocking**  
   - Some networks block outbound SMTP on port 25, leading to connection failures.

2. **Catch-All Domains**  
   - Some domains accept mail for any address. Such addresses might appear **VALID** even if they don’t truly exist.

3. **Greylisting / Tarpitting**  
   - Some servers deliberately slow or block unknown senders, which may cause false negatives.

4. **Rate Limiting / Blacklisting**  
   - Sending too many verification requests can trigger rate limits or blacklisting.

---

## FAQ

1. **Why do I get `ModuleNotFoundError: No module named 'dns'`?**  
   Make sure `dnspython` is installed and that you’re not overshadowing the library with a local file named `dns.py`.

2. **Why is a known good address marked `INVALID`?**  
   - The mail server may block verification attempts from unknown or suspicious IPs.  
   - Temporary network issues could prevent connecting to the mail server.

3. **Why is an address I know is invalid reported as `VALID`?**  
   - The domain might be a “catch-all” domain that accepts mail for any user.

4. **Can I save the results to a file?**  
   - Yes. Modify the script to write the results to a CSV or text file, for example:
     ```python
     with open("results.csv", "w") as out:
         out.write("Email,Status\n")
         for email in emails:
             status_msg = "VALID" if verify_smtp(email) else "INVALID"
             out.write(f"{email},{status_msg}\n")
     ```

---

## License

This project is licensed under the [Apache License 2.0](LICENSE) - see the [LICENSE](LICENSE) file for details.  

Use at your own risk, and feel free to modify or redistribute under the terms of the Apache 2.0 license.  
