"""Simple deterministic embeddings for Show Case RAG demonstrations.

This module provides a mock embeddings implementation that generates
deterministic vectors from text using hash functions. This is suitable
for Show Case purposes to demonstrate RAG concepts without requiring
external API calls or dependencies.

WARNING: Not suitable for production use. For real applications, use
sentence-transformers, OpenAI embeddings, or similar.
"""

import hashlib
from typing import List

from beartype import beartype
from langchain_core.embeddings import Embeddings


@beartype
class DeterministicEmbeddings(Embeddings):
    """Deterministic embeddings for Show Case RAG demonstrations.

    Generates consistent embeddings using SHA256 hash of input text.
    Same text always produces the same embedding vector.

    Attributes:
        embedding_dim: Dimension of the embedding vectors (default: 384).

    Example:
        >>> embeddings = DeterministicEmbeddings(embedding_dim=384)
        >>> vec = embeddings.embed_query("hello world")
        >>> len(vec)
        384
    """

    __slots__ = ("embedding_dim",)

    def __init__(self, embedding_dim: int = 384) -> None:
        """Initialize deterministic embeddings.

        Args:
            embedding_dim: Dimension of embedding vectors (default: 384
                to match common sentence transformer models).
        """
        self.embedding_dim = embedding_dim

    def _text_to_vector(self, text: str) -> List[float]:
        """Convert text to deterministic vector using hash.

        Args:
            text: Input text to convert to vector.

        Returns:
            List of floats representing the embedding vector.
        """
        # Create SHA256 hash of text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert bytes to normalized floats [0, 1]
        values = [float(b) / 255.0 for b in hash_bytes]

        # Pad or truncate to embedding_dim
        if len(values) < self.embedding_dim:
            values.extend([0.0] * (self.embedding_dim - len(values)))
        else:
            values = values[:self.embedding_dim]

        return values

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.
        """
        return [self._text_to_vector(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed a query string.

        Args:
            text: Query text to embed.

        Returns:
            Embedding vector for the query.
        """
        return self._text_to_vector(text)
