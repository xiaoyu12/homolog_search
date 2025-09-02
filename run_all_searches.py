#!/usr/bin/env python3
"""
Run homolog searches for all settings files.
"""

import os
import subprocess
import glob
from pathlib import Path

def run_homolog_search(settings_file):
    """Run homolog search for a single settings file."""
    print(f"\n{'='*80}")
    print(f"Running homolog search for: {settings_file}")
    print(f"{'='*80}")
    
    try:
        # Run the homolog search
        result = subprocess.run([
            'python', 'homolog_search.py', 
            '--settings', settings_file
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {settings_file}")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Last 500 chars
        else:
            print(f"✗ FAILED: {settings_file}")
            print("Error:", result.stderr[-500:] if result.stderr else "Unknown error")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {settings_file} (took longer than 1 hour)")
        return False
    except Exception as e:
        print(f"💥 ERROR: {settings_file} - {str(e)}")
        return False

def main():
    """Main function to run all homolog searches."""
    
    # Get all settings files
    config_dir = Path("config")
    settings_files = list(config_dir.glob("*_settings.yaml"))
    
    print(f"Found {len(settings_files)} settings files to process")
    print("Starting homolog searches...")
    
    # Track results
    successful = 0
    failed = 0
    
    # Run searches
    for i, settings_file in enumerate(settings_files, 1):
        print(f"\n[{i}/{len(settings_files)}] Processing {settings_file.name}")
        
        success = run_homolog_search(str(settings_file))
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Small delay between runs to avoid overwhelming the system
        import time
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total settings files: {len(settings_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/len(settings_files)*100:.1f}%")
    
    if failed > 0:
        print(f"\nFailed files:")
        for settings_file in settings_files:
            if not run_homolog_search(str(settings_file)):
                print(f"  - {settings_file.name}")

if __name__ == "__main__":
    main()
