#!/usr/bin/env python3
"""
SimFlo Figma-to-RAG Pipeline Demo Script

This script demonstrates the complete 9-step pipeline by:
1. Running all steps with project-specific data
2. Setting up the demo server
3. Opening the generated UI in your browser
4. Displaying generated code samples

Usage:
    python3 run-pipeline-demo.py --project PROJECT_NAME
    python3 run-pipeline-demo.py --create-project PROJECT_NAME
    python3 run-pipeline-demo.py --list
"""

import os
import sys
import json
import subprocess
import time
import webbrowser
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def log_step(step_num: int, step_name: str, description: str):
    """Log a pipeline step with formatting."""
    print(f"\n{'='*80}")
    print(f"🔄 Step {step_num}: {step_name}")
    print(f"📝 {description}")
    print(f"{'='*80}")

def log_success(message: str):
    """Log success message."""
    print(f"✅ {message}")

def log_info(message: str):
    """Log info message."""
    print(f"ℹ️  {message}")

def log_error(message: str):
    """Log error message."""
    print(f"❌ {message}")

def run_command(cmd: List[str], description: str, cwd: Optional[Path] = None, env: Dict[str, str] = None) -> bool:
    """Run a command and return success status."""
    log_info(f"Running: {' '.join(cmd)}")
    try:
        # Set up environment with PYTHONPATH
        process_env = os.environ.copy()
        process_env["PYTHONPATH"] = str(PROJECT_ROOT / "v2")

        # Add custom environment variables
        if env:
            process_env.update(env)

        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            env=process_env,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            log_success(f"{description} - Completed successfully")
            if result.stdout:
                print(f"📤 Output: {result.stdout.strip()}")
            return True
        else:
            log_error(f"{description} - Failed with return code {result.returncode}")
            if result.stderr:
                print(f"🔥 Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        log_error(f"{description} - Timed out after 120 seconds")
        return False
    except Exception as e:
        log_error(f"{description} - Exception: {e}")
        return False

def setup_sample_data() -> Path:
    """Set up sample data for the demo."""
    demo_dir = PROJECT_ROOT / "demo-output"
    sample_data_dir = PROJECT_ROOT / "sample-demo-data"

    # Clean up previous demo
    if demo_dir.exists():
        import shutil
        shutil.rmtree(demo_dir)

    demo_dir.mkdir(exist_ok=True)
    sample_data_dir.mkdir(exist_ok=True)

    # Copy sample data to demo input
    log_info("Setting up sample data...")

    # Copy sample Figma data
    figma_input = sample_data_dir / "figma-data"
    figma_input.mkdir(exist_ok=True)

    import shutil
    shutil.copy2(
        PROJECT_ROOT / "rag-test-input" / "sample-figma-data.json",
        figma_input / "figma-data.json"
    )

    # Copy sample test scenarios
    test_scenarios_input = sample_data_dir / "test-scenarios"
    test_scenarios_input.mkdir(exist_ok=True)

    for scenario_file in (PROJECT_ROOT / "v2" / "sample-test-scenarios").glob("*.md"):
        shutil.copy2(scenario_file, test_scenarios_input / scenario_file.name)

    log_success("Sample data setup complete")
    return demo_dir

# =============================================================================
# PROJECT MANAGEMENT FUNCTIONS
# =============================================================================

def create_project(project_name: str) -> bool:
    """Create a new project with directory structure and .env file."""
    project_dir = PROJECT_ROOT / "projects" / project_name

    if project_dir.exists():
        log_error(f"Project '{project_name}' already exists at {project_dir}")
        return False

    # Create project directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "input").mkdir(exist_ok=True)
    (project_dir / "input" / "test-scenarios").mkdir(exist_ok=True)
    (project_dir / "code").mkdir(exist_ok=True)
    (project_dir / "output").mkdir(exist_ok=True)

    # Create .env file template
    env_file = project_dir / ".env"
    with open(env_file, 'w') as f:
        f.write("# Figma API Credentials\n")
        f.write("FIGMA_TOKEN=your_figma_token_here\n")
        f.write(f"FIGMA_FILE_ID={project_name}\n")
        f.write("\n# Project Configuration\n")
        f.write(f"PROJECT_NAME={project_name}\n")

    # Create project metadata
    project_metadata = {
        "project_id": project_name,
        "name": project_name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": "1.0.0",
        "pipeline": {
            "status": "created",
            "last_run": None,
            "steps_completed": 0
        }
    }

    with open(project_dir / "project.json", 'w') as f:
        json.dump(project_metadata, f, indent=2)

    log_success(f"Project '{project_name}' created successfully!")
    log_info(f"Project directory: {project_dir}")
    log_info(f"Add your Figma credentials to: {env_file}")
    log_info(f"Copy your Figma JSON to: {project_dir / 'input' / 'figma-data.json'}")

    return True

def list_projects() -> List[Dict]:
    """List all available projects."""
    projects_dir = PROJECT_ROOT / "projects"
    if not projects_dir.exists():
        return []

    projects = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            project_file = project_dir / "project.json"
            if project_file.exists():
                try:
                    with open(project_file) as f:
                        project_data = json.load(f)
                    projects.append(project_data)
                except:
                    # Fallback for projects without metadata
                    projects.append({
                        "project_id": project_dir.name,
                        "name": project_dir.name,
                        "status": "unknown"
                    })

    return projects

def delete_project(project_name: str) -> bool:
    """Delete a project directory."""
    project_dir = PROJECT_ROOT / "projects" / project_name

    if not project_dir.exists():
        log_error(f"Project '{project_name}' not found")
        return False

    try:
        response = input(f"⚠️  Are you sure you want to delete project '{project_name}'? (y/n): ").lower()
        if response not in ['y', 'yes']:
            log_info("Project deletion cancelled")
            return False

        shutil.rmtree(project_dir)
        log_success(f"Project '{project_name}' deleted successfully")
        return True
    except Exception as e:
        log_error(f"Failed to delete project: {e}")
        return False

def setup_project_data(project_name: str) -> Path:
    """Set up project data for pipeline execution."""
    project_dir = PROJECT_ROOT / "projects" / project_name

    if not project_dir.exists():
        log_error(f"Project '{project_name}' not found. Use --create-project {project_name} first.")
        return None

    # Check for Figma data
    figma_file = project_dir / "input" / "figma-data.json"
    if not figma_file.exists():
        log_error(f"Figma data file not found: {figma_file}")
        log_info(f"Please copy your Figma JSON to: {figma_file}")
        return None

    # Copy sample test scenarios if test-scenarios directory is empty
    test_scenarios_dir = project_dir / "input" / "test-scenarios"
    if not any(test_scenarios_dir.iterdir()):
        log_info("Copying sample test scenarios...")
        sample_scenarios_dir = PROJECT_ROOT / "v2" / "sample-test-scenarios"
        if sample_scenarios_dir.exists():
            for scenario_file in sample_scenarios_dir.glob("*.md"):
                shutil.copy2(scenario_file, test_scenarios_dir / scenario_file.name)

    log_success(f"Project '{project_name}' data ready for pipeline execution")
    return project_dir

def update_project_status(project_name: str, status: str, steps_completed: int = 0) -> None:
    """Update project metadata with pipeline status."""
    project_dir = PROJECT_ROOT / "projects" / project_name
    project_file = project_dir / "project.json"

    if project_file.exists():
        try:
            with open(project_file) as f:
                project_data = json.load(f)

            project_data["pipeline"]["status"] = status
            project_data["pipeline"]["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            project_data["pipeline"]["steps_completed"] = steps_completed

            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            log_info(f"Warning: Could not update project status: {e}")

def run_step_1_figma_analyzer(input_dir: Path, output_dir: Path) -> bool:
    """Run Step 1: figma-analyzer"""
    log_step(1, "figma-analyzer", "Extract design assets from Figma data")

    figma_file = input_dir / "figma-data.json"
    if not figma_file.exists():
        log_error(f"Figma data file not found: {figma_file}")
        return False

    return run_command([
        "python3", "v2/figma-analyzer/main.py",
        str(figma_file),
        str(output_dir / "step1-figma-analyzer")
    ], "Figma Analysis")

def run_step_2_prototype_analyzer(input_dir: Path, output_dir: Path) -> bool:
    """Run Step 2: prototype-analyzer"""
    log_step(2, "prototype-analyzer", "Analyze user interactions and flows")

    return run_command([
        "python3", "v2/prototype-analyzer/main.py",
        "--catalog", str(output_dir / "step1-figma-analyzer" / "component-catalog.json"),
        "--screens", str(output_dir / "step1-figma-analyzer" / "screen-set.json"),
        "--output", str(output_dir / "step2-prototype-analyzer")
    ], "Prototype Analysis")

def run_step_3_token_converter(input_dir: Path, output_dir: Path) -> bool:
    """Run Step 3: token-converter"""
    log_step(3, "token-converter", "Convert design tokens to framework formats")

    design_tokens = output_dir / "step1-figma-analyzer" / "design-tokens.json"
    if not design_tokens.exists():
        log_error(f"Design tokens not found: {design_tokens}")
        return False

    return run_command([
        "python3", "v2/token-converter/main.py",
        "--tokens", str(design_tokens),
        "--output", str(output_dir / "step3-token-converter"),
        "--framework", "tailwind"
    ], "Token Conversion")

def run_step_4_component_generator(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 4: component-generator"""
    log_step(4, "component-generator", "Generate React components")

    component_catalog = output_dir / "step1-figma-analyzer" / "component-catalog.json"
    design_tokens = output_dir / "step3-token-converter" / "design-tokens.json"

    if not component_catalog.exists():
        log_error(f"Component catalog not found: {component_catalog}")
        return False

    # Create components directory in code folder
    components_dir = code_dir / "components"
    components_dir.mkdir(exist_ok=True)

    return run_command([
        "python3", "v2/component-generator/main.py",
        "--catalog", str(component_catalog),
        "--tokens", str(design_tokens),
        "--output", str(components_dir),
        "--library", "shadcn"
    ], "Component Generation")

def run_step_5_page_generator(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 5: page-generator"""
    log_step(5, "page-generator", "Create page implementations")

    screen_specs_dir = output_dir / "step1-figma-analyzer" / "screen-specs"
    components_dir = code_dir / "components"

    if not screen_specs_dir.exists():
        log_error(f"Screen specifications not found: {screen_specs_dir}")
        return False

    # Create pages directory in code folder
    pages_dir = code_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    return run_command([
        "python3", "v2/page-generator/main.py",
        "--screens", str(screen_specs_dir),
        "--components", str(components_dir),
        "--output", str(pages_dir)
    ], "Page Generation")

def run_step_6_test_generator(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 6: test-generator"""
    log_step(6, "test-generator", "Generate Playwright test suites")

    test_scenarios = input_dir / "test-scenarios"
    components_dir = code_dir / "components"

    if not test_scenarios.exists():
        log_error(f"Test scenarios not found: {test_scenarios}")
        return False

    # Create tests directory in code folder
    tests_dir = code_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    return run_command([
        "python3", "v2/test-generator/main.py",
        "--scenarios", str(test_scenarios),
        "--components", str(output_dir / "step1-figma-analyzer" / "component-catalog.json"),
        "--output", str(tests_dir)
    ], "Test Generation")

def run_step_7_test_runner(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 7: test-runner"""
    log_step(7, "test-runner", "Execute tests and provide demo")

    tests_dir = code_dir / "tests"

    if not tests_dir.exists():
        log_error(f"Tests not found: {tests_dir}")
        return False

    return run_command([
        "python3", "v2/test-runner/main.py",
        "--tests", str(tests_dir),
        "--output", str(output_dir / "step7-test-runner"),
        "--mode", "simulation",
        "--generate-demo"
    ], "Test Execution and Demo Generation")

def run_step_8_rag_system(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 8: rag-system"""
    log_step(8, "rag-system", "Create RAG knowledge bases")

    # Collect all outputs from previous steps
    rag_input_dirs = [
        output_dir / "step1-figma-analyzer",
        output_dir / "step3-token-converter",
        code_dir / "components",
        code_dir / "pages",
        code_dir / "tests"
    ]

    return run_command([
        "python3", "v2/rag-system/main.py",
        "--input-dirs", *[str(d) for d in rag_input_dirs if d.exists()],
        "--output", str(output_dir / "step8-rag-system")
    ], "RAG Knowledge Base Creation")

def run_step_9_ai_assistant(input_dir: Path, output_dir: Path, code_dir: Path) -> bool:
    """Run Step 9: ai-assistant"""
    log_step(9, "ai-assistant", "AI-powered code analysis and review")

    rag_bases = output_dir / "step8-rag-system" / "rag-bases"
    code_dirs = [
        code_dir / "components",
        code_dir / "pages",
        code_dir / "tests"
    ]

    if not rag_bases.exists():
        log_error(f"RAG bases not found: {rag_bases}")
        return False

    return run_command([
        "python3", "v2/ai-assistant/main.py",
        "--rag-bases", str(rag_bases),
        "--code-dirs", *[str(d) for d in code_dirs if d.exists()],
        "--output", str(output_dir / "step9-ai-assistant")
    ], "AI Analysis")

def setup_demo_server(demo_dir: Path) -> bool:
    """Set up and start the demo server."""
    log_step(10, "Demo Server", "Start interactive demo server")

    demo_app_dir = demo_dir / "step7-test-runner" / "demo"
    if not demo_app_dir.exists():
        log_error(f"Demo app not found: {demo_app_dir}")
        return False

    # Install dependencies if needed
    if not (demo_app_dir / "node_modules").exists():
        log_info("Installing demo dependencies...")
        if not run_command(["npm", "install"], "Install npm dependencies", cwd=demo_app_dir):
            return False

    return True

def show_results(demo_dir: Path, port: int = 3000):
    """Show the generated results and open browser."""
    log_info("🎉 Pipeline execution completed! Showing results...")

    print(f"\n{'='*80}")
    print("📊 PIPELINE RESULTS SUMMARY")
    print(f"{'='*80}")

    # Show directory structure
    for step_dir in sorted(demo_dir.glob("step*")):
        if step_dir.is_dir():
            file_count = len(list(step_dir.rglob("*")))
            print(f"📁 {step_dir.name}: {file_count} files generated")

    # Show generated components
    components_dir = demo_dir / "step4-component-generator" / "components"
    if components_dir.exists():
        print(f"\n🎨 Generated Components:")
        for component in sorted(components_dir.glob("*.tsx")):
            print(f"  • {component.name}")

    # Show generated pages
    pages_dir = demo_dir / "step5-page-generator" / "pages"
    if pages_dir.exists():
        print(f"\n📄 Generated Pages:")
        for page in sorted(pages_dir.glob("*.tsx")):
            print(f"  • {page.name}")

    # Show AI analysis results
    ai_analysis_file = demo_dir / "step9-ai-assistant" / "ai-review" / "analysis.json"
    if ai_analysis_file.exists():
        try:
            with open(ai_analysis_file) as f:
                analysis = json.load(f)
            metrics = analysis.get("metrics", {})
            print(f"\n🤖 AI Analysis Results:")
            print(f"  • Overall Quality Score: {metrics.get('overall_score', 'N/A')}/100")
            print(f"  • Issues Found: {len(analysis.get('issues', []))}")
            print(f"  • Files Analyzed: {analysis.get('summary', {}).get('files_analyzed', 'N/A')}")
        except Exception as e:
            print(f"\n🤖 AI Analysis: Unable to load results ({e})")

    # Show demo server info
    demo_app_dir = demo_dir / "step7-test-runner" / "demo"
    if demo_app_dir.exists():
        print(f"\n🌐 Demo Application:")
        print(f"  • Demo files location: {demo_app_dir}")
        print(f"  • To start demo server:")
        print(f"    cd {demo_app_dir}")
        print(f"    npm start")
        print(f"    Then open http://localhost:{port} in your browser")

        # Ask if user wants to start the server
        try:
            response = input("\n🚀 Do you want to start the demo server? (y/n): ").lower()
            if response in ['y', 'yes']:
                print(f"🚀 Starting demo server on port {port}...")
                print(f"📝 In a new terminal, run:")
                print(f"    cd {demo_app_dir}")
                print(f"    npm start")
                print(f"🌐 Then open http://localhost:{port} in your browser")

                # Try to open browser after a delay
                time.sleep(2)
                try:
                    webbrowser.open(f"http://localhost:{port}")
                    print(f"🌐 Opening http://localhost:{port} in your browser...")
                except:
                    print(f"💡 Please manually open http://localhost:{port} in your browser")
        except KeyboardInterrupt:
            print("\n👋 Demo setup complete. Run the commands above to start the server.")

def show_generated_code_samples(demo_dir: Path):
    """Display samples of generated code."""
    print(f"\n{'='*80}")
    print("💻 GENERATED CODE SAMPLES")
    print(f"{'='*80}")

    # Show sample component
    sample_component = demo_dir / "step4-component-generator" / "components" / "Button.tsx"
    if sample_component.exists():
        print(f"\n🎨 Sample Component ({sample_component.name}):")
        print("-" * 60)
        with open(sample_component) as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
                print(f"{i:3d}: {line.rstrip()}")
            if len(lines) > 30:
                print(f"... ({len(lines) - 30} more lines)")

    # Show sample page
    sample_page = demo_dir / "step5-page-generator" / "pages" / "HomePage.tsx"
    if sample_page.exists():
        print(f"\n📄 Sample Page ({sample_page.name}):")
        print("-" * 60)
        with open(sample_page) as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
                print(f"{i:3d}: {line.rstrip()}")
            if len(lines) > 30:
                print(f"... ({len(lines) - 30} more lines)")

    # Show sample test
    sample_test = demo_dir / "step6-test-generator" / "tests" / "user-authentication.spec.ts"
    if sample_test.exists():
        print(f"\n🧪 Sample Test ({sample_test.name}):")
        print("-" * 60)
        with open(sample_test) as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
                print(f"{i:3d}: {line.rstrip()}")
            if len(lines) > 30:
                print(f"... ({len(lines) - 30} more lines)")

def run_project_pipeline(project_name: str, demo: bool = False, port: int = 3000, skip_to: int = None) -> bool:
    """Run the complete pipeline for a specific project."""
    project_dir = setup_project_data(project_name)
    if not project_dir:
        return False

    input_dir = project_dir / "input"
    output_dir = project_dir / "output"
    code_dir = project_dir / "code"

    print(f"\n🚀 Starting pipeline for project: {project_name}")
    print(f"📁 Project directory: {project_dir}")

    # Run pipeline steps
    steps = [
        (run_step_1_figma_analyzer, "Figma Analysis", [input_dir, output_dir]),
        (run_step_2_prototype_analyzer, "Prototype Analysis", [input_dir, output_dir]),
        (run_step_3_token_converter, "Token Conversion", [input_dir, output_dir]),
        (run_step_4_component_generator, "Component Generation", [input_dir, output_dir, code_dir]),
        (run_step_5_page_generator, "Page Generation", [input_dir, output_dir, code_dir]),
        (run_step_6_test_generator, "Test Generation", [input_dir, output_dir, code_dir]),
        (run_step_7_test_runner, "Test Execution", [input_dir, output_dir, code_dir]),
        (run_step_8_rag_system, "RAG System", [input_dir, output_dir, code_dir]),
        (run_step_9_ai_assistant, "AI Analysis", [input_dir, output_dir, code_dir])
    ]

    start_step = (skip_to - 1) if skip_to else 0

    for i, (step_func, step_name, step_args) in enumerate(steps[start_step:], start=start_step + 1):
        print(f"\n{'='*80}")
        print(f"🔄 Executing Step {i}: {step_name}")
        print(f"{'='*80}")

        if not step_func(*step_args):
            print(f"\n❌ Step {i} failed. Stopping pipeline.")
            print("💡 Check the error messages above for details.")
            update_project_status(project_name, f"failed_at_step_{i}", i - 1)
            return False

        print(f"✅ Step {i} completed successfully!")
        update_project_status(project_name, f"completed_step_{i}", i)

    # Update project status
    update_project_status(project_name, "completed", 9)

    # Show results
    show_project_results(project_name, code_dir, output_dir, port, demo)

    return True

def show_project_results(project_name: str, code_dir: Path, output_dir: Path, port: int, demo: bool = False):
    """Show the generated results for a project."""
    log_info(f"🎉 Pipeline execution completed for project: {project_name}!")

    print(f"\n{'='*80}")
    print(f"📊 PROJECT {project_name.upper()} RESULTS SUMMARY")
    print(f"{'='*80}")

    # Show generated code structure
    print(f"\n🎨 Generated Code Structure:")
    for item in code_dir.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(code_dir)
            print(f"  📄 {relative_path}")

    # Show pipeline outputs
    print(f"\n🔧 Pipeline Outputs:")
    for step_dir in sorted(output_dir.glob("step*")):
        if step_dir.is_dir():
            file_count = len(list(step_dir.rglob("*")))
            print(f"  📁 {step_dir.name}: {file_count} files generated")

    # Show AI analysis results
    ai_analysis_file = output_dir / "step9-ai-assistant" / "ai-review" / "analysis.json"
    if ai_analysis_file.exists():
        try:
            with open(ai_analysis_file) as f:
                analysis = json.load(f)
            metrics = analysis.get("metrics", {})
            print(f"\n🤖 AI Analysis Results:")
            print(f"  • Overall Quality Score: {metrics.get('overall_score', 'N/A')}/100")
            print(f"  • Issues Found: {len(analysis.get('issues', []))}")
            print(f"  • Files Analyzed: {analysis.get('summary', {}).get('files_analyzed', 'N/A')}")
        except Exception as e:
            print(f"\n🤖 AI Analysis: Unable to load results ({e})")

    # Demo setup
    if demo:
        setup_project_demo(project_name, code_dir, port)

def setup_project_demo(project_name: str, code_dir: Path, port: int):
    """Set up demo for the generated project code."""
    log_info(f"🚀 Setting up demo for project: {project_name}")

    # Create a simple demo for the generated components
    demo_dir = code_dir / "demo"
    demo_dir.mkdir(exist_ok=True)

    # Create a simple demo React app
    demo_app_dir = code_dir / "demo-app"
    create_simple_demo_app(demo_app_dir, code_dir)

    print(f"\n🌐 Demo Information:")
    print(f"  • Generated code location: {code_dir}")
    print(f"  • Demo app location: {demo_app_dir}")
    print(f"  • To run demo:")
    print(f"    cd {demo_app_dir}")
    print(f"    npm install")
    print(f"    npm start")
    print(f"  • Then open http://localhost:{port} in your browser")

def create_simple_demo_app(demo_dir: Path, code_dir: Path):
    """Create a simple demo React app for the generated components."""
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Basic package.json
    package_json = {
        "name": "generated-components-demo",
        "version": "1.0.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test"
        }
    }

    with open(demo_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)

    # Create src directory
    src_dir = demo_dir / "src"
    src_dir.mkdir(exist_ok=True)

    # Simple App.js that shows generated components
    app_js = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 Generated Components Demo</h1>
        <p>Components generated from Figma design</p>
      </header>

      <main className="container">
        <div className="component-showcase">
          <h2>Generated Components</h2>
          <p>These components were automatically generated from your Figma design.</p>

          <div className="component-info">
            <h3>Code Location</h3>
            <p>Generated components are available at: {code_dir}</p>

            <h3>Available Components</h3>
            <ul>
              <li>React Components (components/)</li>
              <li>Pages (pages/)</li>
              <li>Tests (tests/)</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}}

export default App;
"""

    with open(src_dir / "App.js", "w") as f:
        f.write(app_js)

    # Create basic CSS
    app_css = """.App {
  text-align: center;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
}

.App-header h1 {
  margin: 0;
  font-size: 2.5rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.component-showcase {
  text-align: left;
}

.component-info {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  margin-top: 2rem;
}

.component-info h3 {
  color: #333;
  margin-top: 1.5rem;
}

.component-info ul {
  list-style: none;
  padding: 0;
}

.component-info li {
  background: #e9ecef;
  margin: 0.5rem 0;
  padding: 0.75rem;
  border-radius: 4px;
  font-family: monospace;
}
"""

    with open(src_dir / "App.css", "w") as f:
        f.write(app_css)

    # Create index.js
    index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

    with open(src_dir / "index.js", "w") as f:
        f.write(index_js)

    # Create public directory with index.html
    public_dir = demo_dir / "public"
    public_dir.mkdir(exist_ok=True)

    index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Generated Components Demo</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
"""

    with open(public_dir / "index.html", "w") as f:
        f.write(index_html)

def main():
    """Main demo function with project support."""
    parser = argparse.ArgumentParser(description="SimFlo Figma-to-RAG Pipeline Demo")

    # Project management arguments
    parser.add_argument("--create-project", type=str, help="Create a new project")
    parser.add_argument("--project", type=str, help="Run pipeline for specific project")
    parser.add_argument("--list", action="store_true", help="List all projects")
    parser.add_argument("--delete", type=str, help="Delete a project")

    # Demo arguments
    parser.add_argument("--demo", action="store_true", help="Start demo after pipeline")
    parser.add_argument("--demo-only", action="store_true", help="Start demo only (skip pipeline)")
    parser.add_argument("--port", type=int, default=3000, help="Demo server port")
    parser.add_argument("--skip-to", type=int, help="Skip to specific step (1-9)")

    args = parser.parse_args()

    # Handle list projects
    if args.list:
        projects = list_projects()
        if not projects:
            print("📝 No projects found. Use --create-project <name> to create one.")
            return

        print("📋 Available Projects:")
        print("=" * 60)
        for project in projects:
            status = project.get("pipeline", {}).get("status", "unknown")
            last_run = project.get("pipeline", {}).get("last_run", "never")
            print(f"  • {project['name']}")
            print(f"    Status: {status}")
            print(f"    Last run: {last_run}")
            print()
        return

    # Handle delete project
    if args.delete:
        delete_project(args.delete)
        return

    # Handle create project
    if args.create_project:
        if create_project(args.create_project):
            print(f"\n✅ Project '{args.create_project}' created successfully!")
            print(f"📝 Next steps:")
            print(f"  1. Add your Figma credentials to: projects/{args.create_project}/.env")
            print(f"  2. Copy your Figma JSON to: projects/{args.create_project}/input/figma-data.json")
            print(f"  3. Run pipeline: python3 run-pipeline-demo.py --project {args.create_project}")
        return

    # Handle project pipeline
    if args.project:
        if args.demo_only:
            project_dir = PROJECT_ROOT / "projects" / args.project
            if not project_dir.exists():
                log_error(f"Project '{args.project}' not found")
                return

            code_dir = project_dir / "code"
            setup_project_demo(args.project, code_dir, args.port)
            return

        success = run_project_pipeline(args.project, args.demo, args.port, args.skip_to)
        if success:
            print(f"\n🎉 Project '{args.project}' pipeline completed successfully!")
        else:
            print(f"\n❌ Project '{args.project}' pipeline failed!")
        return

    # Default: show help
    parser.print_help()
    print("\n🚀 Quick Start:")
    print("  1. python3 run-pipeline-demo.py --create-project my-project")
    print("  2. # Add Figma JSON to projects/my-project/input/figma-data.json")
    print("  3. python3 run-pipeline-demo.py --project my-project --demo")

  
if __name__ == "__main__":
    main()