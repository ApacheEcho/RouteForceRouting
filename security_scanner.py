#!/usr/bin/env python3
"""
Comprehensive Security Scanner for RouteForce Routing

This script runs all CodeQL security queries and generates a security report.
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_step(step: str) -> None:
    """Print a formatted step"""
    print(f"\n🔍 {step}")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"⚠️  {message}")


def run_codeql_query(query_file: str, query_name: str) -> dict:
    """Run a CodeQL query and return results"""
    print_step(f"Running {query_name}...")
    
    try:
        # Run the query
        result = subprocess.run([
            'codeql', 'query', 'run', 
            f'codeql-custom-queries-python/{query_file}',
            '--database=codeql-database'
        ], capture_output=True, text=True, check=True)
        
        # Parse output to count results
        output_lines = result.stdout.strip().split('\n')
        result_lines = [line for line in output_lines if line.startswith('|') and 'call' not in line and '---' not in line]
        
        # Remove empty result lines
        actual_results = [line for line in result_lines if line.strip() != '| call | col1 |' and '------' not in line]
        
        vulnerability_count = len([line for line in actual_results if line.strip() and '|' in line and line.count('|') >= 2])
        
        return {
            'query': query_name,
            'file': query_file,
            'status': 'success',
            'vulnerabilities_found': vulnerability_count,
            'details': actual_results if vulnerability_count > 0 else [],
            'execution_time': 'N/A'  # CodeQL doesn't provide easy access to this
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'query': query_name,
            'file': query_file,
            'status': 'error',
            'error': str(e),
            'vulnerabilities_found': 0,
            'details': []
        }


def generate_security_report(results: list) -> None:
    """Generate a comprehensive security report"""
    print_header("🔒 SECURITY SCAN REPORT")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_vulnerabilities = sum(r['vulnerabilities_found'] for r in results)
    
    print(f"📅 Scan Date: {timestamp}")
    print(f"📁 Project: RouteForce Routing")
    print(f"🎯 Total Queries Run: {len(results)}")
    print(f"🚨 Total Vulnerabilities Found: {total_vulnerabilities}")
    
    print(f"\n{'─'*60}")
    print("📊 DETAILED RESULTS")
    print(f"{'─'*60}")
    
    for result in results:
        status_icon = "✅" if result['vulnerabilities_found'] == 0 else "🚨"
        print(f"{status_icon} {result['query']}: {result['vulnerabilities_found']} vulnerabilities")
        
        if result['vulnerabilities_found'] > 0:
            for detail in result['details'][:3]:  # Show first 3 details
                print(f"    • {detail.strip()}")
            if len(result['details']) > 3:
                print(f"    • ... and {len(result['details']) - 3} more")
    
    # Overall security assessment
    print(f"\n{'─'*60}")
    print("🏆 SECURITY ASSESSMENT")
    print(f"{'─'*60}")
    
    if total_vulnerabilities == 0:
        print("🎉 EXCELLENT: No security vulnerabilities detected!")
        print("   Your RouteForce Routing application appears to follow")
        print("   secure coding practices.")
    elif total_vulnerabilities <= 5:
        print("🟡 GOOD: Few vulnerabilities found.")
        print("   Review and address the identified issues.")
    elif total_vulnerabilities <= 10:
        print("🟠 MODERATE: Several vulnerabilities found.")
        print("   Prioritize fixing these security issues.")
    else:
        print("🔴 HIGH RISK: Many vulnerabilities found.")
        print("   Immediate attention required for security fixes.")
    
    # Save detailed report to file
    save_report_to_file(results, timestamp, total_vulnerabilities)


def save_report_to_file(results: list, timestamp: str, total_vulnerabilities: int) -> None:
    """Save detailed report to JSON file"""
    report_data = {
        'scan_timestamp': timestamp,
        'project': 'RouteForce Routing',
        'total_queries': len(results),
        'total_vulnerabilities': total_vulnerabilities,
        'results': results,
        'summary': {
            'sql_injection': next((r['vulnerabilities_found'] for r in results if 'SQL' in r['query']), 0),
            'path_traversal': next((r['vulnerabilities_found'] for r in results if 'traversal' in r['query']), 0),
            'command_injection': next((r['vulnerabilities_found'] for r in results if 'Command' in r['query']), 0),
            'xss': next((r['vulnerabilities_found'] for r in results if 'XSS' in r['query']), 0)
        }
    }
    
    # Ensure results directory exists
    os.makedirs('codeql-results', exist_ok=True)
    
    # Save JSON report
    report_file = f"codeql-results/security-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Main security scanning function"""
    print_header("🛡️  RouteForce Routing Security Scanner")
    print("This tool scans your codebase for common security vulnerabilities.")
    
    # Change to project directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Check if CodeQL database exists
    if not os.path.exists('codeql-database'):
        print_warning("CodeQL database not found!")
        print("   Run: codeql database create --language=python --source-root=. codeql-database")
        return
    
    # Define security queries to run
    queries = [
        ('example.ql', 'SQL Injection Detection'),
        ('path-traversal.ql', 'Path Traversal Detection'),
        ('command-injection.ql', 'Command Injection Detection'),
        ('xss.ql', 'Cross-Site Scripting (XSS) Detection')
    ]
    
    # Run all queries
    results = []
    for query_file, query_name in queries:
        if os.path.exists(f'codeql-custom-queries-python/{query_file}'):
            result = run_codeql_query(query_file, query_name)
            results.append(result)
            
            if result['status'] == 'success':
                if result['vulnerabilities_found'] == 0:
                    print_success(f"No {query_name.lower()} vulnerabilities found")
                else:
                    print_warning(f"Found {result['vulnerabilities_found']} potential {query_name.lower()} issues")
            else:
                print_warning(f"Error running {query_name}: {result.get('error', 'Unknown error')}")
        else:
            print_warning(f"Query file not found: {query_file}")
    
    # Generate comprehensive report
    if results:
        generate_security_report(results)
    else:
        print_warning("No queries were executed successfully")
    
    print(f"\n🎯 Security scan complete!")


if __name__ == "__main__":
    main()
