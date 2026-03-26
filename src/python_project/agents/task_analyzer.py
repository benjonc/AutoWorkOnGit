"""Task analyzer agent - breaks down requirements into executable tasks."""

from typing import Any

import yaml

from python_project.agents.base import AgentResult, BaseAgent


class TaskDependency:
    """Represents a dependency between tasks."""

    task_id: str
    depends_on: list[str]


class TaskAnalyzerAgent(BaseAgent):
    """
    Agent that analyzes requirements and breaks them down into:
    - Granular tasks
    - Dependency graph
    - Execution order
    - Parallel execution opportunities
    """

    async def execute(self, requirements_doc: str) -> AgentResult:
        """
        Analyze requirements and generate task breakdown.

        Args:
            requirements_doc: Full requirements document in markdown

        Returns:
            AgentResult with task list and dependency graph
        """
        self.log("Analyzing requirements and breaking down into tasks")

        # Phase 1: Extract requirements
        requirements = await self._extract_requirements(requirements_doc)

        # Phase 2: Generate tasks for each requirement
        tasks = await self._generate_tasks(requirements)

        # Phase 3: Analyze dependencies between tasks
        dependency_graph = await self._analyze_dependencies(tasks)

        # Phase 4: Calculate parallel execution opportunities
        execution_plan = await self._create_execution_plan(tasks, dependency_graph)

        # Save task breakdown
        task_file = await self._save_task_breakdown(execution_plan)

        return AgentResult(
            success=True,
            message=f"Generated {len(tasks)} tasks with dependency analysis",
            data={
                "task_count": len(tasks),
                "max_parallel": execution_plan["max_parallel"],
                "task_file": str(task_file),
                "execution_phases": execution_plan["phases"],
            },
        )

    async def _extract_requirements(self, doc: str) -> list[dict]:
        """Extract structured requirements from markdown document."""
        # In real implementation, use Claude API to parse
        # For now, return sample data
        return [
            {"id": "FR-001", "description": "User authentication", "priority": "high"},
            {"id": "FR-002", "description": "Data management", "priority": "high"},
        ]

    async def _generate_tasks(self, requirements: list[dict]) -> list[dict]:
        """Generate granular tasks for each requirement."""
        tasks = []

        for req in requirements:
            # Break down requirement into implementation tasks
            if req["id"] == "FR-001":
                tasks.extend(
                    [
                        {
                            "id": "TASK-001",
                            "requirement_id": "FR-001",
                            "title": "Design authentication schema",
                            "description": "Design user authentication database schema",
                            "type": "implementation",
                            "estimated_hours": 2,
                        },
                        {
                            "id": "TASK-002",
                            "requirement_id": "FR-001",
                            "title": "Implement user registration endpoint",
                            "description": "Create API endpoint for user registration",
                            "type": "implementation",
                            "estimated_hours": 4,
                            "dependencies": ["TASK-001"],
                        },
                        {
                            "id": "TASK-003",
                            "requirement_id": "FR-001",
                            "title": "Implement login endpoint",
                            "description": "Create API endpoint for user login",
                            "type": "implementation",
                            "estimated_hours": 3,
                            "dependencies": ["TASK-001"],
                        },
                    ]
                )
            elif req["id"] == "FR-002":
                tasks.extend(
                    [
                        {
                            "id": "TASK-004",
                            "requirement_id": "FR-002",
                            "title": "Design data model",
                            "description": "Design core data model and relationships",
                            "type": "implementation",
                            "estimated_hours": 3,
                        },
                        {
                            "id": "TASK-005",
                            "requirement_id": "FR-002",
                            "title": "Implement CRUD operations",
                            "description": "Create CRUD API endpoints for data management",
                            "type": "implementation",
                            "estimated_hours": 6,
                            "dependencies": ["TASK-004"],
                        },
                    ]
                )

        return tasks

    async def _analyze_dependencies(self, tasks: list[dict]) -> dict:
        """
        Analyze task dependencies and build dependency graph.

        Returns:
            Dict with task_id -> list of dependent task_ids
        """
        graph = {}

        for task in tasks:
            task_id = task["id"]
            dependencies = task.get("dependencies", [])

            # Build reverse dependency map
            for dep_id in dependencies:
                if dep_id not in graph:
                    graph[dep_id] = []
                graph[dep_id].append(task_id)

            if task_id not in graph:
                graph[task_id] = []

        return graph

    async def _create_execution_plan(
        self,
        tasks: list[dict],
        dependency_graph: dict,
    ) -> dict:
        """
        Create execution plan with parallel execution opportunities.

        Uses topological sort to identify execution phases.
        """
        # Calculate in-degree for each task
        in_degree = {task["id"]: 0 for task in tasks}
        task_map = {task["id"]: task for task in tasks}

        for task in tasks:
            for _dep_id in task.get("dependencies", []):
                in_degree[task["id"]] += 1

        # Identify phases (tasks that can run in parallel)
        phases = []
        remaining_tasks = set(task_map.keys())

        while remaining_tasks:
            # Find tasks with no dependencies in remaining set
            phase = [task_id for task_id in remaining_tasks if in_degree[task_id] == 0]

            if not phase:
                # Circular dependency detected
                raise ValueError("Circular dependency detected in task graph")

            phases.append(phase)

            # Remove these tasks and update in-degrees
            for task_id in phase:
                remaining_tasks.remove(task_id)
                # Decrement in-degree for dependent tasks
                for dependent_id in dependency_graph.get(task_id, []):
                    in_degree[dependent_id] -= 1

        return {
            "phases": phases,
            "max_parallel": max(len(phase) for phase in phases),
            "total_phases": len(phases),
            "tasks": task_map,
        }

    async def _save_task_breakdown(self, execution_plan: dict) -> Any:
        """Save task breakdown to YAML file."""
        from pathlib import Path

        import aiofiles

        task_file = Path("docs/tasks/task_breakdown.yaml")
        task_file.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(task_file, "w", encoding="utf-8") as f:
            await f.write(yaml.dump(execution_plan, default_flow_style=False))

        return task_file
