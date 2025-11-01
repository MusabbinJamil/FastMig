"""
Example Flask Client for Testing Evolutionary Cleaning
Use this to test the new endpoints from Python
"""

import requests
import json
from pathlib import Path

class FastMigClient:
    """Client for interacting with FastMig backend"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def upload_file(self, file_path):
        """Upload a file to the server"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(f"{self.base_url}/upload", files=files)
            return response.json()
    
    def evaluate_fitness(self):
        """Evaluate fitness of loaded data"""
        response = self.session.post(f"{self.base_url}/fitness/evaluate")
        return response.json()
    
    def get_record_fitness(self, row_index):
        """Get fitness of specific record"""
        response = self.session.get(f"{self.base_url}/fitness/record/{row_index}")
        return response.json()
    
    def clean_data(self, method="hybrid", save_result=True, parameters=None):
        """Clean data using evolutionary algorithms"""
        data = {
            "method": method,
            "save_result": save_result,
            "parameters": parameters or {}
        }
        response = self.session.post(
            f"{self.base_url}/clean/evolutionary",
            json=data
        )
        return response.json()
    
    def compare_methods(self):
        """Compare all cleaning methods"""
        response = self.session.post(f"{self.base_url}/clean/compare")
        return response.json()
    
    def export_data(self, output_path):
        """Export processed data"""
        data = {"output_path": output_path}
        response = self.session.post(f"{self.base_url}/export", json=data)
        return response.json()
    
    def restore_original(self):
        """Restore original data before cleaning"""
        response = self.session.post(f"{self.base_url}/data/restore")
        return response.json()
    
    def get_status(self):
        """Get application status"""
        response = self.session.get(f"{self.base_url}/status")
        return response.json()


def example_workflow():
    """Example workflow demonstrating the features"""
    
    client = FastMigClient()
    
    print("="*60)
    print("FastMig Evolutionary Cleaning - Example Workflow")
    print("="*60)
    
    # 1. Health check
    print("\n1. Checking server health...")
    health = client.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    
    if health.get('status') != 'healthy':
        print("   ❌ Server is not running. Start it with: python server.py")
        return
    
    # 2. Upload file
    print("\n2. Upload a file...")
    print("   Note: Create test_original_data.csv by running test_evolutionary_cleaning.py")
    
    file_path = "test_original_data.csv"
    if not Path(file_path).exists():
        print(f"   ⚠️  File '{file_path}' not found. Creating sample data...")
        # Create sample data
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)
        data = {
            'id': range(1, 51),
            'name': ['Person_' + str(i) if i % 5 != 0 else None for i in range(1, 51)],
            'age': [np.random.randint(18, 80) if i % 7 != 0 else None for i in range(1, 51)],
            'salary': [np.random.uniform(30000, 120000) if i % 6 != 0 else None for i in range(1, 51)]
        }
        pd.DataFrame(data).to_csv(file_path, index=False)
        print(f"   ✓ Created {file_path}")
    
    upload_result = client.upload_file(file_path)
    if upload_result.get('success'):
        print(f"   ✓ Uploaded: {upload_result.get('filename')}")
        print(f"   Shape: {upload_result.get('shape')}")
    else:
        print(f"   ❌ Upload failed: {upload_result.get('error')}")
        return
    
    # 3. Evaluate fitness
    print("\n3. Evaluating data fitness...")
    fitness = client.evaluate_fitness()
    if fitness.get('success'):
        summary = fitness['summary']
        print(f"   Total Records: {summary['total_records']}")
        print(f"   Average Fitness: {summary['average_fitness']:.2f}%")
        print(f"   Records Needing Cleaning: {summary['records_needing_cleaning']}")
        print(f"\n   Health Breakdown:")
        breakdown = summary['health_breakdown']
        print(f"   ✅ Excellent: {breakdown['excellent']}")
        print(f"   ✔️  Good: {breakdown['good']}")
        print(f"   ⚠️  Fair: {breakdown['fair']}")
        print(f"   ❌ Poor: {breakdown['poor']}")
        print(f"   🔴 Critical: {breakdown['critical']}")
    else:
        print(f"   ❌ Evaluation failed: {fitness.get('error')}")
        return
    
    # 4. Check specific records
    print("\n4. Checking specific records...")
    for idx in [0, 5, 10]:
        record_fitness = client.get_record_fitness(idx)
        if record_fitness.get('success'):
            f = record_fitness['fitness']
            print(f"   Record {idx}: {f['overall_fitness']:.1f}% ({f['health_status']})")
            if f['issues']:
                print(f"      Issues: {', '.join(f['issues'][:2])}")
    
    # 5. Compare methods (optional - takes longer)
    print("\n5. Comparing cleaning methods...")
    print("   (This may take a minute...)")
    compare_result = client.compare_methods()
    if compare_result.get('success'):
        results = compare_result['results']
        print(f"\n   Method Comparison:")
        for method, result in results.items():
            if 'error' not in result:
                print(f"   {method.upper():8} - Improvement: +{result['improvement']:.2f}%")
        print(f"\n   🏆 Best Method: {compare_result['best_method'].upper()}")
    
    # 6. Clean with best method
    print("\n6. Cleaning data with best method...")
    best_method = compare_result.get('best_method', 'hybrid')
    clean_result = client.clean_data(method=best_method, save_result=True)
    
    if clean_result.get('success'):
        report = clean_result['report']
        print(f"   Method: {clean_result['method']}")
        print(f"   Before: {report['before']['average_fitness']:.2f}%")
        print(f"   After:  {report['after']['average_fitness']:.2f}%")
        print(f"   Improvement: +{report['improvement']['fitness_increase']:.2f}%")
        print(f"   Records Fixed: {report['improvement']['records_fixed']}")
    else:
        print(f"   ❌ Cleaning failed: {clean_result.get('error')}")
        return
    
    # 7. Export cleaned data
    print("\n7. Exporting cleaned data...")
    export_result = client.export_data("cleaned_output.csv")
    if export_result.get('success'):
        print(f"   ✓ Exported to: {export_result.get('file_path')}")
    else:
        print(f"   ❌ Export failed: {export_result.get('error')}")
    
    print("\n" + "="*60)
    print("Workflow completed successfully!")
    print("="*60)
    print("\nFiles created:")
    print("  - test_original_data.csv (original data)")
    print("  - cleaned_output.csv (cleaned data)")
    print("\nYou can compare these files to see the improvements!")


def quick_clean_example(file_path, output_path="cleaned.csv"):
    """Quick example: Just upload, clean, and export"""
    
    client = FastMigClient()
    
    print(f"Quick Clean: {file_path}")
    print("-" * 40)
    
    # Upload
    print("Uploading...")
    result = client.upload_file(file_path)
    if not result.get('success'):
        print(f"Error: {result.get('error')}")
        return
    
    # Evaluate
    print("Evaluating fitness...")
    fitness = client.evaluate_fitness()
    print(f"Average fitness: {fitness['summary']['average_fitness']:.2f}%")
    
    # Clean
    print("Cleaning with hybrid method...")
    clean_result = client.clean_data(method="hybrid")
    if clean_result.get('success'):
        improvement = clean_result['report']['improvement']['fitness_increase']
        print(f"Improvement: +{improvement:.2f}%")
    
    # Export
    print(f"Exporting to {output_path}...")
    export_result = client.export_data(output_path)
    print(f"✓ Done! Check {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Quick mode with file argument
        file_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else "cleaned.csv"
        quick_clean_example(file_path, output_path)
    else:
        # Full example workflow
        example_workflow()
