"""Main entry point for the autonomous workflow system."""

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
    config = load_config(config_path)

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(config)

    # Generate unique run ID
    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # Start workflow
    print(f"Starting workflow run: {run_id}")
    await orchestrator.start(run_id)

    # Execute complete workflow
    try:
        await orchestrator.execute()
        print(f"✅ Workflow completed successfully: {run_id}")
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
