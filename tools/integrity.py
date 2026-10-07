import hashlib
import json
import pickle
from pathlib import Path

# Path to the JSON run manifest that stores metadata about the datasets
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "run_manifest.json" # Path("../run_manifest.json")



def secure_load_pickle(file_path: Path):
    """
    Verifies SHA-256 digest directly against run_manifest.json before deserializing.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required benchmark artifact: {file_path}")

    # 1. Compute SHA-256 hash of the target file
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    computed_hash = hasher.hexdigest()

    # Convert the file path to a standardized relative string representation
    path_key = file_path.as_posix()
    expected_hash = None

    # 2. Lookup the expected hash from run_manifest.json
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            # Look inside both 'historical_runs' and 'new_runs' groups
            all_runs = manifest_data.get("data_runs", [])
            for run in all_runs:
                # Fallback to checking filename if filepath isn't populated for older records
                if run.get("filepath") == path_key or run.get("filename") == file_path.name:
                    expected_hash = run.get("sha256")
                    break
        except (OSError, json.JSONDecodeError) as e:
            print(f"[INTEGRITY WARNING] Could not read manifest file: {e}")

    # 3. Handle a missing or non-matching hash signature safely
    if not expected_hash:
        raise ValueError(f'\n[INTEGRITY MANIFEST NOTIFICATION] Path missing from manifest. Allowing initial run:\n'
              f'  Path: {path_key}\n  Hash: {computed_hash}\n')

    if computed_hash != expected_hash:
        raise ValueError(
            f"Integrity check failed for {path_key}!\n"
            f"Expected: {expected_hash}\n"
            f"Got:      {computed_hash}"
        )

    # 4. Safely load via context manager after successful verification (SIM115)
    with open(file_path, "rb") as f:
        return pickle.load(f)
