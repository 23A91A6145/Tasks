from tools.calculator import calculator_tool
from tools.company_data import company_data_tool


class TestCalculator:
    def test_basic_arithmetic(self):
        assert calculator_tool.run("150 * 0.15") == "22.5"
        assert calculator_tool.run("1024 / 8") == "128"
        assert calculator_tool.run("100 + 200") == "300"
        assert calculator_tool.run("500 - 30") == "470"

    def test_parentheses(self):
        assert calculator_tool.run("(2000 + 500) * 0.08") == "200"

    def test_division(self):
        result = calculator_tool.run("10 / 3")
        assert result.startswith("3.3333")

    def test_modulo(self):
        assert calculator_tool.run("17 % 5") == "2"

    def test_power(self):
        assert calculator_tool.run("2 ** 10") == "1024"

    def test_negative(self):
        assert calculator_tool.run("-5 + 10") == "5"

    def test_decimal(self):
        assert calculator_tool.run("0.1 + 0.2") == "0.3"

    def test_invalid_expression(self):
        result = calculator_tool.run("2 + 'a'")
        assert "Error" in result or "error" in result

    def test_empty(self):
        result = calculator_tool.run("")
        assert "Error" in result or "error" in result

    def test_deep_nesting(self):
        deep = "+".join(["1"] * 200)
        result = calculator_tool.run(deep)
        assert isinstance(result, str)

    def test_division_by_zero(self):
        result = calculator_tool.run("1/0")
        assert "Error" in result


class TestCompanyData:
    def test_customer_by_id(self):
        r = company_data_tool.run("customer C1001")
        assert "Alice Johnson" in r
        assert "Pro" in r
        assert "active" in r

    def test_customer_by_name(self):
        r = company_data_tool.run("customer Alice")
        assert "Alice Johnson" in r

    def test_all_customers(self):
        r = company_data_tool.run("list all customers")
        assert "C1001" in r
        assert "C1002" in r
        assert "C1003" in r

    def test_invoice_by_id(self):
        r = company_data_tool.run("invoice INV-1243")
        assert "INV-1243" in r
        assert "99.00" in r
        assert "paid" in r

    def test_all_invoices(self):
        r = company_data_tool.run("show invoices")
        assert "INV-1243" in r
        assert "INV-1244" in r
        assert "INV-1245" in r

    def test_order_by_id(self):
        r = company_data_tool.run("order ORD-901")
        assert "ORD-901" in r
        assert "999.00" in r

    def test_product_by_name(self):
        r = company_data_tool.run("product Pro")
        assert "Pro" in r
        assert "5 users" in r
        assert "50GB" in r

    def test_all_plans(self):
        r = company_data_tool.run("pricing plans")
        assert "Basic" in r
        assert "Pro" in r
        assert "Enterprise" in r

    def test_unknown_query(self):
        r = company_data_tool.run("something completely unknown")
        assert "Try" in r or "available" in r
