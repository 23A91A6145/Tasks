import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from providers.file_provider import FileProvider

logging.basicConfig(level=logging.INFO)

def main():
    print("--- File Provider Standalone Demo ---")
    provider = FileProvider()
    skills = provider.load_skills()
    
    print(f"Loaded {len(skills)} skills from filesystem:")
    for skill in skills:
        print(f"\n- Name: {skill.name}")
        print(f"  Source path: {skill.source_path}")
        print(f"  Description: {skill.description}")
        print(f"  Version:     {skill.version}")
        print(f"  Parameters:  {list(skill.parameters.get('properties', {}).keys())}")
        
        # Test execute (with mock args)
        try:
            if skill.name == "system_info":
                res = skill.execute()
                print(f"  Test Exec:   {res}")
            elif skill.name == "math_factorial":
                res = skill.execute(n=5)
                print(f"  Test Exec:   factorial(5) = {res}")
            elif skill.name == "markdown_greet":
                res = skill.execute(name="Alice")
                print(f"  Test Exec:   {res}")
        except Exception as e:
            print(f"  Execution Error: {e}")

if __name__ == "__main__":
    main()
