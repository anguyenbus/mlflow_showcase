"""Multi-turn conversation tracing with LangChain and MLflow.

Demonstrates how to trace conversation history, context management,
and multi-turn interactions with MLflow observability.

Expected Output:
--------------
Multi-Turn Conversation Tracing Demo
==================================================

Turn 1: Hello! What's your name?
AI: [Response from model]

Messages in history: 2

Turn 2: What did I just ask you?
AI: [Response referencing the greeting]

Messages in history: 4

Turn 3: Can you help me calculate 15 * 23?
AI: [Response with calculation]

Messages in history: 6

Turn 4: What was the result of that calculation?
AI: [Response referencing the calculation result]

Conversation complete!
Total exchanges: 4
Total messages: 8

View traces in MLflow UI to see conversation flow!

Run ID: [run_id]
"""

import os
import mlflow

from dotenv import load_dotenv
load_dotenv()

from beartype import beartype
from rich.console import Console
from rich.panel import Panel

from config import get_config
from basics.langchain_integration import create_zhipu_langchain_llm
from advanced.conversation.conversation_memory import ConversationManager
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

console = Console()


@beartype
def create_conversation_chain(conv_manager: ConversationManager):
    """Create a conversation chain with memory.

    Args:
        conv_manager: ConversationManager instance for memory

    Returns:
        Runnable chain that incorporates conversation history
    """
    # Create LLM
    llm = create_zhipu_langchain_llm(model="glm-5", temperature=0.7)

    # Create prompt with chat history placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Consider the conversation history when responding."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    def prepare_inputs(inputs: dict) -> dict:
        """Prepare inputs with conversation history.

        Args:
            inputs: Dictionary with 'input' key containing user message

        Returns:
            Dictionary with 'input' and 'chat_history' keys
        """
        user_input = inputs["input"]
        history = conv_manager.get_conversation_history()

        return {
            "input": user_input,
            "chat_history": history
        }

    # Build chain: prepare inputs -> prompt -> LLM
    chain = (
        RunnableLambda(prepare_inputs)
        | prompt
        | llm
    )

    return chain


@mlflow.trace(span_type="conversation_turn")
def run_conversation_turn(chain, conv_manager: ConversationManager, user_input: str) -> str:
    """Run a single conversation turn with tracing.

    This function traces the entire conversation turn including:
    - User input
    - Conversation history context
    - LLM response generation
    - Memory updates

    Args:
        chain: The conversation chain
        conv_manager: Conversation manager instance
        user_input: User's message

    Returns:
        AI response as string
    """
    # Log user input with span
    with mlflow.start_span(name="user_input") as span:
        span.set_inputs({"user_input": user_input})
        span.set_outputs({"message_logged": True})
        conv_manager.add_user_message(user_input)

    # Generate response with conversation history
    with mlflow.start_span(name="generate_response") as span:
        # Get current history for logging
        history = conv_manager.get_conversation_history()
        history_summary = conv_manager.get_history_summary()

        # Format recent context for logging
        recent_context = []
        for msg in history[-4:]:  # Last 2 exchanges
            if isinstance(msg, HumanMessage):
                recent_context.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                recent_context.append(f"AI: {msg.content}")

        span.set_inputs({
            "user_input": user_input,
            "history_length": history_summary["total_messages"],
            "recent_context": "\n".join(recent_context)
        })

        # Invoke chain with history
        response = chain.invoke({"input": user_input})

        # Extract response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        span.set_outputs({
            "response": response_text[:500] if len(response_text) > 500 else response_text,
            "response_length": len(response_text)
        })

        # Add AI response to memory
        conv_manager.add_ai_message(response_text)

        return response_text


def main() -> None:
    """Run multi-turn conversation demonstration.

    Creates a conversation chain and runs through 4 conversation turns:
    1. Initial greeting
    2. Follow-up question testing memory
    3. New topic requiring calculation
    4. Reference back to previous calculation

    Each turn is traced with MLflow to show conversation history flow.
    """
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment("mlflow-multi-turn-conversations")

    console.print(Panel("[bold cyan]Multi-Turn Conversation Tracing Demo[/bold cyan]"))

    # Initialize conversation manager and chain
    conv_manager = ConversationManager(max_history=10)
    chain = create_conversation_chain(conv_manager)

    with mlflow.start_run():
        mlflow.log_params({
            "model": "glm-5",
            "temperature": 0.7,
            "max_history": 10
        })

        # Conversation 1: Simple greeting
        console.print("\n[bold yellow]Turn 1:[/bold yellow] Hello! What's your name?")
        response = run_conversation_turn(chain, conv_manager, "Hello! What's your name?")
        console.print(f"AI: {response}")

        # Show history stats
        stats = conv_manager.get_history_summary()
        console.print(f"[dim]Messages in history: {stats['total_messages']}[/dim]")

        # Conversation 2: Follow-up question
        console.print("\n[bold yellow]Turn 2:[/bold yellow] What did I just ask you?")
        response = run_conversation_turn(chain, conv_manager, "What did I just ask you?")
        console.print(f"AI: {response}")

        stats = conv_manager.get_history_summary()
        console.print(f"[dim]Messages in history: {stats['total_messages']}[/dim]")

        # Conversation 3: New topic
        console.print("\n[bold yellow]Turn 3:[/bold yellow] Can you help me calculate 15 * 23?")
        response = run_conversation_turn(chain, conv_manager, "Can you help me calculate 15 * 23?")
        console.print(f"AI: {response}")

        stats = conv_manager.get_history_summary()
        console.print(f"[dim]Messages in history: {stats['total_messages']}[/dim]")

        # Conversation 4: Reference back
        console.print("\n[bold yellow]Turn 4:[/bold yellow] What was the result of that calculation?")
        response = run_conversation_turn(chain, conv_manager, "What was the result of that calculation?")
        console.print(f"AI: {response}")

        stats = conv_manager.get_history_summary()
        console.print(f"[dim]Messages in history: {stats['total_messages']}[/dim]")

        # Log final conversation summary
        summary = conv_manager.get_history_summary()
        mlflow.log_metrics({
            "total_messages": summary["total_messages"],
            "user_messages": summary["user_messages"],
            "ai_messages": summary["ai_messages"]
        })

        console.print("\n[green]Conversation complete![/green]")
        console.print(f"[cyan]Total exchanges: {summary['user_messages']}[/cyan]")
        console.print(f"[cyan]Total messages: {summary['total_messages']}[/cyan]")
        console.print("\n[dim]View traces in MLflow UI to see conversation flow![/dim]")


if __name__ == "__main__":
    main()
