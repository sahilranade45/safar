"""
Safar — LangGraph Shared State

TypedDict defining the shared state that flows through
the entire agent pipeline. Each agent reads from and writes
to this state.
"""

from __future__ import annotations
from typing import TypedDict, Optional, Annotated
import operator

from app.models.travel import (
    TravelRequest,
    DestinationInfo,
    WeatherInfo,
    BudgetBreakdown,
    Itinerary,
    FoodRecommendation,
    ReviewResult,
    FinalPlan,
)
from app.models.responses import AgentExecution


def _replace(existing, new):
    """Reducer that replaces the old value with the new one."""
    return new


class TravelPlanState(TypedDict, total=False):
    """
    Shared state for the LangGraph travel planning workflow.

    Each field is populated by a specific agent:
    - travel_request:    Set at the start from user input
    - destination_info:  Set by Destination Research Agent
    - weather_info:      Set by Destination Research Agent (via weather tool)
    - budget_breakdown:  Set by Budget Agent
    - itinerary:         Set by Itinerary Agent
    - food_recommendations: Set by Itinerary Agent
    - review_result:     Set by Review Agent
    - final_plan:        Set by Coordinator (finalize step)
    - agent_executions:  Accumulated by each agent
    - errors:            Accumulated error messages
    - replan_instruction: Set when replanning
    """

    # --- Input ---
    travel_request: Annotated[Optional[TravelRequest], _replace]

    # --- Agent Outputs ---
    destination_info: Annotated[Optional[DestinationInfo], _replace]
    weather_info: Annotated[Optional[WeatherInfo], _replace]
    budget_breakdown: Annotated[Optional[BudgetBreakdown], _replace]
    itinerary: Annotated[Optional[Itinerary], _replace]
    food_recommendations: Annotated[Optional[list[FoodRecommendation]], _replace]
    review_result: Annotated[Optional[ReviewResult], _replace]
    final_plan: Annotated[Optional[FinalPlan], _replace]

    # --- Metadata ---
    agent_executions: Annotated[list[AgentExecution], operator.add]
    errors: Annotated[list[str], operator.add]

    # --- Replanning ---
    replan_instruction: Annotated[Optional[str], _replace]
