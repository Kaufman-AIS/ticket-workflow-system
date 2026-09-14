#!/usr/bin/env python3
"""Create a task and doc via PacaClient. Env: PACA_API_URL, PACA_API_KEY, PACA_PROJECT_ID."""
import os
import sys

from integrations.paca_client import PacaClient, PacaError


def main() -> int:
    base = os.environ["PACA_API_URL"]
    key = os.environ["PACA_API_KEY"]
    project = os.environ["PACA_PROJECT_ID"]
    client = PacaClient(base, key)
    try:
        task = client.create_task(project, title="smoke-task", description="api smoke")
        doc = client.create_document(project, title="smoke-doc", markdown="# smoke\n")
        print(f"OK task={task.id} doc={doc.id}")
        return 0
    except PacaError as e:
        print(f"FAIL {e}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
