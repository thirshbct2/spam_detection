import os
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Spam Detection Prompt Template
spam_detection_template = PromptTemplate(
    input_variables=["email_content", "subject", "sender"],
    template="""
You are a cybersecurity expert specializing in spam and phishing detection.

Analyze the following email:

From: {sender}
Subject: {subject}
Content: {email_content}

Determine if this email is:
- SPAM/PHISHING (fraudulent, dangerous, or malicious)
- LEGITIMATE (real, safe, genuine)

SPAM/PHISHING indicators to look for:
1. Urgent or threatening language ("within 24 hours", "act now", "limited time")
2. Requests for personal/financial information
3. Suspicious sender email domain (misspellings, unusual TLDs like .co, .net instead of .com)
4. Generic greetings ("Dear Customer", "Dear User" instead of actual name)
5. Pressure to act immediately or face consequences
6. Suspicious links or URLs
7. Claims of account issues or delivery problems
8. Too-good-to-be-true offers
9. Poor grammar or spelling errors
10. Authority impersonation (banks, shipping companies, billing departments)

Respond in this EXACT format (keep reason to maximum 2 sentences):

Classification: [SPAM or LEGITIMATE]
Confidence: [0-100 number representing confidence percentage]
Reason: [Explain in 1-2 sentences why this is spam or legitimate]
    """
)

def detect_spam(parsed_email: dict) -> dict:
    """
    Detect if email is spam/phishing or legitimate.
    
    Returns:
        {
            "is_spam": True/False,
            "classification": "SPAM" or "LEGITIMATE",
            "confidence": 0-100,
            "reason": "Brief explanation"
        }
    """
    # Create chain
    chain = spam_detection_template | llm
    
    # Invoke LLM
    result = chain.invoke({
        "sender": parsed_email.get("from", "Unknown"),
        "subject": parsed_email.get("subject", "No Subject"),
        "email_content": parsed_email["body"]
    }).content.strip()
    
    # Parse the response
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    
    classification = ""
    confidence = 0
    reason = ""
    
    for line in lines:
        if line.startswith("Classification:"):
            classification = line.replace("Classification:", "").strip()
        elif line.startswith("Confidence:"):
            conf_str = line.replace("Confidence:", "").strip()
            try:
                confidence = int(''.join(filter(str.isdigit, conf_str)))
            except:
                confidence = 50  # Default if parsing fails
        elif line.startswith("Reason:"):
            reason = line.replace("Reason:", "").strip()
    
    is_spam = "SPAM" in classification.upper()
    
    return {
        "is_spam": is_spam,
        "classification": classification,
        "confidence": confidence,
        "reason": reason
    }