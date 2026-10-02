import hashlib
import pickle
from pathlib import Path

# Manifest tracking exact digests for all consumed artifacts
DATA_MANIFEST = {
    "1_random_3/east.p": "to-add sha",
    "1_random_5/east.p": "to-add sha",
    "close_3/east.p": "to-add sha",
    "close_5/east.p": "to-add sha",
    "confounder_3/east.p": "to-add sha",
    "confounder_5/east.p": "to-add sha",
    "debug_set_3/east.p": "to-add sha",
    "debug_set_5/east.p": "to-add sha",
    "random_3/east.p": "to-add sha",
    "random_5/east.p": "to-add sha",
    "root_cause_3/east.p": "to-add sha",
    "root_cause_5/east.p": "to-add sha",
    # Add hashes for all other expected labels/predictions/product graphs here
}


def secure_load_pickle(file_path: Path):
    """Verifies SHA-256 digest before deserializing any pickle artifact."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required benchmark artifact: {file_path}")

    # Compute SHA-256 hash
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    computed_hash = hasher.hexdigest()

    filename = file_path.name
    expected_hash = DATA_MANIFEST.get(filename)

    if not expected_hash:
        raise ValueError(f"Untrusted artifact: {filename} is not present in the integrity manifest.")

    if computed_hash != expected_hash:
        raise ValueError(
            f"Integrity check failed for {filename}!\n"
            f"Expected: {expected_hash}\n"
            f"Got:      {computed_hash}"
        )

    # Re-open safely via context manager now that hash matches perfectly
    with open(file_path, "rb") as f:
        return pickle.load(f)
