"""
Safar — Itinerary Agent

Responsibilities:
- Generate a realistic day-by-day itinerary
- Incorporate destination research, budget, and weather
- Respect user's interests and food preferences
- Also generate food recommendations
"""

from __future__ import annotations

import logging
import time
from pydantic import BaseModel, Field

from app.graph.state import TravelPlanState
from app.models.travel import Itinerary, FoodRecommendation
from app.models.responses import AgentExecution
from app.services.llm import generate_structured

logger = logging.getLogger(__name__)


class ItineraryWithFood(BaseModel):
    """Combined response model for itinerary + food recommendations."""
    itinerary: Itinerary
    food_recommendations: list[FoodRecommendation] = Field(default_factory=list)


def itinerary_planning(state: TravelPlanState) -> dict:
    """
    Generate the day-by-day itinerary and food recommendations.
    Uses destination info, budget, and weather from previous agents.
    """
    start = time.time()
    agent_name = "Itinerary Planner"

    try:
        request = state["travel_request"]
        destination_info = state.get("destination_info")
        budget = state.get("budget_breakdown")
        weather = state.get("weather_info")
        replan = state.get("replan_instruction")

        # Build context from previous agents
        dest_context = ""
        if destination_info:
            attractions = "\n".join(
                f"- {a.name} ({a.category}): {a.description} "
                f"[Cost: ₹{a.estimated_cost}, Duration: {a.recommended_duration}]"
                for a in destination_info.attractions
            )
            dest_context = f"""
DESTINATION RESEARCH:
{destination_info.overview}

Available Attractions:
{attractions}

Transport Options: {', '.join(destination_info.local_transport_options)}
"""

        budget_context = ""
        if budget:
            budget_context = f"""
BUDGET CONSTRAINTS:
Total budget: ₹{budget.user_budget:,.0f}
Estimated total: ₹{budget.total_estimated:,.0f}
Activities budget: ₹{sum(i.estimated_cost for i in budget.items if 'activit' in i.category.lower()):,.0f}
{'⚠ OVER BUDGET — prioritize free/cheap activities' if not budget.is_within_budget else 'Within budget'}
"""

        weather_context = ""
        if weather and weather.forecast:
            weather_lines = "\n".join(
                f"- {d.date}: {d.condition}, {d.temp_min_c:.0f}–{d.temp_max_c:.0f}°C"
                f"{', rain expected' if d.precipitation_mm > 1 else ''}"
                for d in weather.forecast[:request.days]
            )
            weather_context = f"""
WEATHER FORECAST:
{weather_lines}
Plan indoor activities for rainy days.
"""

        replan_note = ""
        if replan:
            replan_note = (
                f"\n\nIMPORTANT MODIFICATION REQUEST: "
                f'"{replan}". Adjust the itinerary to satisfy this request.'
            )

        prompt = f"""You are an expert travel itinerary planner. Create a detailed, realistic 
day-by-day itinerary.

DESTINATION: {request.destination}
DAYS: {request.days}
TRAVELERS: {request.travelers}
TRAVEL STYLE: {request.travel_style}
INTERESTS: {", ".join(request.interests) if request.interests else "general sightseeing"}
FOOD PREFERENCE: {request.food_preference}
{dest_context}
{budget_context}
{weather_context}
{replan_note}

CREATE:

1. ITINERARY: A day-by-day plan with:
   - day_number (1 to {request.days})
   - title: A catchy title for the day (e.g., "Beach Day & Sunset Vibes")
   - activities: 4-6 activities per day, each with:
     - time (e.g., "9:00 AM")
     - title (activity name)
     - description (1-2 sentences)
     - location (specific place name)
     - duration (e.g., "2 hours")
     - estimated_cost in INR (for all {request.travelers} travelers)
     - category (sightseeing/food/adventure/culture/shopping/relaxation)
   - general_tips: 3-5 practical tips for the trip

2. FOOD RECOMMENDATIONS: 5-8 food recommendations with:
   - name (dish or restaurant)
   - category (Street Food / Casual Dining / Fine Dining / Cafe / Local Specialty)
   - cuisine type
   - description
   - price_range (e.g., "₹100-300 per person")
   - is_vegetarian (boolean — mark true if suitable for {request.food_preference})
   - location_hint (area or street name)

Rules:
- Schedule activities in logical geographic order (minimize travel time)
- Include breakfast, lunch, and dinner slots
- Don't overschedule — leave breathing room
- Respect the weather forecast — indoor activities on rainy days
- All places must be REAL locations
- First day should start easy (arrival), last day allow time for departure
- Match the {request.travel_style} style
"""

        result = generate_structured(prompt, ItineraryWithFood)

        logger.info(
            f"[{agent_name}] Created {len(result.itinerary.days)}-day itinerary "
            f"with {len(result.food_recommendations)} food recommendations."
        )

        return {
            "itinerary": result.itinerary,
            "food_recommendations": result.food_recommendations,
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
