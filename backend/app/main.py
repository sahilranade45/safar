"""
Safar — FastAPI Backend

Main application entry point.
Provides REST API endpoints for travel planning.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.travel import TravelRequest
from app.models.responses import (
    TravelPlanResponse,
    HealthResponse,
    ErrorResponse,
    ReplanRequest,
    AgentExecution,
)
from app.graph.state import TravelPlanState
from app.graph.workflow import run_travel_plan

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup checks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks."""
    logger.info("=" * 60)
    logger.info("  SAFAR — Multi-Agent AI Travel Planner")
    logger.info("=" * 60)

    if settings.is_api_key_configured:
        logger.info(f"✓ Gemini API key configured (model: {settings.gemini_model})")
    else:
        logger.warning(
            "⚠ Gemini API key NOT configured! "
            "Set GEMINI_API_KEY in your .env file. "
            "The /api/plan endpoint will not work without it."
        )

    logger.info(f"✓ CORS allowed origin: {settings.frontend_url}")
    logger.info(f"✓ Server ready on port {settings.backend_port}")
    logger.info("=" * 60)
    yield


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Safar — Multi-Agent AI Travel Planner",
    description=(
        "An agentic AI application where multiple specialized agents "
        "collaborate to create personalized travel plans."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        api_key_configured=settings.is_api_key_configured,
        model=settings.gemini_model,
    )


@app.post("/api/plan", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelRequest):
    """
    Create a personalized travel plan using the multi-agent workflow.

    The request flows through:
    Coordinator → Destination Research → Budget → Itinerary → Review → Finalize
    """
    if not settings.is_api_key_configured:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini API key is not configured. "
                "Please set GEMINI_API_KEY in your .env file."
            ),
        )

    start_time = time.time()

    try:
        # Build initial state
        initial_state: TravelPlanState = {
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

        # Run the LangGraph workflow
        final_state = run_travel_plan(initial_state)

        total_duration = time.time() - start_time

        # Check for critical errors
        errors = final_state.get("errors", [])
        final_plan = final_state.get("final_plan")
        agent_execs = final_state.get("agent_executions", [])

        if not final_plan and errors:
            return TravelPlanResponse(
                success=False,
                plan=None,
                agent_executions=agent_execs,
                total_duration_seconds=total_duration,
                error="; ".join(errors),
            )

        return TravelPlanResponse(
            success=True,
            plan=final_plan,
            agent_executions=agent_execs,
            total_duration_seconds=total_duration,
        )

    except Exception as e:
        logger.error(f"Travel plan creation failed: {e}")
        total_duration = time.time() - start_time
        return TravelPlanResponse(
            success=False,
            plan=None,
            agent_executions=[],
            total_duration_seconds=total_duration,
            error=f"An error occurred: {str(e)}",
        )


@app.post("/api/replan", response_model=TravelPlanResponse)
async def replan_travel(replan_request: ReplanRequest):
    """
    Modify an existing travel plan based on user feedback.

    Re-runs the agent workflow with the modification instruction,
    allowing agents to adjust their outputs accordingly.
    """
    if not settings.is_api_key_configured:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured.",
        )

    start_time = time.time()

    try:
        # Build state with replan instruction
        initial_state: TravelPlanState = {
            "travel_request": replan_request.original_request,
            "destination_info": None,
            "weather_info": None,
            "budget_breakdown": None,
            "itinerary": None,
            "food_recommendations": None,
            "review_result": None,
            "final_plan": None,
            "agent_executions": [],
            "errors": [],
            "replan_instruction": replan_request.modification,
        }

        # Run the workflow with replan context
        final_state = run_travel_plan(initial_state)

        total_duration = time.time() - start_time
        errors = final_state.get("errors", [])
        final_plan = final_state.get("final_plan")
        agent_execs = final_state.get("agent_executions", [])

        if not final_plan and errors:
            return TravelPlanResponse(
                success=False,
                plan=None,
                agent_executions=agent_execs,
                total_duration_seconds=total_duration,
                error="; ".join(errors),
            )

        return TravelPlanResponse(
            success=True,
            plan=final_plan,
            agent_executions=agent_execs,
            total_duration_seconds=total_duration,
        )

    except Exception as e:
        logger.error(f"Replan failed: {e}")
        total_duration = time.time() - start_time
        return TravelPlanResponse(
            success=False,
            plan=None,
            agent_executions=[],
            total_duration_seconds=total_duration,
            error=f"Replanning failed: {str(e)}",
        )


from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Return structured error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )

