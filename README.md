# Safar — Multi-Agent AI Travel Planner 🌍✈️

> **Portfolio-Quality AI Engineering & Full-Stack Project**  
> An autonomous multi-agent travel planning system built with **FastAPI**, **LangGraph**, **Google Gemini AI**, and **React**.

---

## 🌟 Overview

**Safar** (Urdu/Hindi for *Journey*) is an end-to-end multi-agent AI web application designed to generate deeply personalized, realistic, and budget-aware travel itineraries. 

Unlike single-prompt ChatGPT responses, Safar coordinates **5 specialized AI agents** inside a controlled state machine workflow built on **LangGraph**. Each agent takes ownership of a distinct aspect of travel planning (insights, budgeting, scheduling, and overall quality validation).

---

## ✨ Key Features

- **🤖 Autonomous Multi-Agent Orchestration**:
  - **Coordinator Agent**: Validates request parameters and synthesizes agent outputs.
  - **Destination Agent**: Fetches real-time weather via Open-Meteo API and generates local insights, culture tips, and ideal visit windows.
  - **Budget Agent**: Computes granular itemized cost breakdowns (lodging, dining, activities, transport) aligned with user financial constraints.
  - **Itinerary Agent**: Generates day-by-day schedules with morning/afternoon/evening activities tailored to travel style and food preferences.
  - **Review Agent**: Evaluates the compiled travel plan for feasibility, budget compliance, pace, and safety, assigning a quality score (0–100).

- **🔄 Human-in-the-Loop Replanning**:
  - Don't like a specific aspect of the plan? Request target adjustments (e.g., *"Reduce lodging budget"*, *"Add more nature activities"*, *"Pace is too fast"*).
  - The graph re-executes affected agents autonomously while maintaining state history.

- **🌦️ Live Weather Integration**:
  - Live 7-day weather forecast integration powered by the free Open-Meteo API (no API key required).

- **🎨 Modern Dynamic UI**:
  - Built with React & Vite.
  - Features real-time visual step execution tracking, dark mode aesthetics, glassmorphism cards, interactive weather badges, budget breakdowns, and printable PDF / copy views.

---

## 🛠️ Architecture Overview

```
                        +----------------------+
                        |   User Request (UI)  |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |   FastAPI REST API   |
                        +----------+-----------+
                                   |
                                   v
             +--------------------------------------------+
             |            LangGraph Workflow              |
             |                                            |
             |  [Coordinator Agent] (Input Validation)    |
             |          |                                 |
             |          +--> [Destination Agent]          |
             |          |     + Open-Meteo Weather Tool   |
             |          |                                 |
             |          +--> [Budget Agent]               |
             |          |                                 |
             |          +--> [Itinerary Agent]            |
             |          |                                 |
             |          v                                 |
             |  [Review Agent] (Feasibility Check & Score)|
             +--------------------------------------------+
                                   |
                                   v
                        +----------------------+
                        | Compiled Travel Plan |
                        +----------------------+
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Google Gemini API Key** ([Get a key from Google AI Studio](https://aistudio.google.com/))

---

### 1. Environment Setup

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=8000
VITE_API_BASE_URL=http://localhost:8000
```

---

### 2. Backend Setup

Navigate to the `backend` directory, create a virtual environment, and install dependencies:

```bash
# Windows
cd backend
python -m venv ..\.venv
..\.venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend API Interactive Docs will be live at: `http://localhost:8000/docs`

---

### 3. Frontend Setup

In a new terminal window, navigate to `frontend` and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Open your browser at: `http://localhost:5173`

---

## 🧪 Running Tests

Safar includes automated test coverage for data validation models, agent state structures, mock HTTP weather tools, and FastAPI endpoints.

To run the full backend test suite:

```bash
cd backend
python -m pytest
```

---

## 📁 Repository Structure

```
safar/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── backend/
│   ├── app/
│   │   ├── agents/           # Specialized LangGraph agent implementations
│   │   │   ├── coordinator.py
│   │   │   ├── destination.py
│   │   │   ├── budget.py
│   │   │   ├── itinerary.py
│   │   │   └── review.py
│   │   ├── graph/            # LangGraph State & Workflow Builder
│   │   │   ├── state.py
│   │   │   └── workflow.py
│   │   ├── models/           # Pydantic Schemas & Domain Models
│   │   │   ├── travel.py
│   │   │   └── responses.py
│   │   ├── services/         # LLM Service Wrappers & Providers
│   │   │   └── llm.py
│   │   ├── tools/            # External APIs (Weather, Geocoding)
│   │   │   └── weather.py
│   │   ├── utils/            # Helper utilities
│   │   ├── config.py         # App configuration & settings
│   │   └── main.py           # FastAPI application & REST endpoints
│   ├── tests/                # Pytest unit & integration test suites
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios HTTP API client
│   │   ├── components/       # React UI Components
│   │   │   ├── TripForm.jsx
│   │   │   ├── AgentProgress.jsx
│   │   │   ├── TravelPlan.jsx
│   │   │   └── ReplanPanel.jsx
│   │   ├── App.jsx           # Application State & View Routing
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Styling system & dark theme tokens
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── docs/                     # Architecture & Agent Specification Docs
    ├── ARCHITECTURE.md
    └── AGENTS.md
```

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
