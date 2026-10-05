from aurora.agent.audit import AgentAuditLog
from aurora.agent.planner import AgentPlanner


def test_audit_records_structured_event():
    audit = AgentAuditLog()
    event = audit.record("execute", "web", "success", url="https://example.com")
    assert event.tool == "web"
    assert event.status == "success"
    assert len(audit.events) == 1


def test_planner_only_creates_intent():
    plan = AgentPlanner().plan("pesquisar", "consultar", "web", "fonte externa")
    assert plan.tool == "web"
    assert plan.reason == "fonte externa"
