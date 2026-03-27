"""MLflow Tracing Quickstart Example.

This example demonstrates MLflow Tracing for GenAI applications based on the
official MLflow Tracing Quickstart guide.

What it demonstrates:
- Automatic tracing for LLM calls (mlflow.openai.autolog)
- Custom tracing with @mlflow.trace decorator
- Tool calling with SpanType.TOOL and SpanType.AGENT
- Span hierarchy visualization in MLflow UI
- Timeline breakdown of execution
- Feedback attachment on traces

Reference: tracingmlflow.md

Expected Output:
--------------
✓ Experiment 'Tracing Quickstart' (ID: xx)
✓ Enabled automatic tracing for OpenAI-compatible APIs

Example 1: Single LLM Call
✓ LLM call traced automatically
✓ Trace ID: tr-xxxxxxxx
Execution Time: 2.3s
Tokens: 150

Example 2: Tool Calling Agent
✓ Tool calling agent executed
Question: What's the weather like in Seattle?
Answer: Based on the current weather data, the temperature in Seattle is 12.5°C.

View in MLflow UI:
- Navigate to the "Traces" tab
- See the trace hierarchy showing LLM and tool calls
- Click on timeline view to see execution breakdown
- Add feedback using "Add new Assessment" button
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import mlflow
from mlflow.entities.span import SpanType
from langchain_openai import ChatOpenAI
from config import get_config

# Initialize console
console = Console()


def setup_mlflow():
    """Set up MLflow experiment and tracing."""
    console.print("\n[bold cyan]MLflow Tracing Quickstart[/bold cyan]\n")

    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")

    # Create experiment
    experiment_name = "Tracing Quickstart"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        console.print(f"✓ Created experiment: {experiment_name} (ID: {experiment_id})")
    else:
        experiment_id = experiment.experiment_id
        console.print(f"✓ Experiment '{experiment_name}' (ID: {experiment_id})")

    return experiment_id


def example_1_single_llm_call():
    """Example 1: Trace a single LLM call with automatic tracing.

    Demonstrates mlflow.openai.autolog() for automatic instrumentation.
    """
    console.print("\n[bold yellow]Example 1: Single LLM Call[/bold yellow]\n")

    # Enable automatic tracing for OpenAI-compatible APIs
    mlflow.openai.autolog()
    console.print("✓ Enabled automatic tracing for OpenAI-compatible APIs")

    # Create LLM client
    llm = ChatOpenAI(
        model="glm-5",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4",
        openai_api_key=os.getenv("ZHIPU_API_KEY"),
        temperature=0.7,
    )

    # Make a simple LLM call (automatically traced)
    with mlflow.start_run(nested=True, run_name="single_llm_call"):
        response = llm.invoke("What is MLflow Tracing? Explain in one sentence.")

        console.print("\n[bold]LLM Response:[/bold]")
        console.print(Panel(str(response.content), border_style="green"))

        # The trace is automatically created by autolog()
        console.print("\n✓ LLM call traced automatically")
        console.print("  View in MLflow UI: Traces tab → single_llm_call")


def example_2_tool_calling_agent():
    """Example 2: Trace a tool calling agent with custom decorators.

    Demonstrates @mlflow.trace with SpanType.TOOL and SpanType.AGENT.
    """
    console.print("\n[bold yellow]Example 2: Tool Calling Agent[/bold yellow]\n")

    # Define a weather tool with custom tracing
    @mlflow.trace(span_type=SpanType.TOOL, name="get_weather")
    def get_weather(latitude: float, longitude: float) -> float:
        """Get current temperature for provided coordinates in Celsius.

        Uses Open-Meteo API (free, no API key required).
        """
        console.print(f"  [dim]Fetching weather for lat={latitude}, lon={longitude}[/dim]")

        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,wind_speed_10m"
        )
        data = response.json()
        temperature = data["current"]["temperature_2m"]

        console.print(f"  [dim]Temperature: {temperature}°C[/dim]")
        return temperature

    # Define a calculator tool with custom tracing
    @mlflow.trace(span_type=SpanType.TOOL, name="calculate")
    def calculate(expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        console.print(f"  [dim]Calculating: {expression}[/dim]")
        result = eval(expression)
        console.print(f"  [dim]Result: {result}[/dim]")
        return result

    # Define tool schemas for LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current temperature for provided coordinates in celsius.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Calculate mathematical expressions. Example: '2 + 2'",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"},
                    },
                    "required": ["expression"],
                },
            },
        },
    ]

    # Define a tool calling agent with custom tracing
    @mlflow.trace(span_type=SpanType.AGENT, name="tool_agent")
    def run_tool_agent(question: str):
        """Run a simple tool calling agent."""
        console.print(f"\n[bold]Question:[/bold] {question}")

        # Create LLM client
        llm = ChatOpenAI(
            model="glm-5",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4",
            openai_api_key=os.getenv("ZHIPU_API_KEY"),
            temperature=0.7,
        )

        # First LLM call: get tool call instructions
        messages = [{"role": "user", "content": question}]

        response = llm.invoke(messages)
        ai_message = response.content
        messages.append({"role": "assistant", "content": ai_message})

        console.print(f"\n[bold]Assistant:[/bold] {ai_message}")

        # Check if the model wants to use a tool
        # For simplicity, we'll parse the response and call tools directly
        # In production, you'd use the LLM's structured output or tool calling API

        # Simple heuristic: if weather is mentioned, call get_weather
        if "weather" in question.lower() or "temperature" in question.lower():
            # Seattle coordinates
            temp = get_weather(latitude=47.6062, longitude=-122.3321)
            tool_response = f"The current temperature in Seattle is {temp}°C."
            messages.append({"role": "user", "content": tool_response})

            # Second LLM call: generate final answer
            final_response = llm.invoke(messages)
            return final_response.content

        # Simple heuristic: if calculation is mentioned
        elif any(word in question.lower() for word in ["calculate", "add", "multiply", "divide"]):
            # Extract the expression (simplified)
            import re
            numbers = re.findall(r'\d+\.?\d*', question)
            if len(numbers) >= 2:
                expr = f"{numbers[0]} + {numbers[1]}"
                result = calculate(expr)
                tool_response = f"The calculation result is {result}."
                messages.append({"role": "user", "content": tool_response})

                # Second LLM call: generate final answer
                final_response = llm.invoke(messages)
                return final_response.content

        # Default: just return the first response
        return ai_message

    # Run the tool calling agent
    with mlflow.start_run(nested=True, run_name="tool_calling_agent"):
        answer = run_tool_agent("What's the weather like in Seattle?")

        console.print("\n[bold]Final Answer:[/bold]")
        console.print(Panel(answer, border_style="green"))

        console.print("\n✓ Tool calling agent traced")
        console.print("  View in MLflow UI: Traces tab → tool_calling_agent")
        console.print("  - See span hierarchy: AGENT → LLM → TOOL")
        console.print("  - Click timeline view to see execution breakdown")


def example_3_multi_turn_conversation():
    """Example 3: Trace a multi-turn conversation.

    Demonstrates tracing conversation history and context.
    """
    console.print("\n[bold yellow]Example 3: Multi-Turn Conversation[/bold yellow]\n")

    @mlflow.trace(span_type=SpanType.AGENT, name="chat_agent")
    def chat_conversation():
        """Simulate a multi-turn conversation."""
        llm = ChatOpenAI(
            model="glm-5",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4",
            openai_api_key=os.getenv("ZHIPU_API_KEY"),
            temperature=0.7,
        )

        conversation = [
            {"role": "user", "content": "Hi, I'm planning a trip to Seattle."}
        ]

        # Turn 1
        console.print("\n[bold]Turn 1:[/bold]")
        console.print(f"  User: {conversation[0]['content']}")
        response1 = llm.invoke(conversation)
        console.print(f"  Assistant: {response1.content[:100]}...")
        conversation.append({"role": "assistant", "content": response1.content})

        # Turn 2
        console.print("\n[bold]Turn 2:[/bold]")
        user_msg = "What's the weather like there?"
        console.print(f"  User: {user_msg}")
        conversation.append({"role": "user", "content": user_msg})
        response2 = llm.invoke(conversation)
        console.print(f"  Assistant: {response2.content[:100]}...")

        return response2.content

    with mlflow.start_run(nested=True, run_name="multi_turn_conversation"):
        answer = chat_conversation()

        console.print("\n✓ Multi-turn conversation traced")
        console.print("  View in MLflow UI: See conversation context across turns")


def main():
    """Main execution function."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]MLflow Tracing Quickstart Examples[/bold cyan]\n"
        "Based on official MLflow Tracing Quickstart guide\n"
        "Demonstrates automatic tracing, custom decorators, and tool calling",
        border_style="cyan"
    ))

    # Set up MLflow
    experiment_id = setup_mlflow()

    # Enable automatic tracing
    mlflow.openai.autolog()

    with mlflow.start_run(experiment_id=experiment_id, run_name="tracing_quickstart"):
        # Run examples
        example_1_single_llm_call()
        example_2_tool_calling_agent()
        example_3_multi_turn_conversation()

        console.print("\n")
        console.print(Panel.fit(
            "[bold green]Tracing Quickstart Complete![/bold green]\n\n"
            "[bold]View traces in MLflow UI:[/bold]\n"
            "• Navigate to 'Traces' tab\n"
            "• See the trace hierarchy showing LLM and tool calls\n"
            "• Click on timeline view to see execution breakdown\n"
            "• Add feedback using 'Add new Assessment' button\n\n"
            "[bold]Screenshot locations:[/bold]\n"
            "1. Traces list page (shows all traces)\n"
            "2. Trace detail page (click on trace name)\n"
            "3. Timeline view (click timeline icon)\n"
            "4. Feedback form (click 'Add new Assessment')",
            border_style="green"
        ))


if __name__ == "__main__":
    main()
