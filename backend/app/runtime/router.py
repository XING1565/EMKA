from backend.app.runtime.models import RouteDecision


class IntentRouter:
    def route(
        self,
        message: str,
        memory_context: dict | None = None,
        available_tools: list[str] | None = None,
    ) -> RouteDecision:
        text = (message or "").lower()
        modalities = self._detect_modalities(text)

        if len(modalities) >= 2 and any(k in text for k in ["分析", "结合", "综合", "一起", "多模态"]):
            return RouteDecision(
                intent="multimodal_analysis",
                confidence=0.9,
                required_modalities=modalities,
                reason="request asks to analyze multiple modalities together",
            )
        if any(k in text for k in ["报告", "周报", "风险总结", "生成一份", "markdown", "输出文档"]):
            return RouteDecision(
                intent="generate_report",
                confidence=0.88,
                required_modalities=modalities,
                reason="request asks for a structured report or final document",
            )
        if any(k in text for k in ["比较", "对比", "差异", "异同"]):
            return RouteDecision(
                intent="compare",
                confidence=0.86,
                required_modalities=modalities,
                reason="request asks to compare materials or items",
            )
        if any(k in text for k in ["总结", "摘要", "概括", "归纳"]):
            return RouteDecision(
                intent="summary",
                confidence=0.84,
                required_modalities=modalities,
                reason="request asks for a summary",
            )
        if any(k in text for k in ["搜索", "查找", "检索", "查询资料", "知识库", "文档里"]):
            return RouteDecision(
                intent="search_knowledge",
                confidence=0.82,
                required_modalities=modalities,
                reason="request asks to search enterprise knowledge",
            )
        if any(k in text for k in ["执行工具", "调用工具", "运行工具"]):
            return RouteDecision(
                intent="execute_tool",
                confidence=0.8,
                required_modalities=modalities,
                reason="request explicitly asks to execute a tool",
            )
        return RouteDecision(
            intent="question",
            confidence=0.7,
            required_modalities=modalities,
            reason="fallback question intent",
        )

    def _detect_modalities(self, text: str) -> list[str]:
        modalities: list[str] = []
        if any(k in text for k in ["图片", "图像", "截图", "ocr", "png", "jpg", "jpeg"]):
            modalities.append("image")
        if any(k in text for k in ["表格", "报表", "excel", "xlsx", "csv", "工作表"]):
            modalities.append("table")
        if any(k in text for k in ["文档", "pdf", "markdown", "md", "docx", "txt", "会议纪要"]):
            modalities.append("text")
        return modalities
