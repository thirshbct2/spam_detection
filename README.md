# Email Spam Detector

Simple AI-powered spam detection system that keeps all emails in one place.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your OpenAI API key to `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the app:
```bash
streamlit run streamlit_app.py
```

## How It Works

- All 5 emails stay in `mails/` folder permanently
- Select any email to analyze with AI
- AI detects if it's spam or legitimate
- Click button to copy results to `spam/` or `real_mails/` folder
- Original emails always remain in `mails/` folder
- You can re-analyze any email anytime

## Folder Structure

```
spam_mail_analyzer/
├── mails/              # All 5 emails always here
├── spam/               # Spam copies + reason files (created automatically)
└── real_mails/         # Real email copies + reason files (created automatically)
```

## Features

- ✅ All emails stay in mails folder
- ✅ AI-powered spam detection
- ✅ Automatic classification
- ✅ Reason files saved with each detection
- ✅ Simple one-click operation
