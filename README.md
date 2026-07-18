# 🧠 NutriMind AI – Smart Food & Health Companion

> An AI-first, predictive, personalized nutrition and health platform.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                   │
│  Dashboard │ Chatbot │ Scanner │ Planner │ Social        │
└─────────────────────┬───────────────────────────────────┘
                      │ REST + WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                   BACKEND (FastAPI)                       │
│  Auth │ Food API │ AI Engine │ Health │ Notifications    │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
  PostgreSQL  MongoDB    Redis      AI Services
  (users,     (food      (cache,    (LLM, CV,
   health)     logs)      sessions)  ML models)
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

### Run with Docker
```bash
docker-compose up --build
```

### Manual Setup

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🧩 Core Features

| Feature | Status |
|---|---|
| Smart Food Recommendations | ✅ |
| AI Food Scanner (Image) | ✅ |
| Health Chatbot (LLM) | ✅ |
| Personal Health Dashboard | ✅ |
| Predictive Health Insights | ✅ |
| Context-Aware Suggestions | ✅ |
| Habit Building System | ✅ |
| Smart Grocery Planner | ✅ |
| Health Risk Alerts | ✅ |
| Social & Gamification | ✅ |
| Emotion-Aware Eating | ✅ |
| Voice Input | ✅ |
| Explainable AI | ✅ |
| Sustainability Score | ✅ |

## 📁 Project Structure

```
nutrimind-ai/
├── frontend/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/             # Login/Register
│   │   ├── dashboard/          # Main dashboard
│   │   ├── scanner/            # Food scanner
│   │   ├── chatbot/            # AI chatbot
│   │   ├── planner/            # Meal & grocery planner
│   │   ├── habits/             # Habit tracker
│   │   └── social/             # Community
│   ├── components/             # Reusable UI components
│   ├── lib/                    # API clients, utils
│   └── store/                  # Zustand state management
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routers/                # API route handlers
│   ├── models/                 # DB models (SQLAlchemy)
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── ai/                     # AI/ML modules
├── ai/
│   ├── recommendation/         # Collaborative + content filtering
│   ├── food_detection/         # Computer vision
│   ├── chatbot/                # LLM integration
│   └── predictive/             # Time-series health predictions
└── docker-compose.yml
```

## 🔑 Environment Variables

See `.env.example` in each subdirectory.

## 📄 License
MIT
