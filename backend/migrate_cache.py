import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def migrate_cache():
    cache_dir = Path("cache")
    for filepath in cache_dir.glob("*.json"):
        with open(filepath, "r") as f:
            content = f.read()
        try:
            data = json.loads(content)
            if "metadata" in data and "payload" in data:
                continue  # already migrated

            checksum = hashlib.sha256(
                json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            now = datetime.now(timezone.utc)
            metadata = {
                "created_at": now.isoformat(),
                "expires_at": "2099-01-01T00:00:00+00:00",
                "ttl_seconds": 3153600000,
                "checksum": checksum,
                "schema_version": "1.0",
                "cache_version": "1.0",
                "provider": "filesystem",
                "generator": data.get("specialist", "unknown"),
            }

            envelope = {"metadata": metadata, "payload": data}

            with open(filepath, "w") as f:
                json.dump(
                    envelope, f, indent=None
                )  # No indent, to match exact cache behavior? Doesn't matter for hash
            print(f"Migrated {filepath.name}")
        except Exception as e:
            print(f"Failed to migrate {filepath.name}: {e}")


if __name__ == "__main__":
    migrate_cache()
