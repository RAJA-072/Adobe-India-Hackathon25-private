#!/usr/bin/env python3
"""
Validation script for Challenge 1b - Multi-Collection PDF Analysis
Validates output quality and persona-based analysis effectiveness
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import time

def validate_output_structure(output_data: Dict[str, Any]) -> Dict[str, bool]:
    """Validate the structure of output JSON against expected format."""
    validation_results = {
        "has_metadata": False,
        "has_extracted_sections": False,
        "has_subsection_analysis": False,
        "metadata_complete": False,
        "sections_properly_ranked": False,
        "subsections_have_content": False
    }
    
    # Check top-level structure
    required_keys = ["metadata", "extracted_sections", "subsection_analysis"]
    for key in required_keys:
        if key in output_data:
            validation_results[f"has_{key}"] = True
    
    # Validate metadata
    if "metadata" in output_data:
        metadata = output_data["metadata"]
        required_metadata = ["input_documents", "persona", "job_to_be_done", "processing_timestamp"]
        if all(key in metadata for key in required_metadata):
            validation_results["metadata_complete"] = True
    
    # Validate extracted sections
    if "extracted_sections" in output_data:
        sections = output_data["extracted_sections"]
        if isinstance(sections, list) and len(sections) > 0:
            # Check if sections are properly ranked
            ranks = [section.get("importance_rank", 0) for section in sections]
            if ranks == sorted(ranks) and len(set(ranks)) == len(ranks):
                validation_results["sections_properly_ranked"] = True
    
    # Validate subsection analysis
    if "subsection_analysis" in output_data:
        subsections = output_data["subsection_analysis"]
        if isinstance(subsections, list) and len(subsections) > 0:
            # Check if all subsections have content
            has_content = all(
                "refined_text" in sub and len(sub.get("refined_text", "")) > 50
                for sub in subsections
            )
            validation_results["subsections_have_content"] = has_content
    
    return validation_results

def analyze_persona_relevance(output_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how well the output matches the persona and job requirements."""
    analysis = {
        "persona_keywords_found": 0,
        "job_keywords_found": 0,
        "relevance_score": 0.0,
        "detailed_analysis": []
    }
    
    if "metadata" not in output_data:
        return analysis
    
    persona = output_data["metadata"].get("persona", "").lower()
    job_description = output_data["metadata"].get("job_to_be_done", "").lower()
    
    # Define persona-specific keywords for validation
    persona_keywords = {
        "travel planner": ["trip", "travel", "hotel", "restaurant", "activity", "guide", "destination"],
        "hr professional": ["form", "employee", "onboarding", "compliance", "digital", "signature"],
        "food contractor": ["menu", "recipe", "vegetarian", "buffet", "dinner", "corporate", "catering"]
    }
    
    # Get relevant keywords
    relevant_keywords = []
    for key, keywords in persona_keywords.items():
        if key in persona:
            relevant_keywords = keywords
            break
    
    # Analyze subsection content
    if "subsection_analysis" in output_data:
        for subsection in output_data["subsection_analysis"]:
            content = subsection.get("refined_text", "").lower()
            
            # Count persona keywords
            persona_count = sum(1 for keyword in relevant_keywords if keyword in content)
            analysis["persona_keywords_found"] += persona_count
            
            # Count job-specific keywords
            job_words = job_description.split()
            job_count = sum(1 for word in job_words if len(word) > 3 and word in content)
            analysis["job_keywords_found"] += job_count
            
            analysis["detailed_analysis"].append({
                "document": subsection.get("document", ""),
                "persona_keywords": persona_count,
                "job_keywords": job_count,
                "content_length": len(content)
            })
    
    # Calculate overall relevance score
    total_content = len(output_data.get("subsection_analysis", []))
    if total_content > 0:
        analysis["relevance_score"] = (
            analysis["persona_keywords_found"] + analysis["job_keywords_found"]
        ) / total_content
    
    return analysis

