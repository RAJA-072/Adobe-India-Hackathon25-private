#!/usr/bin/env python3
"""
Validation script for the Adobe Hackathon PDF Processing Solution
Validates output against expected schema and performance requirements
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any

def validate_json_schema(data: Dict[str, Any]) -> bool:
    """Validate JSON output against required schema."""
    # Check required top-level fields
    if not isinstance(data, dict):
        return False
    
    if "title" not in data or "outline" not in data:
        return False
    
    # Validate title
    if not isinstance(data["title"], str):
        return False
    
    # Validate outline
    if not isinstance(data["outline"], list):
        return False
    
    # Validate each outline item
    for item in data["outline"]:
        if not isinstance(item, dict):
            return False
        
        required_fields = ["level", "text", "page"]
        for field in required_fields:
            if field not in item:
                return False
        
        # Validate field types
        if not isinstance(item["level"], str):
            return False
        if not isinstance(item["text"], str):
            return False
        if not isinstance(item["page"], int):
            return False
        
        # Validate level format
        if not item["level"].startswith("H") or not item["level"][1:].isdigit():
            return False
        
        level_num = int(item["level"][1:])
        if level_num < 1 or level_num > 6:
            return False
    
    return True

def validate_output_directory(output_dir: Path) -> Dict[str, Any]:
    """Validate all JSON files in output directory."""
    results = {
        "total_files": 0,
        "valid_files": 0,
        "invalid_files": [],
        "schema_errors": []
    }
    
    json_files = list(output_dir.glob("*.json"))
    results["total_files"] = len(json_files)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if validate_json_schema(data):
                results["valid_files"] += 1
                print(f"✅ {json_file.name}: Valid")
            else:
                results["invalid_files"].append(json_file.name)
                results["schema_errors"].append(f"{json_file.name}: Schema validation failed")
                print(f"❌ {json_file.name}: Invalid schema")
                
        except json.JSONDecodeError as e:
            results["invalid_files"].append(json_file.name)
            results["schema_errors"].append(f"{json_file.name}: JSON decode error - {e}")
            print(f"❌ {json_file.name}: JSON decode error")
        except Exception as e:
            results["invalid_files"].append(json_file.name)
            results["schema_errors"].append(f"{json_file.name}: Unexpected error - {e}")
            print(f"❌ {json_file.name}: Unexpected error")
    
    return results

def run_performance_test(docker_image: str, input_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """Run performance test and validate results."""
    print("🚀 Running Performance Test...")
    
    # Clean output directory
    if output_dir.exists():
        for file in output_dir.glob("*.json"):
            file.unlink()
    output_dir.mkdir(exist_ok=True)
    
    # Run Docker container and time execution
    start_time = time.time()
    
    cmd = f'docker run --rm -v "{input_dir.absolute()}:/app/input:ro" -v "{output_dir.absolute()}:/app/output" --network none {docker_image}'
    exit_code = os.system(cmd)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Validate results
    validation_results = validate_output_directory(output_dir)
    
    # Count input PDFs
    input_pdfs = len(list(input_dir.glob("*.pdf")))
    
    performance_results = {
        "execution_time": execution_time,
        "input_pdfs": input_pdfs,
        "exit_code": exit_code,
        "success": exit_code == 0,
        "avg_time_per_pdf": execution_time / max(input_pdfs, 1),
        "meets_time_requirement": execution_time <= 10.0,  # 10 second requirement
        **validation_results
    }
    
    return performance_results

def print_summary(results: Dict[str, Any]):
    """Print test summary."""
    print("\n" + "="*60)
    print("🏆 ADOBE HACKATHON PDF PROCESSOR - VALIDATION REPORT")
    print("="*60)
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   ⏱️  Execution Time: {results['execution_time']:.2f} seconds")
    print(f"   📄 PDFs Processed: {results['input_pdfs']}")
    print(f"   ⚡ Avg Time/PDF: {results['avg_time_per_pdf']:.2f} seconds")
    print(f"   🎯 Meets Requirement (<10s): {'✅ YES' if results['meets_time_requirement'] else '❌ NO'}")
    
    print(f"\n📋 VALIDATION RESULTS:")
    print(f"   📁 Total Output Files: {results['total_files']}")
    print(f"   ✅ Valid Files: {results['valid_files']}")
    print(f"   ❌ Invalid Files: {len(results['invalid_files'])}")
    print(f"   📊 Success Rate: {(results['valid_files']/max(results['total_files'], 1)*100):.1f}%")
    
    if results['invalid_files']:
        print(f"\n❌ ERRORS FOUND:")
        for error in results['schema_errors']:
            print(f"   • {error}")
    
    print(f"\n🏁 OVERALL RESULT:")
    if (results['success'] and 
        results['meets_time_requirement'] and 
        results['valid_files'] == results['total_files'] and 
        results['total_files'] > 0):
        print("   🏆 ALL TESTS PASSED - READY FOR HACKATHON SUBMISSION!")
    else:
        print("   ⚠️  Some issues found - please review and fix")
    
    print("="*60)

if __name__ == "__main__":
    # Configuration
    DOCKER_IMAGE = "pdf-processor-hackathon"
    INPUT_DIR = Path("sample_dataset/pdfs")
    OUTPUT_DIR = Path("validation_output")
    
    print("🧪 Adobe Hackathon PDF Processor Validation")
    print("🎯 Testing performance and output validation...")
    
    # Run comprehensive test
    results = run_performance_test(DOCKER_IMAGE, INPUT_DIR, OUTPUT_DIR)
    
    # Print results
    print_summary(results)
