from backend.app.runtime.models import PlanStep, RouteDecision, TaskPlan


class TaskPlanner:
    def plan(self, message: str, route: RouteDecision, available_tools: list[str]) -> TaskPlan:
        allowed = set(available_tools)
        recipes = {
            "question": [
                ("search_docs", "retrieve relevant evidence"),
                ("summarize", "answer from retrieved evidence"),
            ],
            "summary": [
                ("search_docs", "retrieve source materials"),
                ("summarize", "summarize source materials"),
            ],
            "compare": [
                ("search_docs", "retrieve materials to compare"),
                ("summarize", "summarize comparison evidence"),
                ("generate_report", "generate comparison report"),
            ],
            "generate_report": [
                ("search_docs", "retrieve report evidence"),
                ("summarize", "summarize report evidence"),
                ("generate_report", "generate final report"),
            ],
            "search_knowledge": [
                ("search_docs", "search enterprise knowledge"),
            ],
            "multimodal_analysis": [
                ("search_docs", "retrieve multimodal evidence"),
                ("summarize", "summarize multimodal evidence"),
                ("generate_report", "generate multimodal analysis report"),
            ],
        }

        if route.intent == "execute_tool":
            requested = self._detect_explicit_tool(message, available_tools)
            selected = [(requested, f"execute {requested}")] if requested else []
        else:
            selected = recipes.get(route.intent, recipes["question"])

        steps: list[PlanStep] = []
        previous_id: str | None = None
        for tool, action in selected:
            if tool not in allowed:
                continue
            step_id = f"step_{len(steps) + 1}"
            step_input = {"query": message} if tool == "search_docs" else {}
            steps.append(
                PlanStep(
                    id=step_id,
                    action=action,
                    tool=tool,
                    input=step_input,
                    depends_on=[previous_id] if previous_id else [],
                )
            )
            previous_id = step_id
        return TaskPlan(steps=steps)

    def _detect_explicit_tool(self, message: str, available_tools: list[str]) -> str | None:
        text = (message or "").lower()
        for tool in available_tools:
            if tool.lower() in text:
                return tool
        return available_tools[0] if available_tools else None
