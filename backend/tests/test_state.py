"""
Safar — State Structure Tests

Tests for LangGraph state and agent execution tracking.
No API key required.
"""

import pytest
from app.graph.state import TravelPlanState
from app.models.travel import TravelRequest
from app.models.responses import AgentExecution


class TestTravelPlanState:
    """Tests for the LangGraph shared state structure."""

    def test_initial_state_creation(self):
        """Test creating an initial state with travel request."""
        request = TravelRequest(
            destination="Goa",
            days=4,
            travelers=2,
            budget=25000,
            travel_style="balanced",
            interests=["beaches", "food"],
        )

        state: TravelPlanState = {
            "travel_request": request,
            "destination_info": None,
            "weather_info": None,
            "budget_breakdown": None,
            "itinerary": None,
            "food_recommendations": None,
            "review_result": None,
            "final_plan": None,
            "agent_executions": [],
            "errors": [],
            "replan_instruction": None,
        }

        assert state["travel_request"].destination == "Goa"
        assert state["destination_info"] is None
        assert len(state["agent_executions"]) == 0
        assert len(state["errors"]) == 0

    def test_agent_execution_tracking(self):
        """Test that agent executions can be accumulated."""
        exec1 = AgentExecution(
            agent_name="Coordinator",
            status="completed",
            duration_seconds=0.5,
        )
        exec2 = AgentExecution(
            agent_name="Destination Research",
            status="completed",
            duration_seconds=3.2,
        )

        # Simulate LangGraph accumulation (operator.add)
        executions = [exec1] + [exec2]

        assert len(executions) == 2
        assert executions[0].agent_name == "Coordinator"
        assert executions[1].agent_name == "Destination Research"

    def test_agent_execution_failed_status(self):
        """Test failed agent execution metadata."""
        exec_failed = AgentExecution(
            agent_name="Budget Analyst",
            status="failed",
            duration_seconds=1.0,
            error="LLM call failed",
        )

        assert exec_failed.status == "failed"
        assert exec_failed.error == "LLM call failed"

    def test_error_accumulation(self):
        """Test that errors can be accumulated."""
        errors = ["Error 1"] + ["Error 2"]
        assert len(errors) == 2

    def test_replan_state(self):
        """Test state with replan instruction."""
        request = TravelRequest(
            destination="Goa",
            days=4,
            travelers=2,
            budget=25000,
        )

        state: TravelPlanState = {
            "travel_request": request,
            "destination_info": None,
            "weather_info": None,
            "budget_breakdown": None,
            "itinerary": None,
            "food_recommendations": None,
            "review_result": None,
            "final_plan": None,
            "agent_executions": [],
            "errors": [],
            "replan_instruction": "Reduce budget to ₹15,000",
        }

        assert state["replan_instruction"] == "Reduce budget to ₹15,000"
