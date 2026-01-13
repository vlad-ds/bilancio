"""Storage abstractions for experiment results."""

from .models import (
    RunStatus,
    RunArtifacts,
    RunResult,
    RegistryEntry,
)
from .protocols import ResultStore, RegistryStore
from .file_store import FileResultStore, FileRegistryStore
from .artifact_loaders import ArtifactLoader, LocalArtifactLoader
from .modal_artifact_loader import ModalVolumeArtifactLoader
from .supabase_client import (
    get_supabase_client,
    is_supabase_configured,
    SupabaseConfigError,
)
from .supabase_registry import SupabaseRegistryStore

__all__ = [
    "RunStatus",
    "RunArtifacts",
    "RunResult",
    "RegistryEntry",
    "ResultStore",
    "RegistryStore",
    "FileResultStore",
    "FileRegistryStore",
    "ArtifactLoader",
    "LocalArtifactLoader",
    "ModalVolumeArtifactLoader",
    # Supabase
    "get_supabase_client",
    "is_supabase_configured",
    "SupabaseConfigError",
    "SupabaseRegistryStore",
]
