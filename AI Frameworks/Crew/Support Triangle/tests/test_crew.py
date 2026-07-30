from crews.support_crew import SupportCrew, ROUTING_MAP


class TestClassificationParser:
    def test_billing(self):
        assert SupportCrew._parse_classification("billing invoice issue") == "billing"
        assert SupportCrew._parse_classification("billing") == "billing"

    def test_technical(self):
        assert SupportCrew._parse_classification("technical login problem") == "technical"

    def test_sales(self):
        assert SupportCrew._parse_classification("sales pricing question") == "sales"

    def test_escalate(self):
        assert SupportCrew._parse_classification("escalate unclear") == "escalate"
        assert SupportCrew._parse_classification("I need a human") == "escalate"

    def test_label_in_middle(self):
        assert SupportCrew._parse_classification("This is a billing query about invoice") == "billing"

    def test_case_insensitive(self):
        assert SupportCrew._parse_classification("Billing Issue") == "billing"
        assert SupportCrew._parse_classification("TECHNICAL Support") == "technical"


class TestValidationParser:
    def test_approved_simple(self):
        ok, fb = SupportCrew._parse_validation("APPROVED looks good")
        assert ok is True
        assert fb == ""

    def test_approved_with_leading_space(self):
        ok, fb = SupportCrew._parse_validation("  APPROVED all fine")
        assert ok is True

    def test_revise(self):
        ok, fb = SupportCrew._parse_validation("REVISE missing steps")
        assert ok is False
        assert "missing steps" in fb

    def test_revise_with_colon(self):
        ok, fb = SupportCrew._parse_validation("REVISE: missing steps")
        assert ok is False
        assert "missing steps" in fb

    def test_unknown_format(self):
        ok, fb = SupportCrew._parse_validation("Some random output")
        assert ok is False
        assert fb == "Some random output"


class TestRoutingMap:
    def test_all_categories_present(self):
        for cat in ("billing", "technical", "sales"):
            assert cat in ROUTING_MAP

    def test_each_has_required_keys(self):
        for cat, cfg in ROUTING_MAP.items():
            assert "agent_cls" in cfg
            assert "task_cls" in cfg
            assert "tools" in cfg

    def test_each_has_at_least_one_tool(self):
        for cat, cfg in ROUTING_MAP.items():
            assert len(cfg["tools"]) > 0, f"{cat} has no tools"

    def test_tool_names(self):
        assert {t.name for t in ROUTING_MAP["billing"]["tools"]} == {"Currency Converter", "Company Data"}
        assert {t.name for t in ROUTING_MAP["technical"]["tools"]} == {"Web Search", "Calculator"}
        sales_names = {t.name for t in ROUTING_MAP["sales"]["tools"]}
        assert "Web Search" in sales_names
        assert "Company Data" in sales_names
        assert "Weather" in sales_names
