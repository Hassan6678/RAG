from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from uuid import uuid4
from typing import Iterable, List, TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile


def load_env() -> None:
    """Load environment variables from a .env file if present."""
    env_path = get_project_root() / ".env"
    load_dotenv(dotenv_path=env_path, override=True)


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: Path) -> Path:
    """Create a directory if it does not exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_uploaded_files(uploaded_files: Iterable["UploadedFile"], target_dir: Path) -> List[Path]:
    """Persist uploaded Streamlit files to disk and return their paths."""
    ensure_dir(target_dir)
    saved_paths: List[Path] = []

    for uploaded_file in uploaded_files:
        safe_name = Path(uploaded_file.name).name
        if not safe_name.lower().endswith(".pdf"):
            raise ValueError(f"Unsupported file type for '{safe_name}'. Only PDF is allowed.")

        destination = target_dir / f"{uuid4().hex}_{safe_name}"
        uploaded_bytes = uploaded_file.getbuffer()
        if len(uploaded_bytes) == 0:
            raise ValueError(f"Uploaded file '{safe_name}' is empty.")

        with destination.open("wb") as handle:
            handle.write(uploaded_bytes)
        saved_paths.append(destination)

    return saved_paths


def compute_files_signature(paths: Iterable[Path]) -> str:
    """Compute a stable SHA-256 signature from file contents and names."""
    digest = sha256()
    for path in sorted(paths, key=lambda p: p.name):
        digest.update(path.name.encode("utf-8"))
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
    return digest.hexdigest()


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]


def get_cache_dir() -> Path:
    """Return the base cache directory used for uploads and indexes."""
    return ensure_dir(get_project_root() / ".cache")
