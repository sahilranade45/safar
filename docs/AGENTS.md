# Safar — Agent Design & Specification 🤖

Safar deploys **5 specialized autonomous AI agents**. Each agent is an isolated module executing specific tasks and updating the shared state.

---

## 1. Coordinator Agent (`app/agents/coordinator.py`)

### Responsibilities
- Entry point node of the LangGraph state machine.
- Validates the incoming `TravelRequest`.
- Normalizes destination names, budget values, and date ranges.
- Logs step start to `execution_trace`.

### Input / Output
- **Input**: `state["request"]`
- **Output**: Initialized `execution_trace`, updated status.

---

## 2. Destination Agent (`app/agents/destination.py`)

### Responsibilities
- Interrogates external geocoding and Open-Meteo weather tools for real-time 7-day forecast data.
- Generates high-level local insights, cultural tips, best areas to stay, and local customs.

### Input / Output
- **Input**: `destination`, `travel_style`, `interests`
- **Output**: `state["destination_info"]`, `state["weather_info"]`

---

## 3. Budget Agent (`app/agents/budget.py`)

### Responsibilities
- Calculates itemized allocations across 4 core categories:
  1. **Accommodation** (Hotels, Hostels, Resorts)
  2. **Food & Dining** (Street food, Mid-range dining, Fine dining)
  3. **Activities & Attractions** (Tickets, Guided tours, Entry fees)
  4. **Transport & Buffer** (Local transit, Taxis, Emergency fund)
- Adjusts estimates based on user budget ($ and currency), number of travelers, and trip duration.
- Provides actionable cost-saving tips tailored to the destination.

### Input / Output
- **Input**: `budget`, `currency`, `travelers`, `duration_days`, `travel_style`
- **Output**: `state["budget_breakdown"]`

---

## 4. Itinerary Agent (`app/agents/itinerary.py`)

### Responsibilities
- Generates day-by-day micro-schedules (`Day 1` through `Day N`).
- Breaks each day into:
  - **Morning Activity**
  - **Afternoon Activity**
  - **Evening Activity**
  - **Food Recommendations** (Breakfast, Lunch, Dinner)
  - **Logistics & Transit Tip**
- Adapts to replanning feedback (e.g. slowing down pace, adding family-friendly venues).

### Input / Output
- **Input**: `duration_days`, `interests`, `food_preference`, `destination_info`
- **Output**: `state["daily_itinerary"]`

---

## 5. Review Agent (`app/agents/review.py`)

### Responsibilities
- Acts as Quality Assurance for the compiled plan.
- Performs checks on:
  - **Budget Compliance**: Do itemized costs exceed total budget?
  - **Pacing & Realism**: Is the schedule overly congested?
  - **Seasonal / Weather Alignment**: Are outdoor activities scheduled during rain/storms?
  - **Safety & Cultural Considerations**: Are local tips incorporated?
- Assigns an overall score (`0–100`) and provides constructive recommendations.

### Input / Output
- **Input**: Full compiled state (`destination_info`, `budget_breakdown`, `daily_itinerary`, `weather_info`)
- **Output**: `state["review_output"]` (score, issues, recommendations, passed_review boolean)
