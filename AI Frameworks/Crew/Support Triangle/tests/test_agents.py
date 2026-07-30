from agents.router import RouterAgent
from agents.billing import BillingAgent
from agents.technical import TechnicalAgent
from agents.sales import SalesAgent
from agents.validator import ValidatorAgent

from tools.custom_api import currency_tool
from tools.company_data import company_data_tool
from tools.web_search import web_search_tool
from tools.calculator import calculator_tool
from tools.custom_api import weather_tool


class TestRouterAgent:
    def test_creation(self):
        agent = RouterAgent().get()
        assert agent.role == "Support Request Router"

    def test_no_tools_by_default(self):
        agent = RouterAgent().get()
        assert len(agent.tools) == 0

    def test_with_tools(self):
        agent = RouterAgent(tools=[web_search_tool]).get()
        assert len(agent.tools) == 1


class TestBillingAgent:
    def test_creation(self):
        agent = BillingAgent().get()
        assert agent.role == "Billing Support Specialist"

    def test_with_tools(self):
        tools = [currency_tool, company_data_tool]
        agent = BillingAgent(tools=tools).get()
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "Currency Converter"
        assert agent.tools[1].name == "Company Data"


class TestTechnicalAgent:
    def test_creation(self):
        agent = TechnicalAgent().get()
        assert agent.role == "Technical Support Specialist"

    def test_with_tools(self):
        tools = [web_search_tool, calculator_tool]
        agent = TechnicalAgent(tools=tools).get()
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "Web Search"
        assert agent.tools[1].name == "Calculator"


class TestSalesAgent:
    def test_creation(self):
        agent = SalesAgent().get()
        assert agent.role == "Sales Support Specialist"

    def test_with_tools(self):
        tools = [web_search_tool, company_data_tool, weather_tool]
        agent = SalesAgent(tools=tools).get()
        assert len(agent.tools) == 3


class TestValidatorAgent:
    def test_creation(self):
        agent = ValidatorAgent().get()
        assert agent.role == "Response Quality Validator"

    def test_no_tools(self):
        agent = ValidatorAgent().get()
        assert len(agent.tools) == 0
