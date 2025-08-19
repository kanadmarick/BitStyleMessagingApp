# GCP Free Tier Monitoring System

This monitoring system ensures that your GCP resources stay within the Always Free tier limits to prevent unexpected billing charges. It includes automated monitoring, emergency shutdown capabilities, and Jenkins CI/CD integration.

## 🎯 Purpose

The GCP Free Tier Monitor prevents accidental charges by:
- **Monitoring** resource usage against free tier limits
- **Alerting** when limits are approached or exceeded
- **Emergency shutdown** of resources that exceed limits
- **Jenkins integration** to block deployments that would exceed limits

## 📋 Free Tier Limits Monitored

### Compute Engine (Always Free)
- **1 f1-micro instance** per month (US regions only: us-west1, us-central1, us-east1)
- **30 GB-months HDD persistent disk**
- **1 GB of egress per month** (North America to anywhere)

### Cloud Storage (Always Free)
- **5 GB-months regional storage** (US regions only)
- **1 GB network egress** per month (North America to anywhere)
- **Class A Operations**: 5,000 per month
- **Class B Operations**: 50,000 per month

### Other Services
- **BigQuery**: 1 TB queries/month, 10 GB storage
- **Container Registry**: 0.5 GB storage
- **Cloud Build**: 120 build minutes/day

## 📁 Files Overview

### Core Monitor Scripts
- **`gcp_free_tier_monitor.py`** - Full-featured monitor with Google Cloud SDK dependencies
- **`gcp_free_tier_monitor_simple.py`** - Lightweight monitor using gcloud CLI (recommended)
- **`jenkins_gcp_monitor.py`** - Jenkins pipeline integration script

### Setup and Configuration
- **`setup_gcp_monitor.sh`** - Automated setup script
- **`gcp_monitor_requirements.txt`** - Python dependencies for full monitor
- **`GCP_FREE_TIER_MONITORING.md`** - This documentation

### Jenkins Integration
- **`jenkins/Jenkinsfile`** - Updated pipeline with monitoring stages

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Ensure gcloud CLI is installed and authenticated
gcloud --version
gcloud auth list

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Setup (Choose One Method)

#### Method A: Automated Setup
```bash
chmod +x setup_gcp_monitor.sh
./setup_gcp_monitor.sh
```

#### Method B: Manual Setup
```bash
# For simple monitor (recommended)
chmod +x gcp_free_tier_monitor_simple.py

# For full monitor (requires additional dependencies)
pip3 install -r gcp_monitor_requirements.txt
chmod +x gcp_free_tier_monitor.py
```

### 3. Basic Usage

#### One-time Check (Safe Mode - No Shutdown)
```bash
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID --no-shutdown
```

#### One-time Check (With Emergency Shutdown)
```bash
# ⚠️ WARNING: This can shut down resources if limits are exceeded
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID
```

#### Continuous Monitoring
```bash
# Monitor every 5 minutes with emergency shutdown enabled
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID --continuous

# Monitor every hour (3600 seconds) in safe mode
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID --continuous --interval 3600 --no-shutdown
```

## 🔧 Configuration Options

### Command Line Arguments

```bash
python3 gcp_free_tier_monitor_simple.py [OPTIONS]

Options:
  --project-id TEXT        GCP Project ID (required)
  --no-shutdown           Disable emergency shutdown (monitoring only)
  --continuous            Run continuously instead of one-time check
  --interval INTEGER      Check interval in seconds (default: 300)
```

### Environment Variables

```bash
# Optional: Set default project
export GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## 🚨 Emergency Shutdown Behavior

When violations are detected and emergency mode is enabled:

### Compute Engine Violations
- **Immediately stops** all running instances that exceed limits
- **Stops instances** in non-free regions (outside us-west1, us-central1, us-east1)
- **Stops non-f1-micro** instances

### Storage Violations
- **Empties buckets** that exceed 5GB limit (keeps bucket structure)
- **Reports** buckets in non-free regions

### Alert Generation
- **Creates alert files** with timestamps
- **Logs all actions** to `gcp_monitor_simple.log`
- **Generates reports** with violation details

## 📊 Monitoring Reports

### Sample Output
```
============================================================
GCP FREE TIER MONITORING REPORT
Generated: 2025-08-19 15:54:42.727475
Project: bitstyle-messaging-app
Emergency Mode: ENABLED
============================================================

✅ OK COMPUTE ENGINE
   Running Instances: 1/1
   - messaging-vm (f1-micro) in us-central1-a

