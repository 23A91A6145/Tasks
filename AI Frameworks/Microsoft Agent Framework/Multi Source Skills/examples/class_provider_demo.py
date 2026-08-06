import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from providers.class_provider import ClassProvider, register_class_instance, skill_method

logging.basicConfig(level=logging.INFO)

# Define a custom local class to show programmatic registration
class CustomLocalSkills:
    @skill_method(
        name="local_uppercase",
        description="Converts text to uppercase."
    )
    def uppercase(self, text: str) -> str:
        return text.upper()

def main():
    print("--- Class Provider Standalone Demo ---")
    
    # Register local class instance programmatically
    register_class_instance(CustomLocalSkills())
    
    provider = ClassProvider()
    skills = provider.load_skills()
    
    print(f"Loaded {len(skills)} class-based skills:")
    for skill in skills:
        print(f"\n- Name: {skill.name}")
        print(f"  Source path: {skill.source_path}")
        print(f"  Description: {skill.description}")
        print(f"  Parameters:  {list(skill.parameters.get('properties', {}).keys())}")
        
        # Test execute (with mock args)
        try:
            if skill.name == "math_subtract":
                res = skill.execute(a=50, b=15)
                print(f"  Test Exec:   subtract(50, 15) = {res}")
            elif skill.name == "local_uppercase":
                res = skill.execute(text="hello python")
                print(f"  Test Exec:   {res}")
        except Exception as e:
            print(f"  Execution Error: {e}")

if __name__ == "__main__":
    main()
