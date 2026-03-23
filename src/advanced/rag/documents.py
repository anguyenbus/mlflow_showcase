"""Document loading and chunking for RAG systems.

Provides utilities for loading documents and splitting them into chunks
using different strategies for optimal retrieval.
"""

from pathlib import Path
from enum import Enum
from typing import Literal, Final
from beartype import beartype
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingStrategy(str, Enum):
    """Chunking strategies for document splitting."""

    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"


@beartype
class DocumentLoader:
    """Load and chunk documents for RAG systems.

    Attributes:
        file_path: Path to the document file.
        encoding: File encoding (default: utf-8).

    Example:
        >>> loader = DocumentLoader("data/tax_law.txt")
        >>> documents = loader.load()
        >>> chunks = loader.chunk_documents(documents, chunk_size=1000)
    """

    __slots__ = ("file_path", "encoding")

    DEFAULT_CHUNK_SIZE: Final[int] = 1000
    DEFAULT_CHUNK_OVERLAP: Final[int] = 200

    def __init__(self, file_path: str | Path, encoding: str = "utf-8") -> None:
        """Initialize the document loader.

        Args:
            file_path: Path to the document file.
            encoding: File encoding.
        """
        self.file_path = Path(file_path)
        self.encoding = encoding

    def load(self) -> list[Document]:
        """Load document from file.

        Returns:
            List of Document objects containing the loaded content.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            UnicodeDecodeError: If the file encoding is incorrect.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Document not found: {self.file_path}")

        # NOTE: Using Path.read_text() for cleaner file handling
        content = self.file_path.read_text(encoding=self.encoding)

        return [
            Document(
                page_content=content,
                metadata={"source": str(self.file_path)}
            )
        ]

    def chunk_text(
        self,
        text: str,
        strategy: Literal["fixed_size", "recursive"] = ChunkingStrategy.RECURSIVE,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        """Split text into chunks using the specified strategy.

        Args:
            text: Text to split into chunks.
            strategy: Chunking strategy to use.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between consecutive chunks.

        Returns:
            List of text chunks.
        """
        if strategy == ChunkingStrategy.FIXED_SIZE:
            return self._fixed_size_chunk(text, chunk_size, chunk_overlap)
        else:
            return self._recursive_chunk(text, chunk_size, chunk_overlap)

    def _fixed_size_chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[str]:
        """Split text into fixed-size chunks with overlap.

        Args:
            text: Text to split.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between chunks.

        Returns:
            List of fixed-size chunks.
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position with overlap
            start = end - chunk_overlap if end < text_length else text_length

        return chunks

    def _recursive_chunk(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[str]:
        """Split text using recursive character splitting.

        This method tries to split on paragraph breaks, then sentences,
        then words, maintaining context better than fixed-size splitting.

        Args:
            text: Text to split.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between chunks.

        Returns:
            List of recursively-split chunks.
        """
        # NOTE: Using LangChain's RecursiveCharacterTextSplitter for intelligent splitting
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        return splitter.split_text(text)

    def chunk_documents(
        self,
        documents: list[Document],
        strategy: Literal["fixed_size", "recursive"] = ChunkingStrategy.RECURSIVE,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[Document]:
        """Split documents into chunks.

        Args:
            documents: List of documents to split.
            strategy: Chunking strategy to use.
            chunk_size: Maximum size of each chunk.
            chunk_overlap: Overlap between chunks.

        Returns:
            List of chunked documents with metadata.
        """
        chunked_docs = []

        for doc in documents:
            chunks = self.chunk_text(
                doc.page_content,
                strategy,
                chunk_size,
                chunk_overlap
            )

            for i, chunk in enumerate(chunks):
                chunked_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "chunk_count": len(chunks)
                    }
                )
                chunked_docs.append(chunked_doc)

        return chunked_docs
