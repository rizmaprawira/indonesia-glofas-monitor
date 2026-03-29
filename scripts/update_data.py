#!/usr/bin/env python3
"""
Main update script that orchestrates the full data pipeline.
Fetches latest GloFAS data and processes it for the frontend.
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).parent


def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    script_path = SCRIPTS_DIR / script_name
    logger.info(f"Running {script_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=SCRIPTS_DIR,
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"{script_name} failed with exit code {result.returncode}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to run {script_name}: {e}")
        return False


def main():
    """Run the full update pipeline."""
    logger.info("=" * 60)
    logger.info("Starting GloFAS data update pipeline")
    logger.info("=" * 60)
    
    # Step 1: Fetch data
    if not run_script("fetch_glofas.py"):
        logger.error("Fetch step failed. Aborting.")
        sys.exit(1)
    
    # Step 2: Process data
    if not run_script("process_glofas.py"):
        logger.error("Processing step failed. Aborting.")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Update pipeline completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
