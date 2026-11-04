import time
import asyncio
import random
from typing import Dict, Any, Callable
from tools.mock_tools import (
    tool_calculator, tool_weather, tool_currency_converter,
    tool_sql_database, tool_document_search, tool_file_reader,
    tool_calendar_lookup, tool_flight_search, tool_hotel_search,
    tool_budget_calculator
)
from tools.tavily_tools import TavilyTools

class ToolSandbox:
    """
    Secure sandboxed tool-execution layer.
    Executes mock & live tools, applies controlled failure injection,
    and logs detailed execution telemetry for every call.
    """
    def __init__(self, chaos_config: Dict[str, Any] = None):
        self.chaos = chaos_config or {}
        self.tavily = TavilyTools()
        self.tool_logs = []
        
        self.registry: Dict[str, Callable] = {
            "calculator": tool_calculator,
            "weather": tool_weather,
            "currency_converter": tool_currency_converter,
            "sql_database": tool_sql_database,
            "document_search": tool_document_search,
            "file_reader": tool_file_reader,
            "calendar_lookup": tool_calendar_lookup,
            "flight_search": tool_flight_search,
            "hotel_search": tool_hotel_search,
            "budget_calculator": tool_budget_calculator,
            "tavily_search": self.tavily.search,
            "tavily_extract": self.tavily.extract
        }

    def execute_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        status = "success"
        output = {}

        if self.chaos.get("tool_unavailable"):
            latency = round((time.time() - start_time) * 1000, 2)
            log_entry = {
                "tool_name": tool_name,
                "input_arguments": arguments,
                "raw_output": {"error": f"Tool '{tool_name}' is currently unavailable."},
                "status": "error",
                "latency_ms": latency,
                "retry_count": 0,
                "cost_usd": 0.0
            }
            self.tool_logs.append(log_entry)
            return {"status": "error", "error_code": 503, "data": log_entry["raw_output"]}

        if self.chaos.get("inject_500") and random.random() < self.chaos.get("error_rate", 0.8):
            latency = round((time.time() - start_time) * 1000, 2)
            log_entry = {
                "tool_name": tool_name,
                "input_arguments": arguments,
                "raw_output": {"error": f"HTTP 500 Internal Server Error in {tool_name}"},
                "status": "error",
                "latency_ms": latency,
                "retry_count": 0,
                "cost_usd": 0.0
            }
            self.tool_logs.append(log_entry)
            return {"status": "error", "error_code": 500, "data": log_entry["raw_output"]}

        if self.chaos.get("inject_malformed_json"):
            latency = round((time.time() - start_time) * 1000, 2)
            log_entry = {
                "tool_name": tool_name,
                "input_arguments": arguments,
                "raw_output": "{'error': 'Unterminated string at pos 14: {\"status\": ...",
                "status": "error",
                "latency_ms": latency,
                "retry_count": 0,
                "cost_usd": 0.0
            }
            self.tool_logs.append(log_entry)
            return {"status": "error", "error_code": 422, "data": "Malformed JSON payload from tool"}

        delay = self.chaos.get("latency_seconds", 0.0)
        if delay > 0:
            time.sleep(delay)

        handler = self.registry.get(tool_name)
        if not handler:
            status = "error"
            output = {"error": f"Tool '{tool_name}' not found in sandbox registry."}
        else:
            try:
                output = handler(**arguments)
            except Exception as e:
                status = "error"
                output = {"error": f"Execution error in {tool_name}: {str(e)}"}

        if self.chaos.get("inject_stale_data") and isinstance(output, dict):
            output["_stale_warning"] = "Data drift detected: outdated rate applied."

        latency = round((time.time() - start_time) * 1000, 2)
        log_entry = {
            "tool_name": tool_name,
            "input_arguments": arguments,
            "raw_output": output,
            "status": status,
            "latency_ms": latency,
            "retry_count": 0,
            "cost_usd": 0.0002
        }
        self.tool_logs.append(log_entry)
        return {"status": status, "data": output}

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute_tool_sync(tool_name, arguments)
