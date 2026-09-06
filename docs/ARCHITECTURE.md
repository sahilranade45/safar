# Safar — System Architecture & Workflow 🏗️

## 1. System Overview

Safar is built using a decoupled architecture separating the **Agentic Orchestration Engine (FastAPI + LangGraph)** from the **Presentation Layer (React + Vite)**.

```
+-----------------------------------------------------------------------+
|                           REACT FRONTEND                              |
|  [ TripForm ] ----> [ AgentProgress ] ----> [ TravelPlan / Replan ]   |
+-----------------------------------+-----------------------------------+
                                    | REST API Calls (Axios)
                                    v
+-----------------------------------------------------------------------+
|                           FASTAPI BACKEND                             |
|  POST /api/plan/generate                     POST /api/plan/replan    |
+-----------------------------------+-----------------------------------+
                                    | State Machine Execution
                                    v
+-----------------------------------------------------------------------+
|                         LANGGRAPH AGENT GRAPH                         |
|                                                                       |
|  State: TravelPlanState (TypedDict)                                    |
|                                                                       |
|  [START]                                                              |
|     |                                                                 |
|     v                                                                 |
|  Coordinator Node --------> (Validates Request & Seeds State)         |
|     |                                                                 |
|     v                                                                 |
|  Destination Node --------> (Open-Meteo Tool + LLM Insights)          |
|     |                                                                 |
|     v                                                                 |
|  Budget Node -------------> (Financial Allocation & Itemization)       |
|     |                                                                 |
|     v                                                                 |
|  Itinerary Node ----------> (Day-by-Day Micro-Scheduling)             |
|     |                                                                 |
|     v                                                                 |
|  Review Node -------------> (Feasibility Verification & Score 0-100)  |
|     |                                                                 |
|     v                                                                 |
|   [END]                                                               |
+-----------------------------------------------------------------------+
```

---

## 2. LangGraph State Management

All data exchanged between agents is tracked in a single, mutable `TravelPlanState` dictionary:

```python
class TravelPlanState(TypedDict):
    request: Dict[str, Any]                # Initial User Input
    replan_feedback: Optional[str]        # Feedback for replanning
    is_replan: bool                       # Workflow mode flag
    destination_info: Optional[Dict]      # Destination Agent Output
    weather_info: Optional[Dict]          # Open-Meteo Weather Tool Output
    budget_breakdown: Optional[Dict]      # Budget Agent Output
    daily_itinerary: Optional[List[Dict]] # Itinerary Agent Output
    review_output: Optional[Dict]         # Review Agent Output
    execution_trace: List[Dict]           # Timestamps & Execution Log
    errors: List[str]                     # Accumulated warnings/errors
    status: str                           # Overall status string
```

---

## 3. Communication Patterns & Error Fallbacks

1. **Structured LLM Parsing**:
   Agents utilize `PydanticOutputParser` combined with strict JSON formatting prompts to guarantee deterministic structure from Google Gemini (`gemini-2.5-flash`).

2. **Fault Tolerance**:
   If an agent's LLM invocation fails or returns invalid JSON after retries, the agent records the error into `state["errors"]` and populates a safe, structured fallback object. The graph workflow does NOT break or panic.

3. **External Tools Integration**:
   The `DestinationAgent` connects asynchronously to Open-Meteo (`https://api.open-meteo.com/v1/forecast`) and Geocoding API (`https://geocoding-api.open-meteo.com/v1/search`). If Open-Meteo is unavailable or the destination is unmapped, fallback seasonal weather defaults are injected without breaking graph execution.

---

## 4. Human-in-the-Loop Replanning Flow

```
User feedback: "Increase food budget by 20%, slow down pace"
                        |
                        v
               POST /api/plan/replan
                        |
                        v
           Inject feedback into state
                        |
                        v
          LangGraph Workflow Execution
       [Budget Agent] updates breakdown
       [Itinerary Agent] adjusts pacing
       [Review Agent] validates score
                        |
                        v
           Updated Plan Returned to UI
```
