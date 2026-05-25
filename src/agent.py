"""LangGraph agent definition for Vertex AI Agent Engine."""

from vertexai import agent_engines

from src.tools import get_product_details

DEFAULT_MODEL = "gemini-2.5-flash"


def create_agent(model: str = DEFAULT_MODEL):
    """Build a LanggraphAgent with the product catalog tool."""
    return agent_engines.LanggraphAgent(
        model=model,
        tools=[get_product_details],
    )
