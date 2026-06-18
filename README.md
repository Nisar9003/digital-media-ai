# Digital Media AI Agent System

## Quick Start

### 1. Database setup
```bash
psql -U postgres -d digital_media_ai -f backend/db/migrations/001_init.sql
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
cp .env .env.local   # fill in your API keys
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev   # runs on localhost:3000
```

## Publishers
| Platform  | File                        | API Docs |
|-----------|-----------------------------|----------|
| LinkedIn  | publisher/linkedin.py       | LinkedIn UGC API |
| Instagram | publisher/instagram.py      | Meta Graph API |
| Facebook  | publisher/facebook.py       | Meta Graph API |
| TikTok    | publisher/tiktok.py         | TikTok Content Posting API |
| Ayrshare  | publisher/ayrshare.py       | Free tier fallback |
