import json
import math
from typing import Dict, Any

def tool_calculator(expression: str) -> Dict[str, Any]:
    """Safe evaluation of basic mathematical expressions."""
    try:
        # Restricted safe eval for math
        allowed = {"__builtins__": None, "math": math}
        result = eval(expression, allowed, {})
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"Invalid math expression: {str(e)}"}

def tool_weather(city: str) -> Dict[str, Any]:
    """Mock real-time weather service."""
    city_lower = city.lower()
    if "london" in city_lower or "seattle" in city_lower:
        return {"city": city, "temperature_c": 13, "condition": "Heavy Rain", "precipitation_chance": 85, "recommendation": "Carry an umbrella"}
    elif "tokyo" in city_lower or "paris" in city_lower:
        return {"city": city, "temperature_c": 19, "condition": "Overcast", "precipitation_chance": 30, "recommendation": "Light jacket"}
    return {"city": city, "temperature_c": 26, "condition": "Sunny", "precipitation_chance": 5, "recommendation": "Sunscreen and sunglasses"}

def tool_currency_converter(amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
    """Mock currency exchange engine."""
    rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 152.0,
        "INR": 83.5
    }
    from_rate = rates.get(from_curr.upper(), 1.0)
    to_rate = rates.get(to_curr.upper(), 1.0)
    converted = round((amount / from_rate) * to_rate, 2)
    return {"amount": amount, "from": from_curr.upper(), "to": to_curr.upper(), "converted_amount": converted}

def tool_sql_database(query: str) -> Dict[str, Any]:
    """Mock SQL database engine populated with enterprise customer analytics."""
    records = [
        {"id": 1, "customer": "Acme Corp", "tier": "Enterprise", "arr_usd": 120000, "status": "Active", "churn_risk": "Low"},
        {"id": 2, "customer": "Globex Inc", "tier": "Pro", "arr_usd": 45000, "status": "Active", "churn_risk": "High"},
        {"id": 3, "customer": "Soylent Tech", "tier": "Enterprise", "arr_usd": 250000, "status": "Renewal Due", "churn_risk": "Medium"},
        {"id": 4, "customer": "Initech", "tier": "Starter", "arr_usd": 12000, "status": "Churned", "churn_risk": "High"}
    ]
    return {
        "query": query,
        "rows_count": len(records),
        "results": records,
        "summary": "Total ARR: $427,000 across 4 enterprise accounts."
    }

def tool_document_search(query: str) -> Dict[str, Any]:
    """Mock vector database / internal enterprise knowledge search."""
    return {
        "query": query,
        "matches": [
            {
                "doc_id": "DOC-902",
                "title": "Q3 Enterprise Strategy & OKRs",
                "snippet": "Our primary strategic focus is migrating gateway operations to Bifrost for 99.99% model failover SLA and sub-millisecond routing."
            },
            {
                "doc_id": "DOC-415",
                "title": "Customer Retention Protocol",
                "snippet": "High-risk accounts above $40k ARR must receive dedicated technical account manager review within 48 hours."
            }
        ]
    }

def tool_file_reader(filename: str) -> Dict[str, Any]:
    """Mock sandbox filesystem reader."""
    if "inventory" in filename.lower():
        return {
            "filename": filename,
            "content": "SKU-101: 450 units | SKU-102: 120 units | SKU-103: 85 units (Discrepancy: Physical warehouse count is 65 units)"
        }
    elif "meeting" in filename.lower() or "transcript" in filename.lower():
        return {
            "filename": filename,
            "content": "Transcript: Alice agreed to finalize Bifrost gateway deployment by Friday. Bob will configure Tavily search filters. Carol to benchmark prompt injection guardrails."
        }
    return {"filename": filename, "content": "File loaded successfully. Length: 1,420 bytes."}

def tool_calendar_lookup(date: str) -> Dict[str, Any]:
    """Mock calendar scheduling engine."""
    return {
        "date": date,
        "events": [
            {"time": "09:30 AM", "title": "Bifrost Gateway Architecture Review", "attendees": ["DevOps", "AI Team"]},
            {"time": "02:00 PM", "title": "Executive Briefing: Agent Reliability", "attendees": ["Leadership"]}
        ]
    }

def tool_flight_search(origin: str, destination: str, date: str) -> Dict[str, Any]:
    """Mock flight booking aggregator."""
    return {
        "flights": [
            {"flight_no": "AA-402", "airline": "American", "price_usd": 320, "departure": "08:15 AM", "non_stop": True},
            {"flight_no": "DL-118", "airline": "Delta", "price_usd": 290, "departure": "11:45 AM", "non_stop": False}
        ]
    }

def tool_hotel_search(city: str, nights: int) -> Dict[str, Any]:
    """Mock hotel search system."""
    return {
        "city": city,
        "nights": nights,
        "hotels": [
            {"name": "Grand Central Hotel", "rate_per_night": 180, "total_usd": 180 * nights, "rating": 4.6},
            {"name": "Urban Boutique Suites", "rate_per_night": 140, "total_usd": 140 * nights, "rating": 4.3}
        ]
    }

def tool_budget_calculator(flight_cost: float, hotel_cost: float, daily_food: float, days: int) -> Dict[str, Any]:
    """Calculates comprehensive trip expenditure."""
    food_total = daily_food * days
    total = flight_cost + hotel_cost + food_total
    return {
        "flight_cost": flight_cost,
        "hotel_cost": hotel_cost,
        "food_total": food_total,
        "grand_total_usd": total
    }
