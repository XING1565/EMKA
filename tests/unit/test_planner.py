from backend.app.runtime.models import RouteDecision
from backend.app.runtime.planner import TaskPlanner


def _tools():
    return ["search_docs", "read_doc", "summarize", "generate_report"]


def test_planner_generate_report_sequence():
    route = RouteDecision(intent="generate_report", confidence=0.9, reason="report")
    plan = TaskPlanner().plan("生成报告", route, _tools())

    assert [step.tool for step in plan.steps] == ["search_docs", "summarize", "generate_report"]


def test_planner_search_knowledge_only_search_docs():
    route = RouteDecision(intent="search_knowledge", confidence=0.9, reason="search")
    plan = TaskPlanner().plan("查资料", route, _tools())

    assert [step.tool for step in plan.steps] == ["search_docs"]


def test_planner_filters_missing_tools():
    route = RouteDecision(intent="generate_report", confidence=0.9, reason="report")
    plan = TaskPlanner().plan("生成报告", route, ["search_docs"])

    assert [step.tool for step in plan.steps] == ["search_docs"]
