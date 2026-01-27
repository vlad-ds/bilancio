"""Artifact loaders for fetching artifacts from various storage backends."""

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ArtifactLoader(Protocol):
    """Protocol for loading artifacts from any storage backend.

    This protocol defines the interface for artifact loading, allowing
    different implementations for local filesystem, cloud storage, etc.
    """

    def load_bytes(self, reference: str) -> bytes:
        """Load artifact as bytes.

        Args:
            reference: The artifact reference (e.g., relative path or URI).

        Returns:
            The artifact contents as bytes.

        Raises:
            FileNotFoundError: If the artifact does not exist.
        """
        ...

    def load_text(self, reference: str) -> str:
        """Load artifact as text.

        Args:
            reference: The artifact reference (e.g., relative path or URI).

        Returns:
            The artifact contents as a string.

        Raises:
            FileNotFoundError: If the artifact does not exist.
        """
        ...

    def exists(self, reference: str) -> bool:
        """Check if artifact exists.

        Args:
            reference: The artifact reference (e.g., relative path or URI).

        Returns:
            True if the artifact exists, False otherwise.
        """
        ...


class LocalArtifactLoader:
    """Load artifacts from local filesystem.

    This implementation resolves artifact references as paths relative
    to a base directory.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize with base path for relative references.

        Args:
            base_path: The base directory for resolving relative paths.
        """
        self.base_path = Path(base_path)

    def load_bytes(self, reference: str) -> bytes:
        """Load artifact as bytes from filesystem.

        Args:
            reference: Relative path to the artifact from base_path.

        Returns:
            The artifact contents as bytes.

        Raises:
            FileNotFoundError: If the artifact does not exist.
        """
        path = self.base_path / reference
        return path.read_bytes()

    def load_text(self, reference: str) -> str:
        """Load artifact as text from filesystem.

        Args:
            reference: Relative path to the artifact from base_path.

        Returns:
            The artifact contents as a string.

        Raises:
            FileNotFoundError: If the artifact does not exist.
        """
        path = self.base_path / reference
        return path.read_text(encoding="utf-8")

    def exists(self, reference: str) -> bool:
        """Check if artifact exists on filesystem.

        Args:
            reference: Relative path to the artifact from base_path.

        Returns:
            True if the artifact exists, False otherwise.
        """
        path = self.base_path / reference
        return path.exists()
