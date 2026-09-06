"""
Safar — Model Validation Tests

Tests for Pydantic models and input validation.
No API key required.
"""

import pytest
from pydantic import ValidationError
from app.models.travel import (
    TravelRequest,
    DestinationInfo,
    BudgetBreakdown,
    BudgetItem,
    Itinerary,
    DayPlan,
    Activity,
    ReviewResult,
    FinalPlan,
    WeatherInfo,
    WeatherDay,
    Attraction,
    FoodRecommendation,
)


class TestTravelRequest:
    """Tests for TravelRequest validation."""

    def test_valid_request(self):
        req = TravelRequest(
            destination="Goa",
            days=4,
            travelers=2,
            budget=25000,
            travel_style="balanced",
            interests=["beaches", "food"],
            food_preference="vegetarian",
        )
        assert req.destination == "Goa"
        assert req.days == 4
        assert req.travelers == 2
        assert req.budget == 25000.0

    def test_destination_trimmed(self):
        req = TravelRequest(destination="  Goa  ", days=3, travelers=1, budget=10000)
        assert req.destination == "Goa"

    def test_empty_destination_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="", days=3, travelers=1, budget=10000)

    def test_zero_days_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=0, travelers=1, budget=10000)

    def test_negative_days_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=-1, travelers=1, budget=10000)

    def test_max_days_exceeded(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=31, travelers=1, budget=10000)

    def test_zero_travelers_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=3, travelers=0, budget=10000)

    def test_zero_budget_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=3, travelers=1, budget=0)

    def test_negative_budget_rejected(self):
        with pytest.raises(ValidationError):
            TravelRequest(destination="Goa", days=3, travelers=1, budget=-5000)

    def test_invalid_travel_style(self):
        with pytest.raises(ValidationError):
            TravelRequest(
                destination="Goa", days=3, travelers=1,
                budget=10000, travel_style="ultra-premium"
            )

    def test_travel_style_normalized(self):
        req = TravelRequest(
            destination="Goa", days=3, travelers=1,
            budget=10000, travel_style="LUXURY"
        )
        assert req.travel_style == "luxury"

    def test_default_values(self):
        req = TravelRequest(destination="Goa", days=3, travelers=1, budget=10000)
        assert req.travel_style == "balanced"
        assert req.interests == []
        assert req.food_preference == "no preference"
        assert req.special_requirements == ""


class TestBudgetBreakdown:
    """Tests for BudgetBreakdown model."""

    def test_budget_within_range(self):
        budget = BudgetBreakdown(
            total_estimated=20000,
            per_person=10000,
            user_budget=25000,
            is_within_budget=True,
            items=[
                BudgetItem(category="Accommodation", estimated_cost=8000),
                BudgetItem(category="Food", estimated_cost=6000),
                BudgetItem(category="Transport", estimated_cost=3000),
                BudgetItem(category="Activities", estimated_cost=3000),
            ],
        )
        assert budget.is_within_budget is True
        assert budget.total_estimated == 20000

    def test_budget_over(self):
        budget = BudgetBreakdown(
            total_estimated=30000,
            per_person=15000,
            user_budget=25000,
            is_within_budget=False,
            budget_warning="Over budget by ₹5,000",
        )
        assert budget.is_within_budget is False
        assert budget.budget_warning != ""


class TestItinerary:
    """Tests for Itinerary model."""

    def test_itinerary_structure(self):
        itinerary = Itinerary(
            days=[
                DayPlan(
                    day_number=1,
                    title="Beach Day",
                    activities=[
                        Activity(
                            time="9:00 AM",
                            title="Visit Baga Beach",
                            location="Baga Beach",
                            duration="3 hours",
                            estimated_cost=0,
                        ),
                    ],
                ),
            ],
            general_tips=["Stay hydrated"],
        )
        assert len(itinerary.days) == 1
        assert itinerary.days[0].day_number == 1
        assert len(itinerary.days[0].activities) == 1


class TestWeatherInfo:
    """Tests for WeatherInfo model."""

    def test_weather_with_forecast(self):
        weather = WeatherInfo(
            destination="Goa",
            forecast=[
                WeatherDay(
                    date="2025-01-15",
                    temp_max_c=32.5,
                    temp_min_c=24.0,
                    condition="Clear sky",
                    precipitation_mm=0,
                ),
            ],
            summary="Sunny weather expected.",
            is_fallback=False,
        )
        assert weather.is_fallback is False
        assert len(weather.forecast) == 1

    def test_weather_fallback(self):
        weather = WeatherInfo(
            destination="Unknown Place",
            forecast=[],
            summary="Weather data unavailable.",
            is_fallback=True,
        )
        assert weather.is_fallback is True


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_approved_review(self):
        review = ReviewResult(overall_score=8, approved=True, checks=[], issues=[])
        assert review.approved is True
        assert review.overall_score == 8

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            ReviewResult(overall_score=11, approved=True)

        with pytest.raises(ValidationError):
            ReviewResult(overall_score=-1, approved=True)


class TestFinalPlan:
    """Tests for FinalPlan model."""

    def test_minimal_plan(self):
        plan = FinalPlan(
            destination="Goa",
            days=3,
            travelers=2,
            travel_style="balanced",
        )
        assert plan.destination == "Goa"
        assert plan.destination_info is None
        assert plan.itinerary is None

    def test_full_plan(self):
        plan = FinalPlan(
            destination="Goa",
            days=3,
            travelers=2,
            travel_style="balanced",
            overview="A 3-day trip to Goa",
            destination_info=DestinationInfo(
                destination_name="Goa",
                overview="Beautiful coastal state",
                attractions=[Attraction(name="Baga Beach", category="beach")],
            ),
            budget_breakdown=BudgetBreakdown(
                total_estimated=20000,
                per_person=10000,
                user_budget=25000,
            ),
            food_recommendations=[
                FoodRecommendation(name="Fish Thali", category="Local Specialty"),
            ],
        )
        assert plan.destination_info is not None
        assert len(plan.destination_info.attractions) == 1
        assert len(plan.food_recommendations) == 1
