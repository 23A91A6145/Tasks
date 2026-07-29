import json
import xml.etree.ElementTree as ET

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class YamlParseInput(BaseModel):
    yaml_text: str = Field(description="YAML string to parse")


@tool(args_schema=YamlParseInput)
def yaml_parse(yaml_text: str) -> str:
    """Parse a YAML string into JSON.

    Args:
        yaml_text: YAML content.

    Returns:
        JSON representation of the YAML data.
    """
    try:
        import yaml
    except ImportError:
        return "Error: pyyaml is required. Install with: pip install pyyaml"
    try:
        data = yaml.safe_load(yaml_text)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Error parsing YAML: {e}"


class YamlDumpInput(BaseModel):
    json_text: str = Field(description="JSON string to convert to YAML")


@tool(args_schema=YamlDumpInput)
def yaml_dump(json_text: str) -> str:
    """Convert a JSON string to YAML.

    Args:
        json_text: JSON string.

    Returns:
        YAML-formatted output.
    """
    try:
        import yaml
    except ImportError:
        return "Error: pyyaml is required. Install with: pip install pyyaml"
    try:
        data = json.loads(json_text)
        return yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}"
    except Exception as e:
        return f"Error converting to YAML: {e}"


class TomlParseInput(BaseModel):
    toml_text: str = Field(description="TOML string to parse")


@tool(args_schema=TomlParseInput)
def toml_parse(toml_text: str) -> str:
    """Parse a TOML string into JSON.

    Args:
        toml_text: TOML content.

    Returns:
        JSON representation.
    """
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return "Error: tomli is required for Python <3.11. Install with: pip install tomli"
    try:
        data = tomllib.loads(toml_text)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Error parsing TOML: {e}"


class XmlParseInput(BaseModel):
    xml_text: str = Field(description="XML string to parse")


@tool(args_schema=XmlParseInput)
def xml_parse(xml_text: str) -> str:
    """Parse XML into a JSON-like structure.

    Args:
        xml_text: XML content.

    Returns:
        JSON representation of the XML tree.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"

    def _element_to_dict(el):
        children = list(el)
        attrs = dict(el.attrib)
        result: dict = {}
        if el.text and el.text.strip():
            result["#text"] = el.text.strip()
        if attrs:
            result["@attrs"] = attrs
        if children:
            child_dict: dict = {}
            for child in children:
                name = child.tag
                child_data = _element_to_dict(child)
                if name in child_dict:
                    if not isinstance(child_dict[name], list):
                        child_dict[name] = [child_dict[name]]
                    child_dict[name].append(child_data)
                else:
                    child_dict[name] = child_data
            result.update(child_dict)
        if not result:
            return el.text.strip() if el.text and el.text.strip() else None
        return result

    data = {root.tag: _element_to_dict(root)}
    return json.dumps(data, indent=2, default=str)


class JsonPrettifyInput(BaseModel):
    json_text: str = Field(description="JSON string to prettify")
    indent: int = Field(default=2, ge=0, le=8, description="Indent spaces")


@tool(args_schema=JsonPrettifyInput)
def json_prettify(json_text: str, indent: int = 2) -> str:
    """Format/prettify a JSON string.

    Args:
        json_text: Raw JSON string.
        indent: Number of spaces for indentation.

    Returns:
        Prettified JSON string.
    """
    try:
        data = json.loads(json_text)
        return json.dumps(data, indent=indent, default=str)
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}"
