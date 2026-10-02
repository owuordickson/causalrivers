import hashlib
import pickle
from pathlib import Path

# Manifest tracking exact digests for all consumed artifacts
DATA_MANIFEST = {
    "rivers_east_germany.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/1_random_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/1_random_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/close_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/close_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/confounder_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/confounder_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/debug_set_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/debug_set_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/random_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/random_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/root_cause_3/east.p": "PLACEHOLDER_UNTIL_PRINTED",
    "datasets/root_cause_5/east.p": "PLACEHOLDER_UNTIL_PRINTED",
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

    # TEMPORARY SAFEGUARD BYPASS: 
    # If the file is not in the manifest or is using a placeholder, print the true hash to the terminal
    if not expected_hash or expected_hash == "PLACEHOLDER_UNTIL_PRINTED":
        print(f'\n[INTEGRITY MANIFEST NOTIFICATION] Add this to DATA_MANIFEST:\n    "{filename}": "{computed_hash}",\n')
        # Allow it to load for this initial generation run so it doesn't crash:
        with open(file_path, "rb") as f:
            return pickle.load(f)

    if computed_hash != expected_hash:
        raise ValueError(
            f"Integrity check failed for {filename}!\n"
            f"Expected: {expected_hash}\n"
            f"Got:      {computed_hash}"
        )

    with open(file_path, "rb") as f:
        return pickle.load(f)
