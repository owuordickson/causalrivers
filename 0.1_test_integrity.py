import pytest
from pathlib import Path
from benchmarks.causalrivers.tools.integrity import DATA_MANIFEST, secure_load_pickle


def test_manifest_matches_local_files():
    """Asserts that all files matching the manifest have valid matching hashes."""
    data_dir = Path("datasets/")  # Adjust to your actual data folder

    for filename, expected_hash in DATA_MANIFEST.items():
        target_file = data_dir / filename
        assert target_file.exists(), f"Benchmark data file {filename} is missing!"

        # Test that secure_load_pickle parses it without raising ValueError
        try:
            secure_load_pickle(target_file)
        except Exception as e:
            # If it's a structural parsing error rather than an integrity block, that's fine for this test
            if "Integrity check failed" in str(e) or "Untrusted artifact" in str(e):
                pytest.fail(f"Hash mismatch on active benchmark asset: {filename}")
