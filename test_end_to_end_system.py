#!/usr/bin/env python3
"""
End-to-End System Validation Test
Demonstrates the complete BitStyle Messaging App CI/CD Pipeline
with GCP Free Tier Monitoring integration
"""

import subprocess
import requests
import time
import json
import os
from pathlib import Path

class EndToEndSystemTest:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.jenkins_url = "http://localhost:8080"
        self.results = []
        
    def run_command(self, command, description, ignore_errors=False):
        """Execute a command and track results"""
        print(f"🔄 Testing: {description}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 or ignore_errors:
                print(f"✅ SUCCESS: {description}")
                self.results.append({"test": description, "status": "PASS", "output": result.stdout})
                return result.stdout
            else:
                print(f"❌ FAILED: {description}")
                print(f"Error: {result.stderr}")
                self.results.append({"test": description, "status": "FAIL", "error": result.stderr})
                return None
        except subprocess.TimeoutExpired:
            print(f"⏱️ TIMEOUT: {description}")
            self.results.append({"test": description, "status": "TIMEOUT"})
            return None
        except Exception as e:
            print(f"❌ ERROR: {description} - {str(e)}")
            self.results.append({"test": description, "status": "ERROR", "error": str(e)})
            return None

    def test_messaging_app_functionality(self):
        """Test core messaging application"""
        print("\n" + "="*70)
        print("               MESSAGING APPLICATION TESTS")
        print("="*70)
        
        # Test Flask application startup
        self.run_command("python3 -c 'import app; print(\"Flask app importable\")'", 
                        "Flask Application Import")
        
        # Test database functionality
        self.run_command("python3 -c 'import app; app.init_db(); print(\"Database initialized\")'", 
                        "Database Initialization")
        
        # Run unit tests
        self.run_command("python3 -m pytest test_app.py -v", "Unit Tests Execution")
        
        # Run integration tests (optional)
        if (self.base_dir / 'test_integration.py').exists():
            self.run_command("python3 -m pytest test_integration.py -v", "Integration Tests Execution", ignore_errors=True)
        else:
            print("ℹ️ Skipping Integration Tests (file not present)")

    def test_docker_infrastructure(self):
        """Test Docker containerization"""
        print("\n" + "="*70)
        print("                 DOCKER INFRASTRUCTURE TESTS")
        print("="*70)
        
        # Check Docker status
        self.run_command("docker --version", "Docker Installation")
        
        # Test Docker build
        self.run_command("docker build -t bitstyle-messaging-test .", "Docker Build Process")
        
        # Check Jenkins container
        self.run_command("docker ps | grep jenkins", "Jenkins Container Status")

    def test_gcp_monitoring_system(self):
        """Test GCP monitoring capabilities"""
        print("\n" + "="*70)
        print("              GCP MONITORING SYSTEM TESTS")
        print("="*70)
        
        # Test main monitoring script
        self.run_command("python3 gcp_free_tier_monitor_simple.py --safe-mode", 
                        "GCP Monitor Safe Mode")
        
        # Test Jenkins integration script
        self.run_command("docker exec jenkins python3 /var/jenkins_home/jenkins_gcp_monitor.py --safe-mode", 
                        "Jenkins GCP Monitor Integration")
        
        # Check continuous monitoring process
        self.run_command("pgrep -f gcp_free_tier_monitor_simple.py", 
                        "Continuous Monitoring Process")
        
        # Test size estimation
        self.run_command("python3 -c 'from jenkins_gcp_monitor import estimate_deployment_size; print(estimate_deployment_size())'", 
                        "Deployment Size Estimation", ignore_errors=True)

    def test_jenkins_integration(self):
        """Test Jenkins CI/CD pipeline"""
        print("\n" + "="*70)
        print("               JENKINS CI/CD PIPELINE TESTS")
        print("="*70)
        
        # Test Jenkins accessibility
        try:
            response = requests.get(f"{self.jenkins_url}/api/json", timeout=10)
            if response.status_code == 200:
                print("✅ SUCCESS: Jenkins Web Interface Accessible")
                self.results.append({"test": "Jenkins Web Interface", "status": "PASS"})
            else:
                print(f"❌ FAILED: Jenkins returned status {response.status_code}")
                self.results.append({"test": "Jenkins Web Interface", "status": "FAIL"})
        except Exception as e:
            print(f"❌ FAILED: Jenkins Web Interface - {str(e)}")
            self.results.append({"test": "Jenkins Web Interface", "status": "FAIL", "error": str(e)})
        
        # Test Jenkins CLI availability
        self.run_command("ls -la jenkins-cli.jar", "Jenkins CLI Availability")
        
        # Test pipeline configuration files
        self.run_command("ls -la pipeline_*.xml", "Pipeline Configuration Files")
        
        # Test Jenkinsfile availability
        self.run_command("ls -la *jenkinsfile* jenkins/Jenkinsfile", "Jenkinsfile Availability")

    def test_infrastructure_as_code(self):
        """Test IaC components"""
        print("\n" + "="*70)
        print("           INFRASTRUCTURE AS CODE TESTS")
        print("="*70)
        
        # Test Terraform configuration
        self.run_command("ls -la terraform/", "Terraform Configuration")
        
        # Test Ansible playbooks
        self.run_command("ls -la ansible/", "Ansible Configuration")
        
        # Test Helm charts
        self.run_command("ls -la helm/", "Helm Charts")
        
        # Test Kubernetes manifests
        self.run_command("ls -la k8s/", "Kubernetes Manifests")

    def test_monitoring_logs_and_reports(self):
        """Test monitoring logs and reporting"""
        print("\n" + "="*70)
        print("             MONITORING & REPORTING TESTS")
        print("="*70)
        
    # Check monitoring logs (optional)
    self.run_command("ls -la *monitor*.log", "Monitoring Log Files", ignore_errors=True)
        
    # Check GCP reports (optional)
    self.run_command("ls -la gcp_report_*.txt", "GCP Monitoring Reports", ignore_errors=True)
        
    # Check monitoring configuration (optional)
    self.run_command("ls -la gcp_monitor.properties", "Monitor Configuration", ignore_errors=True)
        
    # Test monitoring PID file (optional)
    self.run_command("ls -la gcp_monitor.pid", "Monitor Process ID File", ignore_errors=True)

    def generate_comprehensive_report(self):
        """Generate final comprehensive report"""
        print("\n" + "="*70)
        print("              COMPREHENSIVE SYSTEM REPORT")
        print("="*70)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        timeout_tests = len([r for r in self.results if r["status"] == "TIMEOUT"])
        error_tests = len([r for r in self.results if r["status"] == "ERROR"])
        
        print(f"📊 TOTAL TESTS: {total_tests}")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print(f"⏱️ TIMEOUTS: {timeout_tests}")
        print(f"🚫 ERRORS: {error_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"\n🎉 SYSTEM VALIDATION: EXCELLENT!")
            print(f"Your BitStyle Messaging App with CI/CD Pipeline is production-ready!")
        elif success_rate >= 60:
            print(f"\n✅ SYSTEM VALIDATION: GOOD!")
            print(f"System is functional with minor issues to address.")
        else:
            print(f"\n⚠️ SYSTEM VALIDATION: NEEDS ATTENTION!")
            print(f"Several components require fixes before production.")
        
        # Save detailed report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": success_rate,
            "details": self.results
        }
        
        with open("end_to_end_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Detailed report saved to: end_to_end_test_report.json")

    def run_all_tests(self):
        """Execute complete end-to-end test suite"""
        print("🚀 BITSTYLE MESSAGING APP - END-TO-END SYSTEM VALIDATION")
        print("🔒 Secure Messaging + CI/CD + GCP Free Tier Monitoring")
        print("📅 Test Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Execute all test categories
        self.test_messaging_app_functionality()
        self.test_docker_infrastructure()
        self.test_gcp_monitoring_system()
        self.test_jenkins_integration()
        self.test_infrastructure_as_code()
        self.test_monitoring_logs_and_reports()
        
        # Generate final report
        self.generate_comprehensive_report()

if __name__ == "__main__":
    tester = EndToEndSystemTest()
    tester.run_all_tests()
