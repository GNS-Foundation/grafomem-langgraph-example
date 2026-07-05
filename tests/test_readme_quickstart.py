import os
import re
import pytest

def test_readme_quickstart():
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    with open(readme_path, "r") as f:
        content = f.read()
        
    # Extract the first python code block
    match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
    assert match is not None, "Could not find python code block in README.md"
    code = match.group(1)
    
    # Execute it in a clean namespace
    namespace = {}
    try:
        exec(code, namespace)
    except Exception as e:
        pytest.fail(f"README quickstart failed to execute: {e}")
        
    assert "receipt" in namespace
    assert "public_key" in namespace
    
    receipt = namespace["receipt"]
    public_key = namespace["public_key"]
    assert receipt.verify(public_key) is True
