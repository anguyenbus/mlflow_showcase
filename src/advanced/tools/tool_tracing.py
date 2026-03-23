"""Tool calling tracing with LangChain and MLflow.

Demonstrates how to trace tool invocations, showing:
- Tool selection and execution
- Tool inputs and outputs
- Multi-tool workflows
- Error handling for tool failures

Expected Output:
--------------
Tool Calling Tracing Demo
╔════════════════════════════════════════════════════════╗
║       Tool Calling Tracing Demo                         ║
╚════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tool            ┃ Description                           ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ get_current_time│ Get current date/time with custom...  │
│ get_current_date│ Get current date in YYYY-MM-DD format  │
│ calculate       │ Evaluate mathematical expressions      │
│ add_numbers     │ Add two numbers together               │
│ multiply_numbers│ Multiply two numbers                   │
└────────────────┴────────────────────────────────────────┘

Query 1: What is 15 * 23?
Response: [Tool execution result]

Query 2: What time is it?
Response: [Current time]

Query 3: What's 10 * 5 plus the current date?
Response: [Multi-step tool result]

Tool calling demonstration complete!
View traces in MLflow UI to see:
  - Tool selection decisions
  - Tool inputs and outputs
  - Multi-step tool workflows

Run ID: [run_id]
"""

import mlflow

from dotenv import load_dotenv
load_dotenv()

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import get_config
from basics.langchain_integration import create_zhipu_langchain_llm
from advanced.tools.builtin_tools import AVAILABLE_TOOLS, TOOL_DESCRIPTIONS
from langchain_core.tools import render_text_description
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any, List

console = Console()


def create_tool_calling_chain():
    """Create a chain with tool calling capabilities.

    Returns:
        Tuple of (llm_with_tools, tools_list) where:
        - llm_with_tools: LLM with tools bound using bind_tools()
        - tools_list: List of tool objects for reference
    """
    # Create LLM with low temperature for deterministic tool selection
    llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.0)

    # Bind tools directly to LLM
    # NOTE: bind_tools() tells the LLM about available tools and their schemas
    llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)

    return llm_with_tools, AVAILABLE_TOOLS


def create_tool_prompt_template() -> ChatPromptTemplate:
    """Create prompt template for tool-augmented LLM.

    Returns:
        ChatPromptTemplate with system instructions for tool use
    """
    system_message = """You are a helpful AI assistant with access to the following tools:

{tools}

Tool Names: {tool_names}

When you need to use a tool, respond with a tool call in the appropriate format.
Think step by step about which tool(s) you need to answer the user's question.

Available tools:
- get_current_time: Get current date and time
- get_current_date: Get today's date
- calculate: Evaluate mathematical expressions like "15 * 23" or "2 ** 8"
- add_numbers: Add two numbers
- multiply_numbers: Multiply two numbers

Always explain your reasoning before calling tools. After getting tool results,
provide a clear answer to the user."""

    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}")
    ])


