# SEC Insight: AI-Powered Market Intelligence

A real-time web application that tracks public company filings (SEC EDGAR) and uses **Google Gemini 3** (via `google-genai`) to extract actionable market insights.

## Features
- **Real-time Tracking**: Monitors SEC 8-K and 10-K filings.
- **AI Analysis**: Automatically analyzes filings for "Actionable Market Information" using Gemini.
- **Modern Dashboard**: Built with Svelte and Tailwind CSS (Glassmorphism design).
- **Background Monitoring**: Python FastAPI backend with async schedulers.

## Project Structure
- `backend/`: Python FastAPI application (Scraper, Analyzer, API).
- `frontend/`: Svelte + Vite application.

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API Key

### Backend Setup
1. Navigate to `backend/`.
2. Create virtual env: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Create `.env` file and add: `GOOGLE_API_KEY=your_key_here`.
5. Run server: `python -m uvicorn main:app --reload`.

### Frontend Setup
1. Navigate to `frontend/`.
2. Install: `npm install`.
3. Run dev server: `npm run dev`.

Open `http://localhost:5173` to use the app.
