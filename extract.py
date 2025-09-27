#!/usr/bin/env python3
"""
SimFlo MCP RAG - Simple Extraction Wrapper

Convenient wrapper for running data pipeline extractions from project root.
"""

import sys
import os
from pathlib import Path

# Add data-pipeline to path
pipeline_dir = Path(__file__).parent / "data-pipeline"
sys.path.insert(0, str(pipeline_dir))

# Change to pipeline directory for config access
os.chdir(pipeline_dir)

# Import and run orchestrator
from orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    import sys
    sys.argv = ['orchestrator'] + sys.argv[1:]  # Pretend to be orchestrator script
    from orchestrator import main
    main()