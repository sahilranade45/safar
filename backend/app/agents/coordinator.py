"""
Safar — Coordinator Agent

Responsibilities:
- Validate the user's travel request
- Assemble the final travel plan from all agent outputs
- Handle replanning coordination
"""

from __future__ import annotations

import logging
import time

from app.graph.state import TravelPlanState
from app.models.travel import FinalPlan
from app.models.responses import AgentExecution

logger = logging.getLogger(__name__)


def coordinator_start(state: TravelPlanState) -> dict:
    """
    First node in the workflow.
    Validates the travel request and prepares the pipeline.
    """
    start = time.time()
    agent_name = "Coordinator"

    try:
        request = state.get("travel_request")
        if not request:
            return {
                "errors": [f"[{agent_name}] No travel request provided."],
                "agent_executions": [
                    AgentExecution(
                        agent_name=agent_name,
                        status="failed",
                        duration_seconds=time.time() - start,
                        error="No travel request provided",
                    )
                ],
            }

        logger.info(
            f"[{agent_name}] Starting pipeline for: "
            f"{request.destination}, {request.days} days, "
            f"{request.travelers} travelers, ₹{request.budget}"
        )

        return {
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


def coordinator_finalize(state: TravelPlanState) -> dict:
    """
    Last node in the workflow.
    Assembles the FinalPlan from all agent outputs.
    """
    start = time.time()
    agent_name = "Coordinator (Finalize)"

    try:
        request = state["travel_request"]
        destination_info = state.get("destination_info")
        weather_info = state.get("weather_info")
        budget_breakdown = state.get("budget_breakdown")
        itinerary = state.get("itinerary")
        food_recs = state.get("food_recommendations", [])
        review_result = state.get("review_result")

        # Build the overview
        overview_parts = [
            f"Your {request.days}-day {request.travel_style} trip to "
            f"{request.destination} for {request.travelers} traveler(s)."
        ]
        if budget_breakdown:
            overview_parts.append(
                f"Estimated total cost: ₹{budget_breakdown.total_estimated:,.0f} "
                f"(₹{budget_breakdown.per_person:,.0f} per person)."
            )
        if review_result and review_result.approved:
            overview_parts.append("✓ Plan reviewed and approved by AI Review Agent.")
        elif review_result:
            overview_parts.append(
                "⚠ Review agent found some issues — see review details."
            )

        # Collect travel tips from multiple sources
        travel_tips = []
        if destination_info and destination_info.safety_tips:
            travel_tips.extend(destination_info.safety_tips)
        if weather_info and weather_info.packing_suggestions:
            travel_tips.extend(weather_info.packing_suggestions)
        if budget_breakdown and budget_breakdown.savings_tips:
            travel_tips.extend(budget_breakdown.savings_tips)

        final_plan = FinalPlan(
            destination=request.destination,
            days=request.days,
            travelers=request.travelers,
            travel_style=request.travel_style,
            overview=" ".join(overview_parts),
            destination_info=destination_info,
            weather_info=weather_info,
            budget_breakdown=budget_breakdown,
            itinerary=itinerary,
            food_recommendations=food_recs or [],
            travel_tips=travel_tips,
            review_result=review_result,
        )

        logger.info(f"[{agent_name}] Final plan assembled successfully.")

        return {
            "final_plan": final_plan,
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
