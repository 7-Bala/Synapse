"""Replay artifact provenance validator."""

import hashlib
import json
import os


def sha256_file(filepath: str) -> str:
    """Computes SHA256 of a file's content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return hashlib.sha256(f.read().encode("utf-8")).hexdigest()


class ReplayValidator:
    """Validates the Merkle-style provenance tree of a generated replay."""

    def __init__(self, artifacts_dir: str, metrics_dir: str):
        self.artifacts_dir = artifacts_dir
        self.metrics_dir = metrics_dir

    def _verify_leaf_hash(
        self, filename: str, directory: str, expected_hash: str, name: str
    ) -> bool:
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            print(f"ERROR: {name} file missing: {path}")
            return False

        computed_hash = sha256_file(path)
        if computed_hash != expected_hash:
            print(f"ERROR: {name} hash mismatch in manifest.")
            return False
        return True

    def validate_certificate(self, cert_filename: str) -> bool:
        """Validates a specific certificate and its entire dependency tree."""
        cert_path = os.path.join(self.artifacts_dir, cert_filename)
        if not os.path.exists(cert_path):
            print(f"ERROR: Certificate not found: {cert_path}")
            return False

        with open(cert_path, "r", encoding="utf-8") as f:
            cert = json.load(f)

        # 1. Verify Manifest
        version = cert_filename.split("_")[-1].replace(".json", "")
        manifest_filename = f"manifest_{version}.json"
        manifest_path = os.path.join(self.artifacts_dir, manifest_filename)

        if not os.path.exists(manifest_path):
            print(f"ERROR: Manifest missing for certificate: {manifest_path}")
            return False

        computed_manifest_hash = sha256_file(manifest_path)
        if computed_manifest_hash != cert.get("manifest_hash"):
            print("ERROR: Manifest hash mismatch in certificate.")
            return False

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # 2. Verify Leaf Hashes
        expected_hashes = manifest.get("artifact_hashes", {})

        # Verify Events
        events_filename = f"events_supply_chain_{version}.json"
        if not self._verify_leaf_hash(
            events_filename,
            self.artifacts_dir,
            expected_hashes.get("events_json"),
            "Events",
        ):
            return False

        # Verify Metrics
        metrics_filename = f"metrics_report_{version}.json"
        if not self._verify_leaf_hash(
            metrics_filename,
            self.metrics_dir,
            expected_hashes.get("metrics_json"),
            "Metrics",
        ):
            return False

        # Verify Prompt Bundle
        prompt_bundle_filename = f"prompt_bundle_{version}.json"
        if not self._verify_leaf_hash(
            prompt_bundle_filename,
            self.artifacts_dir,
            expected_hashes.get("prompt_bundle_json"),
            "Prompt bundle",
        ):
            return False

        # 3. Verify Replay ID
        # The Replay ID is generated using the manifest hash BEFORE the replay_identifier was injected
        manifest_copy = manifest.copy()
        manifest_copy["replay_identifier"] = "PENDING"
        intermediate_manifest_hash = hashlib.sha256(json.dumps(manifest_copy, indent=2).encode("utf-8")).hexdigest()
        
        computed_events_hash = sha256_file(os.path.join(self.artifacts_dir, events_filename))
        computed_prompt_hash = sha256_file(os.path.join(self.artifacts_dir, prompt_bundle_filename))
        
        replay_id_str = f"{computed_events_hash}{intermediate_manifest_hash}{computed_prompt_hash}"
        computed_replay_id = hashlib.sha256(replay_id_str.encode("utf-8")).hexdigest()

        if computed_replay_id != manifest.get("replay_identifier"):
            print("ERROR: Replay ID mismatch in manifest.")
            return False

        if computed_replay_id != cert.get("replay_id"):
            print("ERROR: Replay ID mismatch in certificate.")
            return False

        print(f"SUCCESS: Provenance tree validated for {version}")
        print(f"Validated Replay ID: {computed_replay_id}")
        return True


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    metrics_dir = os.path.join(base_dir, "metrics")

    if not os.path.exists(artifacts_dir):
        print("No artifacts directory found. Run generate_demo.py first.")
        exit(0)

    validator = ReplayValidator(artifacts_dir, metrics_dir)
    certs = [f for f in os.listdir(artifacts_dir) if f.startswith("replay_certificate")]

    if not certs:
        print("No certificates found to validate.")
        exit(0)

    success = True
    for cert in certs:
        if not validator.validate_certificate(cert):
            success = False

    if not success:
        exit(1)
