import os
import shutil
from datetime import datetime

def copy_email_with_reason(email_filename, is_spam, reason, source_dir):
    """
    Copy email to appropriate folder (spam or real_mails) and save the reason.
    Original email remains in mails folder.
    
    Args:
        email_filename: Name of the .eml file
        is_spam: Boolean - True if spam, False if legitimate
        reason: 2-line explanation
        source_dir: Directory where original email is located (mails folder)
    
    Returns:
        dict with status and destination path
    """
    # Get parent directory (project root)
    parent_dir = os.path.dirname(source_dir)
    
    # Determine destination folder
    if is_spam:
        dest_folder = os.path.join(parent_dir, "spam")
    else:
        dest_folder = os.path.join(parent_dir, "real_mails")
    
    # Ensure destination folder exists
    os.makedirs(dest_folder, exist_ok=True)
    
    # Source and destination paths
    source_path = os.path.join(source_dir, email_filename)
    dest_email_path = os.path.join(dest_folder, email_filename)
    
    # Create reason filename (same name but .txt extension)
    reason_filename = email_filename.replace(".eml", "_reason.txt")
    dest_reason_path = os.path.join(dest_folder, reason_filename)
    
    try:
        # Copy email to destination (keep original in mails folder)
        shutil.copy2(source_path, dest_email_path)
        
        # Save reason to text file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        classification = "SPAM/PHISHING" if is_spam else "LEGITIMATE"
        
        with open(dest_reason_path, 'w', encoding='utf-8') as f:
            f.write(f"Email Classification Report\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Email File: {email_filename}\n")
            f.write(f"Analysis Date: {timestamp}\n")
            f.write(f"Classification: {classification}\n\n")
            f.write(f"Reason:\n")
            f.write(f"{reason}\n\n")
            f.write(f"=" * 50 + "\n")
            
            if is_spam:
                f.write(f"\nSECURITY WARNINGS:\n")
                f.write(f"- DO NOT RESPOND to this email\n")
                f.write(f"- DO NOT CLICK any links\n")
                f.write(f"- DO NOT SHARE personal information\n")
                f.write(f"- DELETE this email immediately\n")
            else:
                f.write(f"\nSTATUS: This email appears to be safe\n")
        
        return {
            "success": True,
            "email_path": dest_email_path,
            "reason_path": dest_reason_path,
            "folder": "spam" if is_spam else "real_mails"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_folder_stats(source_dir):
    """
    Get statistics about emails in spam and real_mails folders.
    
    Returns:
        dict with counts for each folder
    """
    spam_folder = os.path.join(source_dir, "spam")
    real_folder = os.path.join(source_dir, "real_mails")
    
    spam_count = 0
    real_count = 0
    
    if os.path.exists(spam_folder):
        spam_count = len([f for f in os.listdir(spam_folder) if f.endswith(".eml")])
    
    if os.path.exists(real_folder):
        real_count = len([f for f in os.listdir(real_folder) if f.endswith(".eml")])
    
    return {
        "spam_count": spam_count,
        "real_count": real_count,
        "total_classified": spam_count + real_count
    }
