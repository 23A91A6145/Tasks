import sys
sys.path.insert(0, "/home/cherry/Desktop/1_Gen/Tasks/Crew/Custom Tools")

from experiments.docstring_experiment import run_experiment, print_results
from experiments.queries import (
    WORD_COUNT_QUERIES,
    UNIT_CONVERT_QUERIES,
    IRRELEVANT_QUERIES,
    get_all_queries,
)
from experiments.parameter_experiment import run_parameter_experiment, print_param_results
from experiments.validation_experiment import run_validation_experiment, print_validation_results


def get_desc(tool):
    return tool.description if hasattr(tool, "description") else (tool.__doc__ or "")


def cmd_experiment():
    results = run_experiment(mode="simulated")
    print_results(results)
    return results


def cmd_queries():
    print(f"Word count queries: {len(WORD_COUNT_QUERIES)}")
    for q in WORD_COUNT_QUERIES:
        print(f"  [WC] {q}")
    print(f"\nUnit converter queries: {len(UNIT_CONVERT_QUERIES)}")
    for q in UNIT_CONVERT_QUERIES:
        print(f"  [CV] {q}")
    print(f"\nIrrelevant queries: {len(IRRELEVANT_QUERIES)}")
    for q in IRRELEVANT_QUERIES:
        print(f"  [--] {q}")
    print(f"\nTotal: {len(get_all_queries())} queries")


def cmd_tools():
    from crew_tools import TOOL_REGISTRY
    for name, func in TOOL_REGISTRY.items():
        doc = get_desc(func).strip()
        print(f"  Tool: {name}")
        print(f"   Description ({len(doc)} chars): {doc[:80]}{'...' if len(doc) > 80 else ''}")
        print()


def cmd_inspect():
    from crew_tools import TOOL_REGISTRY
    versions = {"word_counter": ["v1", "v2", "v3", "v4"], "convert": ["v1", "v2", "v3", "v4"]}
    for base, suffixes in versions.items():
        print(f"\n{'=' * 72}")
        label = base.replace("_", " ").upper()
        print(f"  {label} — Docstring Versions")
        print(f"{'=' * 72}")
        for suf in suffixes:
            key = f"{base}_{suf}"
            func = TOOL_REGISTRY[key]
            doc = get_desc(func).strip()
            print(f"\n  --- {key} ({len(doc)} chars) ---")
            print(f"  {doc}")
        print()


def cmd_params():
    data = run_parameter_experiment()
    print_param_results(data)


def cmd_param_tools():
    from experiments.parameter_experiment import get_tool_schema
    from crew_tools import TOOL_REGISTRY
    for name in sorted(TOOL_REGISTRY):
        tool = TOOL_REGISTRY[name]
        schema = get_tool_schema(name)
        props = schema["properties"]
        req = schema["required"]
        print(f"\n{'=' * 60}")
        print(f"  {name}")
        print(f"{'=' * 60}")
        print(f"  Description: {get_desc(tool)[:100]}")
        print(f"  Parameters ({len(props)}):")
        for pname, pinfo in sorted(props.items()):
            req_mark = " [REQUIRED]" if pname in req else ""
            default_info = f" (default: {pinfo['default']})" if pinfo["has_default"] else ""
            desc = pinfo.get("description", "")[:60]
            print(f"    - {pname}: {pinfo['type']}{req_mark}{default_info}")
            if desc:
                print(f"      {desc}")
        print()


def cmd_validate():
    results = run_validation_experiment()
    print_validation_results(results)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Custom Tools via @tool Decorator — Docstring, Parameter & Validation Experiments"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="experiment",
        choices=["experiment", "queries", "tools", "inspect", "params", "param-tools", "validate"],
        help="Command to run (default: experiment)",
    )
    args = parser.parse_args()

    commands = {
        "experiment": cmd_experiment,
        "queries": cmd_queries,
        "tools": cmd_tools,
        "inspect": cmd_inspect,
        "params": cmd_params,
        "param-tools": cmd_param_tools,
        "validate": cmd_validate,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
