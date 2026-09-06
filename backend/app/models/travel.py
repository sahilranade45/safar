"""
Safar — Core Travel Data Models

Pydantic models for all structured data flowing through the agent pipeline.
These models ensure type safety and validation at every stage.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ==============================================================================
# User Input
# ==============================================================================

class TravelRequest(BaseModel):
    """Validated user input for a travel planning request."""

    destination: str = Field(..., min_length=1, description="Travel destination")
    days: int = Field(..., gt=0, le=30, description="Number of days")
    travelers: int = Field(..., gt=0, le=20, description="Number of travelers")
    budget: float = Field(..., gt=0, description="Approximate budget in INR")
    travel_style: str = Field(
        default="balanced",
        description="Travel style: budget, balanced, or luxury"
    )
    interests: list[str] = Field(
        default_factory=list,
        description="List of interests (beaches, culture, food, adventure, etc.)"
    )
    food_preference: str = Field(
        default="no preference",
        description="Food preference (vegetarian, vegan, non-vegetarian, etc.)"
    )
    special_requirements: str = Field(
        default="",
        description="Any special requirements or notes"
    )

    @field_validator("travel_style")
    @classmethod
    def validate_travel_style(cls, v: str) -> str:
        allowed = {"budget", "balanced", "luxury"}
        v_lower = v.strip().lower()
        if v_lower not in allowed:
            raise ValueError(f"travel_style must be one of {allowed}")
        return v_lower

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v: str) -> str:
        return v.strip()


# ==============================================================================
# Destination Research
# ==============================================================================

class Attraction(BaseModel):
    """A single attraction or point of interest."""
    name: str
    category: str = ""  # e.g. "beach", "temple", "market"
    description: str = ""
    estimated_cost: float = 0.0
    recommended_duration: str = ""  # e.g. "2-3 hours"


class DestinationInfo(BaseModel):
    """Structured destination research output."""
    destination_name: str
    overview: str = ""
    best_time_to_visit: str = ""
    language: str = ""
    currency: str = "INR"
    attractions: list[Attraction] = Field(default_factory=list)
    cultural_notes: list[str] = Field(default_factory=list)
    safety_tips: list[str] = Field(default_factory=list)
    local_transport_options: list[str] = Field(default_factory=list)


# ==============================================================================
# Weather
# ==============================================================================

class WeatherDay(BaseModel):
    """Weather for a single day."""
    date: str = ""
    temp_max_c: float = 0.0
    temp_min_c: float = 0.0
    condition: str = ""  # e.g. "Sunny", "Rainy", "Cloudy"
    precipitation_mm: float = 0.0


class WeatherInfo(BaseModel):
    """Weather information for the destination."""
    destination: str
    forecast: list[WeatherDay] = Field(default_factory=list)
    summary: str = ""
    packing_suggestions: list[str] = Field(default_factory=list)
    is_fallback: bool = False  # True if real API was unavailable


# ==============================================================================
# Budget
# ==============================================================================

class BudgetItem(BaseModel):
    """A single line item in the budget breakdown."""
    category: str  # e.g. "Accommodation", "Food", "Transport"
    estimated_cost: float
    notes: str = ""


class BudgetBreakdown(BaseModel):
    """Complete budget analysis."""
    total_estimated: float = 0.0
    per_person: float = 0.0
    user_budget: float = 0.0
    is_within_budget: bool = True
    items: list[BudgetItem] = Field(default_factory=list)
    savings_tips: list[str] = Field(default_factory=list)
    budget_warning: str = ""


# ==============================================================================
# Itinerary
# ==============================================================================

class Activity(BaseModel):
    """A single activity within a day."""
    time: str = ""  # e.g. "9:00 AM"
    title: str
    description: str = ""
    location: str = ""
    duration: str = ""  # e.g. "2 hours"
    estimated_cost: float = 0.0
    category: str = ""  # e.g. "sightseeing", "food", "adventure"


class DayPlan(BaseModel):
    """Plan for a single day."""
    day_number: int
    title: str = ""  # e.g. "Beach Day & Local Cuisine"
    activities: list[Activity] = Field(default_factory=list)


class Itinerary(BaseModel):
    """Complete day-by-day itinerary."""
    days: list[DayPlan] = Field(default_factory=list)
    general_tips: list[str] = Field(default_factory=list)


# ==============================================================================
# Food Recommendations
# ==============================================================================

class FoodRecommendation(BaseModel):
    """Food and dining recommendation."""
    name: str  # dish or restaurant name
    category: str = ""  # e.g. "Street Food", "Fine Dining", "Cafe"
    cuisine: str = ""
    description: str = ""
    price_range: str = ""  # e.g. "₹100-300"
    is_vegetarian: bool = False
    location_hint: str = ""


# ==============================================================================
# Review
# ==============================================================================

class ReviewCheck(BaseModel):
    """A single validation check performed by the review agent."""
    check_name: str
    passed: bool
    details: str = ""


class ReviewResult(BaseModel):
    """Output of the review agent."""
    overall_score: int = Field(default=0, ge=0, le=10)
    checks: list[ReviewCheck] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    approved: bool = True


# ==============================================================================
# Final Plan
# ==============================================================================

class FinalPlan(BaseModel):
    """The complete, assembled travel plan."""
    destination: str
    days: int
    travelers: int
    travel_style: str
    overview: str = ""
    destination_info: Optional[DestinationInfo] = None
    weather_info: Optional[WeatherInfo] = None
    budget_breakdown: Optional[BudgetBreakdown] = None
    itinerary: Optional[Itinerary] = None
    food_recommendations: list[FoodRecommendation] = Field(default_factory=list)
    travel_tips: list[str] = Field(default_factory=list)
    review_result: Optional[ReviewResult] = None
