import os
from email_parser import parse_eml
from spam_detector import detect_spam
from file_mover import copy_email_with_reason
from database import init_db, log_analysis, get_analysis_history, get_stats

def print_header():
    print("\n" + "="*60)
    print("🛡️  AI SPAM DETECTOR - CLI VERSION")
    print("="*60 + "\n")

def print_email_details(parsed):
    print("\n📧 EMAIL DETAILS:")
    print("-" * 60)
    print(f"From:    {parsed['from']}")
    print(f"To:      {parsed['to']}")
    print(f"Subject: {parsed['subject']}")
    print("-" * 60)
    print("\n📄 CONTENT:")
    print(parsed['body'][:500] + "..." if len(parsed['body']) > 500 else parsed['body'])
    print("-" * 60)

def print_analysis_result(spam_result):
    print("\n🔍 AI ANALYSIS RESULT:")
    print("=" * 60)
    
    if spam_result["is_spam"]:
        print(f"⚠️  {spam_result['classification']} ({spam_result['confidence']}% confidence)")
        print(f"\n💬 Reason: {spam_result['reason']}")
        print("\n🚨 SECURITY WARNINGS:")
        print("   🚫 DO NOT RESPOND to this email!")
        print("   ⚠️  DO NOT CLICK any links!")
        print("   ⚠️  DO NOT SHARE personal information!")
    else:
        print(f"✅ {spam_result['classification']} ({spam_result['confidence']}% confidence)")
        print(f"\n💬 Reason: {spam_result['reason']}")
        print("\n✅ STATUS: This email appears to be safe")
        print("   👍 VERIFY SENDER - Double check the email address if unsure")
        print("   🔒 STAY CAUTIOUS - Still avoid sharing sensitive data")
    
    print("=" * 60)

def print_stats():
    stats = get_stats()
    print("\n📊 OVERALL STATISTICS:")
    print("-" * 60)
    print(f"🚨 Spam Detected:      {stats['spam_count']}")
    print(f"✅ Legitimate Emails:  {stats['real_count']}")
    print(f"📊 Total Analyzed:     {stats['total']}")
    print("-" * 60)

def print_history(limit=10):
    history = get_analysis_history(limit=limit)
    
    if not history:
        print("\n📋 No analysis history yet.")
        return
    
    print(f"\n📋 RECENT ANALYSIS HISTORY (Last {limit}):")
    print("=" * 60)
    
    for record in history:
        status_icon = "🚨" if record["is_spam"] else "✅"
        timestamp = record["timestamp"].split("T")[0] + " " + record["timestamp"].split("T")[1][:8]
        
        print(f"\n{status_icon} {record['classification']} ({record['confidence']}% confidence)")
        print(f"   File: {record['email_filename']}")
        print(f"   From: {record['sender']}")
        print(f"   Time: {timestamp}")
        print(f"   Folder: {record['copied_to_folder']}/")
        print(f"   Reason: {record['reason']}")
        print("-" * 60)

def main():
    # Initialize database
    init_db()
    
    # Get current directory and mails folder
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    MAILS_FOLDER = os.path.join(CURRENT_DIR, "mails")
    
    # Get list of .eml files
    if not os.path.exists(MAILS_FOLDER):
        print("❌ Error: 'mails' folder not found!")
        return
    
    email_files = [f for f in os.listdir(MAILS_FOLDER) if f.endswith(".eml")]
    
    if not email_files:
        print("⚠️  No emails found in 'mails' folder!")
        return
    
    while True:
        print_header()
        print_stats()
        
        print("\n📧 AVAILABLE EMAILS:")
        for i, email_file in enumerate(email_files, 1):
            print(f"   {i}. {email_file}")
        
        print("\n📋 OPTIONS:")
        print("   h - View analysis history")
        print("   q - Quit")
        
        choice = input("\n👉 Select email number (or option): ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Goodbye!\n")
            break
        
        if choice == 'h':
            print_history(limit=20)
            input("\nPress Enter to continue...")
            continue
        
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(email_files):
                print("❌ Invalid selection!")
                input("\nPress Enter to continue...")
                continue
            
            selected_email = email_files[index]
            email_path = os.path.join(MAILS_FOLDER, selected_email)
            
            # Parse email
            print(f"\n📖 Reading {selected_email}...")
            parsed = parse_eml(email_path)
            print_email_details(parsed)
            
            # Analyze
            print("\n🤖 Analyzing with AI...")
            spam_result = detect_spam(parsed)
            print_analysis_result(spam_result)
            
            # Copy to folder
            print(f"\n📁 Copying to {'spam' if spam_result['is_spam'] else 'real_mails'} folder...")
            copy_result = copy_email_with_reason(
                email_filename=selected_email,
                is_spam=spam_result["is_spam"],
                reason=spam_result["reason"],
                source_dir=MAILS_FOLDER
            )
            
            if copy_result.get("success"):
                print(f"✅ Saved to: {copy_result['folder']}/")
            
            # Log to database
            log_analysis(selected_email, parsed, spam_result, copy_result)
            print("✅ Logged to database")
            
            input("\nPress Enter to continue...")
            
        except ValueError:
            print("❌ Invalid input! Please enter a number.")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
