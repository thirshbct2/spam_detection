import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "spam_detector.db")

def print_table(rows, headers):
    """Print data in a formatted table"""
    if not rows:
        print("No data found.")
        return
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    
    # Print header
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print("\n" + header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(val).ljust(w) for val, w in zip(row, col_widths)))

def view_all_records():
    """View all records in analysis_log table"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM analysis_log ORDER BY id DESC")
    rows = cursor.fetchall()
    
    headers = ["ID", "Timestamp", "Email", "Sender", "Subject", "Classification", "Spam", "Confidence", "Reason", "Folder", "Success"]
    
    print("\n" + "="*150)
    print("📊 SPAM DETECTOR DATABASE - ALL RECORDS")
    print("="*150)
    
    print_table(rows, headers)
    
    print(f"\n📈 Total Records: {len(rows)}")
    
    conn.close()

def view_summary():
    """View summary statistics"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 DATABASE SUMMARY")
    print("="*60)
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM analysis_log")
    total = cursor.fetchone()[0]
    print(f"\n📋 Total Analyses: {total}")
    
    # Spam count
    cursor.execute("SELECT COUNT(*) FROM analysis_log WHERE is_spam = 1")
    spam_count = cursor.fetchone()[0]
    print(f"🚨 Spam Detected: {spam_count}")
    
    # Legitimate count
    cursor.execute("SELECT COUNT(*) FROM analysis_log WHERE is_spam = 0")
    real_count = cursor.fetchone()[0]
    print(f"✅ Legitimate: {real_count}")
    
    # Average confidence
    cursor.execute("SELECT AVG(confidence) FROM analysis_log")
    avg_conf = cursor.fetchone()[0]
    if avg_conf:
        print(f"📊 Average Confidence: {avg_conf:.1f}%")
    
    # Most analyzed email
    cursor.execute("""
        SELECT email_filename, COUNT(*) as count 
        FROM analysis_log 
        GROUP BY email_filename 
        ORDER BY count DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        print(f"\n🔝 Most Analyzed Email: {result[0]} ({result[1]} times)")
    
    # Recent activity
    cursor.execute("""
        SELECT email_filename, classification, confidence, timestamp 
        FROM analysis_log 
        ORDER BY id DESC 
        LIMIT 5
    """)
    recent = cursor.fetchall()
    
    if recent:
        print("\n📅 Recent Activity (Last 5):")
        print("-" * 60)
        for r in recent:
            timestamp = r[3].split("T")[0] + " " + r[3].split("T")[1][:8]
            print(f"   {r[1]} ({r[2]}%) - {r[0]} - {timestamp}")
    
    print("="*60 + "\n")
    
    conn.close()

def view_by_email():
    """View records grouped by email"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT email_filename, COUNT(*) as analyses, 
               AVG(confidence) as avg_conf,
               MAX(timestamp) as last_analyzed
        FROM analysis_log
        GROUP BY email_filename
        ORDER BY analyses DESC
    """)
    rows = cursor.fetchall()
    
    print("\n" + "="*100)
    print("📧 ANALYSIS BY EMAIL")
    print("="*100)
    
    headers = ["Email Filename", "Times Analyzed", "Avg Confidence", "Last Analyzed"]
    print_table(rows, headers)
    
    conn.close()

def main():
    while True:
        print("\n" + "="*60)
        print("🗄️  SPAM DETECTOR DATABASE VIEWER")
        print("="*60)
        print("\nOptions:")
        print("  1 - View all records")
        print("  2 - View summary statistics")
        print("  3 - View by email")
        print("  4 - Run custom SQL query")
        print("  q - Quit")
        
        choice = input("\n👉 Select option: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Goodbye!\n")
            break
        elif choice == '1':
            view_all_records()
        elif choice == '2':
            view_summary()
        elif choice == '3':
            view_by_email()
        elif choice == '4':
            query = input("\n📝 Enter SQL query: ").strip()
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    headers = [desc[0] for desc in cursor.description]
                    print_table(rows, headers)
                else:
                    print("✅ Query executed successfully (no results)")
                
                conn.close()
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print("❌ Invalid option!")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
