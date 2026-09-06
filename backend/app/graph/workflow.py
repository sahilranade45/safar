"""
Safar — LangGraph Workflow

Defines the agent pipeline as a LangGraph StateGraph:

    coordinator_start → destination_research → budget_analysis
    → itinerary_planning → review_plan → coordinator_finalize

Each node is an agent function that reads/writes the shared state.
"""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph, END

from app.graph.state import TravelPlanState
from app.agents.coordinator import coordinator_start, coordinator_finalize
from app.agents.destination_agent import destination_research
from app.agents.budget_agent import budget_analysis
from app.agents.itinerary_agent import itinerary_planning
from app.agents.review_agent import review_plan

logger = logging.getLogger(__name__)


def build_workflow() -> StateGraph:
    """
    Build and compile the LangGraph travel planning workflow.

    Returns a compiled graph that can be invoked with an initial state.
    """
    graph = StateGraph(TravelPlanState)

    # Add nodes (each node is an agent)
    graph.add_node("coordinator_start", coordinator_start)
    graph.add_node("destination_research", destination_research)
    graph.add_node("budget_analysis", budget_analysis)
    graph.add_node("itinerary_planning", itinerary_planning)
    graph.add_node("review_plan", review_plan)
    graph.add_node("coordinator_finalize", coordinator_finalize)

    # Define the sequential flow
    graph.set_entry_point("coordinator_start")
    graph.add_edge("coordinator_start", "destination_research")
    graph.add_edge("destination_research", "budget_analysis")
    graph.add_edge("budget_analysis", "itinerary_planning")
    graph.add_edge("itinerary_planning", "review_plan")
    graph.add_edge("review_plan", "coordinator_finalize")
    graph.add_edge("coordinator_finalize", END)

    return graph.compile()


# Pre-compiled workflow instance
travel_workflow = build_workflow()


def run_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """
    Execute the complete travel planning workflow.

    Args:
        state: Initial state with at least travel_request populated.

    Returns:
        Final state with all agent outputs and the assembled plan.
    """
    logger.info("Starting travel planning workflow...")
    result = travel_workflow.invoke(state)
    logger.info("Travel planning workflow completed.")
    return result
