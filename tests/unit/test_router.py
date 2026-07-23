from backend.app.runtime.router import IntentRouter


def test_router_classifies_report_with_modalities():
    route = IntentRouter().route("分析这张截图和项目周报表，生成一份风险总结")

    assert route.intent in {"generate_report", "multimodal_analysis"}
    assert "image" in route.required_modalities
    assert "table" in route.required_modalities


def test_router_classifies_search_compare_summary_question():
    router = IntentRouter()

    assert router.route("检索知识库里的项目A资料").intent == "search_knowledge"
    assert router.route("比较两个方案的差异").intent == "compare"
    assert router.route("总结这份会议纪要").intent == "summary"
    assert router.route("项目A现在怎么样").intent == "question"


def test_router_detects_document_modalities():
    route = IntentRouter().route("阅读 PDF 和 docx 文档")

    assert route.required_modalities == ["text"]