@mlflow.trace(span_type="tool_query")
def run_tool_query(llm_with_tools, tools: List, query: str, prompt_template: ChatPromptTemplate) -> Dict[str, Any]:
    """Execute a query with tool calling and comprehensive tracing.

    This function traces the entire tool calling workflow:
    1. Query analysis
    2. Tool selection (LLM decision)
    3. Tool execution
    4. Response generation

    Args:
        llm_with_tools: LLM with tools bound via bind_tools()
        tools: List of available tool objects
        query: User's natural language query
        prompt_template: Prompt template with tool descriptions

    Returns:
        Dictionary with:
        - response: Final LLM response
        - tool_calls: List of tool invocations (if any)
        - has_tools: Boolean indicating if tools were called
    """
    with mlflow.start_span(name="tool_query_processing") as span:
        span.set_inputs({
            "query": query,
            "available_tools": [t.name for t in tools],
            "num_tools": len(tools)
        })

        # Prepare prompt with tool descriptions
        tools_desc = render_text_description(tools)
        tool_names = ", ".join([t.name for t in tools])

        # Format prompt
        prompt_messages = prompt_template.format_messages(
            tools=tools_desc,
            tool_names=tool_names,
            input=query
        )

        # Execute LLM with tool binding
        with mlflow.start_span(name="llm_tool_execution") as llm_span:
            llm_span.set_inputs({
                "query": query,
                "tools_bound": len(tools)
            })

            response = llm_with_tools.invoke(prompt_messages)

            # Extract response content
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)

            llm_span.set_outputs({
                "response_preview": response_content[:200] if len(response_content) > 200 else response_content
            })

        # Check for tool calls
        tool_calls_info = []
        has_tools = False

        if hasattr(response, 'tool_calls') and response.tool_calls:
            has_tools = True
            with mlflow.start_span(name="tool_calls_analysis") as tools_span:
                tool_calls_list = []
                tool_names_called = []

                for tc in response.tool_calls:
                    # Handle both dict and object formats
                    if isinstance(tc, dict):
                        tool_name = tc.get('name', 'unknown')
                        tool_args = str(tc.get('args', {}))
                        tool_id = tc.get('id', 'unknown')
                    else:
                        tool_name = tc.name if hasattr(tc, 'name') else 'unknown'
                        tool_args = str(tc.args) if hasattr(tc, 'args') else '{}'
                        tool_id = tc.id if hasattr(tc, 'id') else 'unknown'

                    tool_calls_list.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "id": tool_id
                    })
                    tool_names_called.append(tool_name)

                    # Log individual tool call
                    with mlflow.start_span(name=f"tool_call_{tool_name}") as tool_span:
                        tool_span.set_inputs({
                            "tool_name": tool_name,
                            "tool_args": tool_args
                        })

                        # NOTE: In a full implementation, we would execute tools here
                        # For this demo, we log the tool call intent
                        tool_span.set_outputs({
                            "tool_executed": "logged"
                        })

                tools_span.set_outputs({
                    "tools_called": tool_names_called,
                    "num_tool_calls": len(tool_names_called)
                })

                tool_calls_info = tool_calls_list

        # Prepare final result
        result = {
            "response": response_content,
            "tool_calls": tool_calls_info,
            "has_tools": has_tools
        }

        span.set_outputs({
            "has_tool_calls": has_tools,
            "num_tools_called": len(tool_calls_info) if has_tools else 0,
            "response_length": len(response_content)
        })

        return result


def main() -> None:
    """Run tool calling demonstration.

    Demonstrates three types of queries:
    1. Calculation query - triggers calculate tool
    2. Time query - triggers get_current_time tool
    3. Multi-step query - may trigger multiple tools

    Each query is traced to show tool selection and execution flow.
    """
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment("mlflow-tool-calling")

    console.print(Panel("[bold cyan]Tool Calling Tracing Demo[/bold cyan]"))

    # Initialize
    llm_with_tools, tools = create_tool_calling_chain()
    prompt_template = create_tool_prompt_template()

    # Display available tools
    table = Table(title="Available Tools")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    for tool_name, description in TOOL_DESCRIPTIONS.items():
        table.add_row(tool_name, description)
    console.print(table)

    with mlflow.start_run():
        mlflow.log_params({
            "model": "glm-5",
            "temperature": 0,
            "num_tools": len(tools),
            "tool_names": ",".join([t.name for t in tools])
        })

        # Query 1: Simple calculation
        console.print("\n[bold yellow]Query 1:[/bold yellow] What is 15 * 23?")
        result = run_tool_query(llm_with_tools, tools, "What is 15 * 23?", prompt_template)
        console.print(f"[green]Response:[/green] {result['response']}")

        if result['has_tools']:
            tool_names = [tc['tool'] for tc in result['tool_calls']]
            console.print(f"[dim]Tools called: {', '.join(tool_names)}[/dim]")

        # Query 2: DateTime
        console.print("\n[bold yellow]Query 2:[/bold yellow] What time is it right now?")
        result = run_tool_query(llm_with_tools, tools, "What time is it right now?", prompt_template)
        console.print(f"[green]Response:[/green] {result['response']}")

        if result['has_tools']:
            tool_names = [tc['tool'] for tc in result['tool_calls']]
            console.print(f"[dim]Tools called: {', '.join(tool_names)}[/dim]")

        # Query 3: Multi-step
        console.print("\n[bold yellow]Query 3:[/bold yellow] What's 10 * 5 and what's today's date?")
        result = run_tool_query(llm_with_tools, tools, "What's 10 * 5 and what's today's date?", prompt_template)
        console.print(f"[green]Response:[/green] {result['response']}")

        if result['has_tools']:
            tool_names = [tc['tool'] for tc in result['tool_calls']]
            console.print(f"[dim]Tools called: {', '.join(tool_names)}[/dim]")

        # Log summary metrics
        mlflow.log_metrics({"total_queries": 3})

        console.print("\n[green]Tool calling demonstration complete![/green]")
        console.print("\n[dim]View traces in MLflow UI to see:[/dim]")
        console.print("  [dim]- Tool selection decisions[/dim]")
        console.print("  [dim]- Tool inputs and outputs[/dim]")
        console.print("  [dim]- Multi-step tool workflows[/dim]")


if __name__ == "__main__":
    main()
