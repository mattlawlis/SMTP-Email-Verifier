# SMTP-Email-Verifier
This script reads email addresses from emails.txt (one per line), attempts to verify each address by: (1) checking basic syntax, (2) resolving the domain's MX record via dnspython and (3) performing an SMTP handshake to see if the server will accept mail for that address.
