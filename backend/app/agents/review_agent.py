"""
Safar — Review Agent

Responsibilities:
- Review all agent outputs for consistency
- Check budget alignment
- Check itinerary realism
- Identify contradictions or missing information
- Return structured validation result
"""

from __future__ import annotations

import logging
import time

from app.graph.state import TravelPlanState
from app.models.travel import ReviewResult
from app.models.responses import AgentExecution
from app.services.llm import generate_structured

logger = logging.getLogger(__name__)


def review_plan(state: TravelPlanState) -> dict:
    """
    Review all agent outputs for quality, consistency, and completeness.
    Returns review_result for the shared state.
    """
    start = time.time()
    agent_name = "Review Agent"

    try:
        request = state["travel_request"]
        destination_info = state.get("destination_info")
        budget = state.get("budget_breakdown")
        itinerary = state.get("itinerary")
        weather = state.get("weather_info")
        food_recs = state.get("food_recommendations", [])

        # Build a summary of all outputs for review
        dest_summary = "NOT AVAILABLE"
        if destination_info:
            dest_summary = (
                f"Destination: {destination_info.destination_name}\n"
                f"Attractions: {len(destination_info.attractions)} found\n"
                f"Overview length: {len(destination_info.overview)} chars"
            )

        budget_summary = "NOT AVAILABLE"
        if budget:
            budget_summary = (
                f"Total estimated: ₹{budget.total_estimated:,.0f}\n"
                f"User budget: ₹{budget.user_budget:,.0f}\n"
                f"Within budget: {budget.is_within_budget}\n"
                f"Categories: {len(budget.items)}\n"
                f"Savings tips: {len(budget.savings_tips)}"
            )

        itinerary_summary = "NOT AVAILABLE"
        if itinerary:
            total_activities = sum(len(d.activities) for d in itinerary.days)
            itinerary_summary = (
                f"Days planned: {len(itinerary.days)}\n"
                f"Total activities: {total_activities}\n"
                f"Days expected: {request.days}"
            )

        weather_summary = "NOT AVAILABLE"
        if weather:
            weather_summary = (
                f"Forecast days: {len(weather.forecast)}\n"
                f"Is fallback: {weather.is_fallback}\n"
                f"Summary: {weather.summary}"
            )

        food_summary = f"{len(food_recs)} recommendations" if food_recs else "NOT AVAILABLE"

        prompt = f"""You are a travel plan quality reviewer. Carefully review all the outputs from the 
planning team and check for quality, consistency, and completeness.

ORIGINAL REQUEST:
- Destination: {request.destination}
- Days: {request.days}
- Travelers: {request.travelers}
- Budget: ₹{request.budget:,.0f}
- Travel Style: {request.travel_style}
- Interests: {", ".join(request.interests) if request.interests else "general"}
- Food Preference: {request.food_preference}

DESTINATION RESEARCH OUTPUT:
{dest_summary}

BUDGET ANALYSIS OUTPUT:
{budget_summary}

ITINERARY OUTPUT:
{itinerary_summary}

WEATHER OUTPUT:
{weather_summary}

FOOD RECOMMENDATIONS:
{food_summary}

Perform these checks and report on each:

1. "Destination Coverage" — Does the research cover the requested destination adequately?
2. "Budget Alignment" — Is the estimated budget reasonable? Does it match the travel style?
3. "Itinerary Completeness" — Are all {request.days} days covered with activities?
4. "Interest Matching" — Do the activities match the user's stated interests?
5. "Schedule Realism" — Is the daily schedule realistic (not overpacked, logical order)?
6. "Food Preference Respected" — Are food recommendations compatible with {request.food_preference}?
7. "Weather Consideration" — Is weather accounted for in the itinerary?

For each check provide:
- check_name: the name
- passed: true/false
- details: brief explanation

Also provide:
- overall_score: 1-10 quality rating
- issues: list of specific problems found (can be empty)
- suggestions: list of improvement suggestions (can be empty)
- approved: true if overall_score >= 6 and no critical issues
"""

        review = generate_structured(prompt, ReviewResult)

        logger.info(
            f"[{agent_name}] Score: {review.overall_score}/10, "
            f"Approved: {review.approved}, "
            f"Issues: {len(review.issues)}"
        )

        return {
            "review_result": review,
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
        # If review fails, create a fallback review that passes
        # (don't block the entire plan because review crashed)
        return {
            "review_result": ReviewResult(
                overall_score=5,
                checks=[],
                issues=[f"Review agent encountered an error: {str(e)}"],
                suggestions=["Please manually review the plan"],
                approved=True,
            ),
            "agent_executions": [
                AgentExecution(
                    agent_name=agent_name,
                    status="failed",
                    duration_seconds=time.time() - start,
                    error=str(e),
                )
            ],
        }