def run_performance_test() -> Dict[str, Any]:
    """Run performance test on all collections."""
    start_time = time.time()
    
    # Run the main processing script
    result = subprocess.run(
        ["python", "process_collections.py"],
        capture_output=True,
        text=True
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return {
        "execution_time": execution_time,
        "exit_code": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }

def validate_all_collections() -> Dict[str, Any]:
    """Validate all generated collection outputs."""
    base_dir = Path(".")
    collections = ["Collection 1", "Collection 2", "Collection 3"]
    
    validation_summary = {
        "total_collections": len(collections),
        "successful_collections": 0,
        "failed_collections": [],
        "collection_results": {}
    }
    
    for collection in collections:
        collection_dir = base_dir / collection
        output_file = collection_dir / "challenge1b_output_generated.json"
        
        if not output_file.exists():
            validation_summary["failed_collections"].append(f"{collection}: Output file not found")
            continue
        
        try:
            # Load and validate output
            with open(output_file, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # Structural validation
            structure_validation = validate_output_structure(output_data)
            
            # Persona relevance analysis
            relevance_analysis = analyze_persona_relevance(output_data)
            
            # Combine results
            collection_result = {
                "structure_validation": structure_validation,
                "relevance_analysis": relevance_analysis,
                "overall_score": sum(structure_validation.values()) + relevance_analysis["relevance_score"]
            }
            
            validation_summary["collection_results"][collection] = collection_result
            
            # Check if collection passed
            if all(structure_validation.values()) and relevance_analysis["relevance_score"] > 1.0:
                validation_summary["successful_collections"] += 1
            else:
                validation_summary["failed_collections"].append(
                    f"{collection}: Quality issues detected"
                )
        
        except Exception as e:
            validation_summary["failed_collections"].append(f"{collection}: {str(e)}")
    
    return validation_summary

def print_detailed_report(performance: Dict, validation: Dict):
    """Print comprehensive validation report."""
    print("\n" + "="*80)
    print("🏆 CHALLENGE 1B - MULTI-COLLECTION PDF ANALYSIS VALIDATION REPORT")
    print("="*80)
    
    print(f"\n📊 PERFORMANCE METRICS:")
    print(f"   ⏱️  Total Execution Time: {performance['execution_time']:.2f} seconds")
    print(f"   🎯 Processing Success: {'✅ YES' if performance['success'] else '❌ NO'}")
    print(f"   📄 Collections Processed: {validation['total_collections']}")
    
    print(f"\n📋 VALIDATION RESULTS:")
    print(f"   ✅ Successful Collections: {validation['successful_collections']}")
    print(f"   ❌ Failed Collections: {len(validation['failed_collections'])}")
    print(f"   📊 Success Rate: {(validation['successful_collections']/validation['total_collections']*100):.1f}%")
    
    if validation['failed_collections']:
        print(f"\n❌ COLLECTION ISSUES:")
        for issue in validation['failed_collections']:
            print(f"   • {issue}")
    
    print(f"\n🔍 DETAILED COLLECTION ANALYSIS:")
    for collection, results in validation['collection_results'].items():
        print(f"\n   📁 {collection}:")
        structure = results['structure_validation']
        relevance = results['relevance_analysis']
        
        print(f"      📊 Structure Score: {sum(structure.values())}/6")
        print(f"      🎯 Relevance Score: {relevance['relevance_score']:.2f}")
        print(f"      🔤 Persona Keywords: {relevance['persona_keywords_found']}")
        print(f"      💼 Job Keywords: {relevance['job_keywords_found']}")
        
        # Show any structural issues
        failed_checks = [k for k, v in structure.items() if not v]
        if failed_checks:
            print(f"      ⚠️  Structure Issues: {', '.join(failed_checks)}")
    
    print(f"\n🏁 OVERALL ASSESSMENT:")
    if (performance['success'] and 
        validation['successful_collections'] == validation['total_collections']):
        print("   🏆 ALL TESTS PASSED - CHALLENGE 1B SOLUTION READY!")
        print("   🎯 Persona-based analysis working effectively")
        print("   📊 High-quality structured outputs generated")
    else:
        print("   ⚠️  Some issues detected - review and optimize")
    
    print("="*80)

def main():
    """Main validation function."""
    print("🧪 Challenge 1b Multi-Collection PDF Analysis Validation")
    print("🎯 Testing persona-based content extraction and analysis...")
    
    # Run performance test
    print("\n🚀 Running Performance Test...")
    performance_results = run_performance_test()
    
    # Validate all collections
    print("🔍 Validating Collection Outputs...")
    validation_results = validate_all_collections()
    
    # Print comprehensive report
    print_detailed_report(performance_results, validation_results)

if __name__ == "__main__":
    main()
