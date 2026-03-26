"""Claude Code headless mode executor."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import aiofiles
from tenacity import retry, stop_after_attempt, wait_exponential

from python_project.core.config import ClaudeConfig


class ClaudeCodeExecutor:
    """Execute tasks using Claude Code in headless mode."""

    def __init__(self, config: ClaudeConfig, workspace_root: Path):
        self.config = config
        self.workspace_root = workspace_root

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def execute(
        self,
        task_description: str,
        context: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> dict:
        """
        Execute a task using Claude Code headless mode.

        Args:
            task_description: Clear description of the task to perform
            context: Additional context (files, requirements, etc.)
            timeout: Override default timeout

        Returns:
            Execution result with status, changes, and metadata
        """
        # Build the prompt with context
        prompt = self._build_prompt(task_description, context)

        # Write prompt to temporary file
        prompt_file = self.workspace_root / ".claude_prompt"
        async with aiofiles.open(prompt_file, "w", encoding="utf-8") as f:
            await f.write(prompt)

        try:
            # Execute Claude Code in headless mode
            result = await self._run_claude_code(
                prompt_file=prompt_file,
                timeout=timeout or self.config.headless_timeout,
            )

            return result

        finally:
            # Cleanup
            if prompt_file.exists():
                prompt_file.unlink()

    def _build_prompt(self, task_description: str, context: Optional[dict]) -> str:
        """Build structured prompt for Claude Code."""
        sections = [
            "# Task Description",
            task_description,
            "",
        ]

        if context:
            if "requirements" in context:
                sections.extend(
                    [
                        "# Requirements",
                        "\n".join(f"- {r}" for r in context["requirements"]),
                        "",
                    ]
                )

            if "files_to_modify" in context:
                sections.extend(
                    [
                        "# Files to Modify",
                        "\n".join(f"- {f}" for f in context["files_to_modify"]),
                        "",
                    ]
                )

            if "constraints" in context:
                sections.extend(
                    [
                        "# Constraints",
                        "\n".join(f"- {c}" for c in context["constraints"]),
                        "",
                    ]
                )

        sections.extend(
            [
                "# Instructions",
                "1. Analyze the task and create a plan",
                "2. Make minimal, focused changes",
                "3. Ensure code quality and tests pass",
                "4. Commit changes with clear message",
                "",
                "Execute this task autonomously.",
            ]
        )

        return "\n".join(sections)

    async def _run_claude_code(
        self,
        prompt_file: Path,
        timeout: int,
    ) -> dict:
        """
        Run Claude Code CLI in headless mode.

        This method invokes Claude Code as a subprocess with the --headless flag.
        """
        cmd = [
            "claude",
            "--headless",
            "--prompt",
            str(prompt_file),
            "--workspace",
            str(self.workspace_root),
            "--output-format",
            "json",
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            if process.returncode != 0:
                return {
                    "status": "error",
                    "error": stderr.decode("utf-8"),
                    "return_code": process.returncode,
                }

            # Parse JSON output
            output = json.loads(stdout.decode("utf-8"))
            return {
                "status": "success",
                "changes": output.get("changes", []),
                "commits": output.get("commits", []),
                "message": output.get("message", ""),
            }

        except asyncio.TimeoutError:
            process.kill()
            return {
                "status": "timeout",
                "error": f"Execution exceeded {timeout} seconds",
            }
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Failed to parse output: {e}",
                "raw_output": stdout.decode("utf-8"),
            }
