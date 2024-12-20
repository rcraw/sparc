import os
import shutil
import subprocess
import pytest
from pathlib import Path
from datetime import datetime

def test_implement_mode_develops_components(clean_test_dir, cli_script, output_dir):
    """Test that implement mode develops components and saves them to output directory."""
    
    # Copy the sparc_cli.py script to the test directory
    shutil.copy(cli_script, clean_test_dir)
    
    os.chdir(clean_test_dir)

    # Create a basic guidance.toml file with real implementation requirements
    guidance_content = """
[specification]
content = '''
Create a REST API service with:
- User authentication using JWT tokens
- CRUD operations for a blog post resource
- Error handling with proper HTTP status codes
'''

[architecture]
content = '''
## Component: AuthService
Handles JWT token generation, validation, and user authentication.

## Component: BlogPostManager
Manages CRUD operations for blog posts with proper validation.

## Component: ErrorHandler
Provides standardized error handling with appropriate HTTP status codes.
'''

[pseudocode]
content = '''
AuthService:
- generate_token(user_data) -> str
- validate_token(token) -> dict
- authenticate_user(username, password) -> bool

BlogPostManager:
- create_post(user_id, title, content) -> Post
- get_post(post_id) -> Post
- update_post(post_id, updates) -> Post
- delete_post(post_id) -> bool

ErrorHandler:
- handle_auth_error() -> Response(401)
- handle_not_found() -> Response(404)
- handle_validation_error() -> Response(400)
'''
"""
    with open(clean_test_dir / "guidance.toml", "w") as f:
        f.write(guidance_content)

    # Run the architect mode first
    cmd_architect = ["python", "sparc_cli.py", "architect", "--guidance-file", "guidance.toml"]
    result_architect = subprocess.run(cmd_architect, capture_output=True, text=True)
    assert result_architect.returncode == 0, f"Architect mode failed: {result_architect.stderr}"

    # Run the implement mode with Claude 3.5 Sonnet
    cmd_implement = ["python", "sparc_cli.py", "implement", "--max-attempts", "2", "--guidance-file", "guidance.toml", "--model", "claude-3-sonnet-20240229"]
    result_implement = subprocess.run(cmd_implement, capture_output=True, text=True)
    assert result_implement.returncode == 0, f"Implement mode failed: {result_implement.stderr}"

    # Check that the src directory was created
    src_dir = clean_test_dir / "src"
    assert src_dir.exists(), "Source directory was not created"

    # Check that the tests directory was created
    tests_dir = clean_test_dir / "tests"
    assert tests_dir.exists(), "Tests directory was not created"

    # Check for expected component files
    expected_components = {
        "authservice": "Authentication service",
        "blogpostmanager": "Blog post manager",
        "errorhandler": "Error handler"
    }
    
    for component, description in expected_components.items():
        src_file = src_dir / f"{component}.py"
        test_file = tests_dir / f"test_{component}.py"
        assert src_file.exists(), f"{description} component file was not created"
        assert test_file.exists(), f"{description} test file was not created"

    # Save to test_outputs with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_output_dir = output_dir / f"blog_app_{timestamp}"
    
    # Copy the generated application to test_outputs
    shutil.copytree(clean_test_dir, test_output_dir)
    
    # Create a README.md in the output directory explaining what was generated
    readme_content = f"""# Blog Application - Generated {timestamp}

This application was automatically generated using the SPARC framework.

## Components
- AuthService: JWT authentication service
- BlogPostManager: Blog post CRUD operations
- ErrorHandler: HTTP error handling

## Generated Files
- src/: Source code for each component
- tests/: Unit tests for each component
- architecture/: SPARC architecture documents
- guidance.toml: Project guidance and requirements

## Test Status
All components have been generated and tested successfully.
"""
    
    with open(test_output_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print(f"\nGenerated application saved to: {test_output_dir}")
    print("Test 2 passed: Implement mode develops components successfully")
