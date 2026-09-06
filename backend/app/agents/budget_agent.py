"""
Safar — Budget Agent

Responsibilities:
- Estimate all travel costs based on destination, style, and duration
- Produce itemized budget breakdown
- Compare with user's budget
- Flag over-budget situations
- Suggest cost-saving strategies
"""

from __future__ import annotations

import logging
import time

from app.graph.state import TravelPlanState
from app.models.travel import BudgetBreakdown
from app.models.responses import AgentExecution
from app.services.llm import generate_structured

logger = logging.getLogger(__name__)


def budget_analysis(state: TravelPlanState) -> dict:
    """
    Analyze the budget based on destination research and user constraints.
    Returns budget_breakdown for the shared state.
    """
    start = time.time()
    agent_name = "Budget Analyst"

    try:
        request = state["travel_request"]
        destination_info = state.get("destination_info")
        replan = state.get("replan_instruction")

        # Build context from destination research
        destination_context = ""
        if destination_info:
            attractions_list = "\n".join(
                f"- {a.name} (entry: ₹{a.estimated_cost})"
                for a in destination_info.attractions
            )
            transport_list = ", ".join(destination_info.local_transport_options) or "various options"
            destination_context = f"""
DESTINATION RESEARCH AVAILABLE:
Location: {destination_info.destination_name}
Currency: {destination_info.currency}
Attractions:
{attractions_list}
Transport options: {transport_list}
"""

        replan_note = ""
        if replan:
            replan_note = (
                f"\n\nNOTE: The user has requested a modification: "
                f'"{replan}". Adjust the budget accordingly.'
            )

        prompt = f"""You are a travel budget analyst. Create a detailed, realistic budget breakdown 
for this trip.

DESTINATION: {request.destination}
NUMBER OF DAYS: {request.days}
TRAVELERS: {request.travelers}
TRAVEL STYLE: {request.travel_style}
USER BUDGET: ₹{request.budget:,.0f} (total for all travelers)
FOOD PREFERENCE: {request.food_preference}
INTERESTS: {", ".join(request.interests) if request.interests else "general"}
{destination_context}
{replan_note}

Create an itemized budget with these categories:
1. Accommodation (for {request.days} nights)
2. Food & Dining (for {request.days} days, {request.travelers} people)
3. Local Transportation (within destination)
4. Activities & Attractions (entry fees, tours, etc.)
5. Miscellaneous (tips, souvenirs, emergency buffer)

For each category provide:
- Realistic estimated cost in INR for ALL travelers combined
- Brief notes explaining the estimate

Also provide:
- total_estimated: sum of all items
- per_person: total / {request.travelers}
- user_budget: {request.budget}
- is_within_budget: whether total <= user budget
- savings_tips: at least 3 practical ways to reduce costs if over budget
- budget_warning: a warning message if significantly over budget, empty string if within budget

Prices must be realistic for {request.destination} with a {request.travel_style} travel style.
Do NOT underestimate costs — be practical.
"""

        budget = generate_structured(prompt, BudgetBreakdown)

        # Ensure user_budget is set correctly
        budget.user_budget = request.budget
        budget.is_within_budget = budget.total_estimated <= request.budget

        logger.info(
            f"[{agent_name}] Budget: ₹{budget.total_estimated:,.0f} "
            f"vs user budget ₹{request.budget:,.0f} "
            f"({'within' if budget.is_within_budget else 'OVER'} budget)"
        )

        return {
            "budget_breakdown": budget,
            "agent_executions": [
                AgentExecution(
                    agent_name=agent_name,
                    status="completed",
                    duration_seconds=time.time() - start,
                )
            ],
        }

    except Exception as e:
        logger.error(f"[{agent_name}] Error: {e}")
        return {
            "errors": [f"[{agent_name}] {str(e)}"],
            "agent_executions": [
                AgentExecution(
                    agent_name=agent_name,
                    status="failed",
                    duration_seconds=time.time() - start,
                    error=str(e),
                )
            ],
        }
