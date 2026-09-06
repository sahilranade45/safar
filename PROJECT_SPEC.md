# Safar — Project Specification 📋

## 1. Executive Summary
**Safar** is an interactive multi-agent AI travel planning platform designed to transform raw user travel preferences into actionable, realistic, itemized itineraries with real-time weather integration and intelligent human-in-the-loop replanning.

## 2. Target Audience & Use Case
- Travelers who want structured, personalized travel plans without spending hours researching manually.
- Budget-conscious or style-specific travelers (luxury, backpacker, eco-friendly, family).
- AI Engineers & Recruiters evaluating agentic LLM system architecture.

## 3. Core Functional Requirements
1. **User Input Form**:
   - Destination, Travelers, Duration (1-14 days), Total Budget & Currency.
   - Travel Style (Luxury, Mid-range, Budget, Backpacker, Eco-friendly, Family).
   - Interests (Culture, Nature, Food, Nightlife, Shopping, Relaxation, Adventure).
   - Dietary preferences & optional special requests.

2. **Autonomous Multi-Agent Processing**:
   - Coordinator: Input verification & trace logging.
   - Destination Agent: Insights & Open-Meteo weather forecast.
   - Budget Agent: Category-based financial allocation & cost-saving tips.
   - Itinerary Agent: Morning/Afternoon/Evening micro-activities.
   - Review Agent: Audit & Quality Score (0-100).

3. **Replanning Feature**:
   - Allows users to request target adjustments to any section of the generated plan.

4. **UI Visualizations**:
   - Dynamic progress stepper showing active agent execution.
   - Interactive tabbed plan layout (Overview, Weather, Budget, Itinerary, Review).
   - Export functionality (Print/PDF and Clipboard copy).

## 4. Non-Functional Requirements
- **Response Time**: Full multi-agent execution completed within 8-15 seconds.
- **Reliability**: Graceful fallback structures if external APIs or LLMs encounter errors.
- **Maintainability**: Clear division of agent modules, Pydantic schemas, and React components.
