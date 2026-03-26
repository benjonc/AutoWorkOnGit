"""Requirements collection agent - interactive dialogue with user."""

from pathlib import Path

import aiofiles

from python_project.agents.base import AgentResult, BaseAgent


class RequirementsCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting requirements from user.

    Conducts interactive dialogue to understand:
    - Project goals and scope
    - Functional requirements
    - Technical constraints
    - Success criteria
    """

    async def execute(self, initial_request: str) -> AgentResult:
        """
        Execute requirements collection dialogue.

        Args:
            initial_request: User's initial project request

        Returns:
            AgentResult with requirements document
        """
        self.log(f"Starting requirements collection for: {initial_request}")

        # Phase 1: Understand project scope
        project_scope = await self._collect_project_scope(initial_request)

        # Phase 2: Collect functional requirements
        functional_reqs = await self._collect_functional_requirements(project_scope)

        # Phase 3: Collect technical constraints
        technical_constraints = await self._collect_technical_constraints()

        # Phase 4: Define success criteria
        success_criteria = await self._collect_success_criteria()

        # Generate requirements document
        requirements_doc = await self._generate_requirements_document(
            project_scope=project_scope,
            functional_reqs=functional_reqs,
            technical_constraints=technical_constraints,
            success_criteria=success_criteria,
        )

        # Save to file
        doc_path = await self._save_requirements_document(requirements_doc)

        return AgentResult(
            success=True,
            message="Requirements collected and documented successfully",
            data={
                "document_path": str(doc_path),
                "requirements_count": len(functional_reqs),
            },
        )

    async def _collect_project_scope(self, initial_request: str) -> dict:
        """Collect project scope through interactive dialogue."""
        # In real implementation, this would use Claude API for natural conversation
        # For now, return structured data
        return {
            "initial_request": initial_request,
            "project_type": "web_application",
            "target_users": "end_users",
            "timeline": "flexible",
        }

    async def _collect_functional_requirements(self, scope: dict) -> list[dict]:
        """Collect functional requirements."""
        return [
            {
                "id": "FR-001",
                "description": "User authentication",
                "priority": "high",
                "details": [],
            },
            {
                "id": "FR-002",
                "description": "Data management",
                "priority": "high",
                "details": [],
            },
        ]

    async def _collect_technical_constraints(self) -> list[dict]:
        """Collect technical constraints."""
        return [
            {
                "id": "TC-001",
                "constraint": "Python 3.11+",
                "rationale": "Modern async features",
            },
        ]

    async def _collect_success_criteria(self) -> list[dict]:
        """Collect success criteria."""
        return [
            {
                "id": "SC-001",
                "criterion": "All tests passing",
                "measurable": True,
            },
        ]

    async def _generate_requirements_document(
        self,
        project_scope: dict,
        functional_reqs: list[dict],
        technical_constraints: list[dict],
        success_criteria: list[dict],
    ) -> str:
        """Generate comprehensive requirements document in markdown."""
        doc_sections = [
            "# Requirements Document\n",
            "## Project Scope\n",
            f"- **Initial Request**: {project_scope['initial_request']}\n",
            f"- **Project Type**: {project_scope['project_type']}\n",
            f"- **Target Users**: {project_scope['target_users']}\n\n",
            "## Functional Requirements\n",
        ]

        for req in functional_reqs:
            doc_sections.append(
                f"### {req['id']}: {req['description']}\n" f"- Priority: {req['priority']}\n\n"
            )

        doc_sections.append("## Technical Constraints\n")
        for constraint in technical_constraints:
            doc_sections.append(
                f"- {constraint['id']}: {constraint['constraint']} "
                f"(Rationale: {constraint['rationale']})\n"
            )

        doc_sections.append("\n## Success Criteria\n")
        for criterion in success_criteria:
            doc_sections.append(f"- {criterion['criterion']}\n")

        return "".join(doc_sections)

    async def _save_requirements_document(self, document: str) -> Path:
        """Save requirements document to file."""
        docs_dir = Path("docs/requirements")
        docs_dir.mkdir(parents=True, exist_ok=True)

        doc_path = docs_dir / "requirements.md"
        async with aiofiles.open(doc_path, "w", encoding="utf-8") as f:
            await f.write(document)

        return doc_path
