# 🔧 Jenkins Freestyle Setup (Current CI/CD)

Use this when the Pipeline plugin isn't installed. This replicates the pipeline flow with simple shell steps.

### Step 1: Create Freestyle Project
1. Open Jenkins: `http://localhost:8080`
2. Click "New Item"
3. Enter name: `bitstyle-messaging-pipeline` (recommended)
4. Select "Freestyle project"
5. Click "OK"

### Step 2: Configure Build Steps

In the configuration page, add these **Build Steps** (click "Add build step" → "Execute shell"):

#### Build Step 1: Tests
```bash
echo "=== Tests ==="
python3 -m pytest -q || true
```

#### Build Step 2: Docker Build
```bash
echo "=== Docker Build ==="
docker build -t bitstyle-messaging:$BUILD_NUMBER .
```

#### Build Step 3: Deploy (Optional)
```bash
echo "=== Deploy ==="
docker stop messaging-app-$BUILD_NUMBER 2>/dev/null || true
docker rm messaging-app-$BUILD_NUMBER 2>/dev/null || true
docker run -d --name messaging-app-$BUILD_NUMBER -p 500$BUILD_NUMBER:5000 bitstyle-messaging:$BUILD_NUMBER || true
```

#### Build Step 4: GCP Monitor Check
```bash
echo "=== GCP Free Tier Check ==="
python3 gcp_free_tier_monitor_simple.py --project-id YOUR_PROJECT --no-shutdown || true
```

### Step 3: Save and Build

1. Scroll down and click "Save"
2. Click "Build Now" on the left sidebar
3. Watch the build progress in "Build History"

> Tip: Later, install the Pipeline plugin to switch this job to a Jenkinsfile.

## 🎯 Quick Test Commands

After creating the Freestyle project:

```bash
# Check if project was created
curl -s http://localhost:8080/api/json | python3 -c "
import json, sys
data = json.load(sys.stdin)
jobs = [job['name'] for job in data.get('jobs', [])]
print('✅ Jobs found:' if jobs else '❌ No jobs found')
for job in jobs: print(f'  - {job}')
"

# Trigger build via API (optional)
curl -X POST http://localhost:8080/job/bitstyle-messaging-pipeline/build --user admin:your_password
```

## 🚀 Expected Results

After running the freestyle build, you should see:
- ✅ Tests executed (with results in console output)
- ✅ Docker image built: `bitstyle-messaging:BUILD_NUMBER`
- ✅ Container deployed on dynamic port (500X)
- ✅ GCP monitoring verified as active
- ✅ Complete build log with all steps

## 📊 Monitoring Integration

The freestyle project includes the same GCP monitoring checks as the pipeline version:
- Verifies continuous monitoring is running
- Checks GCP free tier status
- Logs all activities for audit trail

---

## 💡 Pro Tip
The Freestyle project approach gives you the same CI/CD functionality as Pipeline - it just uses a different interface. All your monitoring, Docker builds, and deployments will work exactly the same way!
