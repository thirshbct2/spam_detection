import email
from email import policy
from email.parser import BytesParser

def parse_eml(file_path: str):
    """
    Parse .eml file and extract email details
    """
    with open(file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract plain text body
    if msg.is_multipart():
        parts = [part.get_payload(decode=True).decode(errors="ignore")
                 for part in msg.walk() if part.get_content_type() == "text/plain"]
        body = "\n".join(parts)
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    return {
        "subject": msg.get("subject", "No Subject"),
        "from": msg.get("from", "Unknown Sender"),
        "to": msg.get("to", "Unknown Recipient"),
        "body": body
    }