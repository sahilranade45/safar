"""
Safar — Destination Research Agent

Responsibilities:
- Analyze the destination
- Identify major attractions matching user interests
- Fetch real weather data
- Produce structured DestinationInfo
"""

from __future__ import annotations

import asyncio
import logging
import time

from app.graph.state import TravelPlanState
from app.models.travel import DestinationInfo
from app.models.responses import AgentExecution
from app.services.llm import generate_structured
from app.tools.weather import get_weather

logger = logging.getLogger(__name__)


def destination_research(state: TravelPlanState) -> dict:
    """
    Research the destination and fetch weather data.
    Returns destination_info and weather_info for the shared state.
    """
    start = time.time()
    agent_name = "Destination Research"

    try:
        request = state["travel_request"]
        replan = state.get("replan_instruction")

        # Build the research prompt
        interests_str = ", ".join(request.interests) if request.interests else "general sightseeing"
        replan_note = ""
        if replan:
            replan_note = (
                f"\n\nNOTE: The user has requested a modification to the plan: "
                f'"{replan}". Adjust your research accordingly.'
            )

        prompt = f"""You are a travel research expert. Research the destination and provide detailed, 
accurate information.

DESTINATION: {request.destination}
NUMBER OF DAYS: {request.days}
TRAVELERS: {request.travelers}
TRAVEL STYLE: {request.travel_style}
INTERESTS: {interests_str}
FOOD PREFERENCE: {request.food_preference}
{replan_note}

Provide comprehensive destination information including:
1. A detailed overview of the destination (2-3 paragraphs)
2. Best time to visit
3. Local language and currency
4. At least 8-10 attractions that match the traveler's interests
   - For each attraction: name, category, description, estimated entry cost in INR, recommended duration
5. Cultural notes and etiquette tips (at least 3)
6. Safety tips specific to this destination (at least 3)
7. Local transport options available

Make sure attractions are REAL places. Do not fabricate locations.
Estimated costs should be realistic for {request.travel_style} travel style.
"""

        # Generate destination info via LLM
        destination_info = generate_structured(prompt, DestinationInfo)

        # Fetch real weather data
        weather_info = asyncio.run(get_weather(request.destination))

        logger.info(
            f"[{agent_name}] Researched {destination_info.destination_name}: "
            f"{len(destination_info.attractions)} attractions found. "
            f"Weather fallback: {weather_info.is_fallback}"
        )

        return {
            "destination_info": destination_info,
            "weather_info": weather_info,
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
