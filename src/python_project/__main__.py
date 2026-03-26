"""Entry point for running python_project as a module."""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from python_project.core.config import load_config
from python_project.workflows.orchestrator import WorkflowOrchestrator


async def main():
    """Run the autonomous workflow."""
    # Load configuration
    config_path = Path("config/config.yaml")
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print("[ERROR] Configuration file not found!")
        print("Please create config/config.yaml from config/config.yaml.example")
        return
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(config)

    # Generate unique run ID
    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # Start workflow
    print(f"Starting workflow run: {run_id}")
    print("=" * 60)

    try:
        await orchestrator.start(run_id)
        await orchestrator.execute()
        print("=" * 60)
        print(f"[SUCCESS] Workflow completed successfully: {run_id}")
    except Exception as e:
        print("=" * 60)
        print(f"[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