✅ OK CLOUD STORAGE
   Storage Usage: 2.31/5.00 GB
   - messaging-bucket: 2.31 GB (US-CENTRAL1)

============================================================
TOTAL VIOLATIONS: 0
============================================================
```

### Report Files
- **`gcp_report_YYYYMMDD_HHMMSS.txt`** - Detailed monitoring report
- **`gcp_alert_YYYYMMDD_HHMMSS.txt`** - Emergency alert (only if violations found)
- **`gcp_monitor_simple.log`** - Continuous log file

## 🔄 Jenkins CI/CD Integration

The monitoring system integrates with your Jenkins pipeline to prevent deployments that would exceed free tier limits.

### Pipeline Stages Added

1. **Pre-Deployment Check** - Runs before deployment to ensure capacity
2. **Post-Deployment Check** - Verifies deployment stayed within limits

### Jenkins Configuration

The updated `jenkins/Jenkinsfile` includes:

```groovy
stage('GCP Free Tier Check - Pre-Deployment') {
    steps {
        script {
            def result = sh(
                script: "python3 jenkins_gcp_monitor.py --project-id ${PROJECT_ID} --stage pre",
                returnStatus: true
            )
            
            if (result != 0) {
                error("❌ Pre-deployment check failed! Deployment blocked.")
            }
        }
    }
}
```

### Jenkins Environment
- **Build properties** written to `gcp_monitor.properties`
- **Reports archived** as build artifacts
- **Pipeline fails** if limits would be exceeded

## 🛡️ Safety Features

### Multiple Safety Levels
1. **Monitoring Only** (`--no-shutdown`) - Reports but takes no action
2. **Emergency Mode** (default) - Automatically shuts down violating resources
3. **Jenkins Integration** - Prevents deployments that would exceed limits

### Fail-Safe Defaults
- **Conservative limits** - Triggers before reaching actual limits
- **Grace periods** - Allows temporary spikes before taking action
- **Detailed logging** - All actions are logged and reportable
- **Reversible actions** - Stopped instances can be restarted manually

## 📈 System Service Setup (Optional)

To run continuous monitoring as a system service:

```bash
# Create systemd service
sudo cp gcp-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gcp-monitor.service
sudo systemctl start gcp-monitor.service

# Check status
sudo systemctl status gcp-monitor.service

# View logs
sudo journalctl -u gcp-monitor.service -f
```

## 🧪 Testing

### Test Safe Mode
```bash
# This will only report, not take action
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID --no-shutdown
```

### Test Emergency Mode (Be Careful!)
```bash
# Create a test instance first, then run monitor
gcloud compute instances create test-instance --machine-type=e2-micro --zone=us-central1-a
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID
# The e2-micro instance should be stopped
```

## 🔍 Troubleshooting

### Common Issues

#### "gcloud command not found"
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### "Project not found" or "Permission denied"
```bash
# Check authentication
gcloud auth list
gcloud config list

# Re-authenticate if needed
gcloud auth login
gcloud auth application-default login
```

#### "gsutil command not found"
```bash
# Install gsutil
gcloud components install gsutil
```

### Debug Mode
Add verbose logging:
```bash
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT_ID --no-shutdown 2>&1 | tee debug.log
```

## ⚠️ Important Warnings

1. **Emergency Mode**: Can stop/delete resources automatically. Test with `--no-shutdown` first.
2. **Free Tier Regions**: Only us-west1, us-central1, us-east1 are free for Compute Engine.
3. **Resource Limits**: Monitor includes safety margins - actual free tier limits may be slightly higher.
4. **Billing**: This tool helps avoid charges but doesn't guarantee zero billing. Monitor your billing dashboard.
5. **Dependencies**: Simple monitor only needs gcloud CLI. Full monitor needs Python libraries.

## 🤝 Usage in Production

### Recommended Setup
1. Use **simple monitor** for reliability
2. Run **continuous monitoring** with 5-minute intervals
3. Enable **emergency shutdown** in production
4. Use **Jenkins integration** for deployments
5. Set up **alerts** to external monitoring systems

### Best Practices
- **Test first** with `--no-shutdown`
- **Monitor logs** regularly
- **Archive reports** for compliance
- **Review violations** and adjust limits as needed
- **Keep backup** of critical resources

## 📞 Support

For issues or questions:
1. Check the **troubleshooting** section above
2. Review **log files** for detailed error messages
3. Test with **safe mode** (`--no-shutdown`) first
4. Verify **GCP authentication** and permissions

Remember: This tool is designed to help you stay within free tier limits, but you should also monitor your GCP billing dashboard regularly.
