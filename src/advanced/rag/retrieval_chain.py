"""Retrieval-augmented generation chain implementation.

Combines document retrieval with LLM generation using LangChain LCEL syntax.
"""

from typing import Final
from beartype import beartype
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


@beartype
class RetrievalChain:
    """RAG chain combining document retrieval with LLM generation.

    Uses LangChain LCEL syntax to create a composable retrieval chain.

    Attributes:
        retriever: Document retriever (typically from VectorStore).
        llm: Language model for response generation.
        chain: Compiled LangChain for end-to-end RAG.

    Example:
        >>> chain = RetrievalChain(retriever, llm)
        >>> result = chain.invoke("What are tax implications?")
        >>> print(result)
    """

    __slots__ = ("retriever", "llm", "chain", "_prompt")

    DEFAULT_TEMPLATE: Final[str] = """Answer the question based only on the following context:

Context:
{context}

Question: {question}

Answer:"""

    def __init__(self, retriever, llm, prompt_template: str | None = None) -> None:
        """Initialize the RAG chain.

        Args:
            retriever: LangChain retriever for document retrieval.
            llm: LangChain language model for generation.
            prompt_template: Optional custom prompt template.
        """
        self.retriever = retriever
        self.llm = llm

        # Create prompt template
        template = prompt_template or self.DEFAULT_TEMPLATE
        self._prompt = ChatPromptTemplate.from_template(template)

        # NOTE: Using LCEL syntax for composable chain
        # The format_docs function formats retrieved documents
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Build the RAG chain using LCEL
        self.chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | self._prompt
            | self.llm
            | StrOutputParser()
        )

    def invoke(self, query: str, **kwargs) -> str:
        """Invoke the RAG chain with a query.

        Args:
            query: User question or query text.
            **kwargs: Additional arguments for chain invocation.

        Returns:
            Generated answer based on retrieved context.
        """
        result = self.chain.invoke(query, **kwargs)
        return result

    def invoke_with_tracing(self, query: str, **kwargs) -> tuple[str, list]:
        """Invoke the RAG chain with explicit chunk tracing.

        This method retrieves documents explicitly and logs them as span outputs,
        making retrieved chunks visible in MLflow UI.

        Args:
            query: User question or query text.
            **kwargs: Additional arguments for chain invocation.

        Returns:
            Tuple of (generated_answer, retrieved_documents).
        """
        import mlflow

        # Retrieve documents explicitly with tracing
        with mlflow.start_span(name="retrieve_documents") as retrieve_span:
            retrieve_span.set_inputs({"query": query, "top_k": 3})

            # Retrieve documents from vector store
            docs = self.retriever.invoke(query)

            # Format retrieved chunks for display
            chunk_info = [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]

            retrieve_span.set_outputs({
                "num_chunks": len(docs),
                "chunks": chunk_info
            })

        # Generate answer using the chain (without explicit retracing)
        with mlflow.start_span(name="generate_answer") as generate_span:
            generate_span.set_inputs({"query": query})

            result = self.chain.invoke(query, **kwargs)

            generate_span.set_outputs({"answer": result})

        return result, docs

    def stream(self, query: str, **kwargs):
        """Stream the RAG chain response.

        Args:
            query: User question or query text.
            **kwargs: Additional arguments for chain invocation.

        Yields:
            Streaming tokens from the LLM response.
        """
        for token in self.chain.stream(query, **kwargs):
            yield token

    def batch(self, queries: list[str], **kwargs) -> list[str]:
        """Invoke the RAG chain on multiple queries.

        Args:
            queries: List of query texts.
            **kwargs: Additional arguments for batch processing.

        Returns:
            List of generated answers.
        """
        results = self.chain.batch(queries, **kwargs)
        return results

    def get_retriever(self):
        """Access the underlying retriever.

        Returns:
            The retriever object for direct use.
        """
        return self.retriever

    def get_prompt(self):
        """Access the prompt template.

        Returns:
            The ChatPromptTemplate used by the chain.
        """
        return self._prompt
