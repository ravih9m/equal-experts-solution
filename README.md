# Operability Take-Home: Gist Service

A containerized, production-ready microservice that exposes a simplified REST API to retrieve public GitHub Gists for a specific user.

This service is designed with **Site Reliability Engineering (SRE)** principles in mind: observability, security, failure management, and simplicity.

## 📋 Table of Contents
1. [Quick Start](#-quick-start)
2. [Architecture & Trade-offs](#-architecture--trade-offs)
3. [Operational Maturity](#-operational-maturity)
4. [API Reference](#-api-reference)
5. [Deployment (Kubernetes)](#%EF%B8%8F-deployment-kubernetes)
6. [Troubleshooting & Runbook](#-troubleshooting--runbook)

---

## 🚀 Quick Start

### Prerequisites
* **Docker Engine** (20.10+)
* **Make** (Optional, for simplified commands)
* **cURL** or a browser

### Build and Run (Standalone)
To spin up the service locally on port **8080**:

```bash
# 1. Build the Docker image
docker build -t gist-service:latest .

# 2. Run the container (detached mode)
docker run -d -p 8080:8080 --name gist-app gist-service:latest

# 3. Verify it works
curl -v http://localhost:8080/octocat
```

Run Tests
Unit tests are included to validate logic without hitting the real GitHub API (using mocks).

Bash
# Run tests inside the container build process or locally
docker run --rm gist-service:latest pytest tests/ -v
🏗 Architecture & Trade-offs
Design Pattern: Synchronous Proxy
The service acts as a pass-through proxy to the GitHub API, transforming the response into a list of Gist objects.

Decision	Choice	Rationale	Trade-off
Language	Python (FastAPI)	Native Async I/O support handles concurrent requests efficiently without blocking threads.	Slightly higher memory footprint than Go/Rust, but faster development velocity.
State	Stateless	Meets the requirement for "Simplicity." No external database dependencies.	Heavy traffic is bound by GitHub's rate limits (60 reqs/hr for unauthenticated IP).
Security	Non-Root User	The container runs as a standard user (appuser) to prevent container breakout escalation.	Requires care when mounting volumes (permissions).
Alternative Approaches Considered
Caching Proxy (Redis): Adding Redis would reduce latency and save API quota. Rejected to strictly adhere to the "no fancy dependencies/simple solution" constraint of the assignment.

Async Worker (Queue): Decoupling fetching from serving. Rejected because users expect synchronous feedback for "List" operations.

🛡 Operational Maturity
This service is built to be "Production Ready" out of the box.

1. Observability
   Structured Logging: All logs are emitted in JSON format (time, level, message) for easy ingestion by Datadog, Splunk, or ELK.

Health Checks: Exposes /healthz for Kubernetes Liveness/Readiness probes.

Metrics: The Fetch logic includes timing logging to help debug upstream latency.

2. Failure Handling
   Timeouts: All upstream calls to GitHub have a strict 10-second timeout. This prevents the application threads from hanging indefinitely if GitHub goes down.

Graceful Degredation:

404 User Not Found -> Returns clean 404 to client.

Github API Down (5xx) -> Returns 502 Bad Gateway (signals it's not our code crashing).

Rate Limit Exceeded -> Logs warning and returns 429.

📖 API Reference
Get User Gists
Returns a list of public gists.

URL: /{username}

Method: GET

Success Response: 200 OK

JSON
[
{
"id": "6fd34...",
"url": "[https://gist.github.com/](https://gist.github.com/)...",
"files": { "file.txt": { ... } },
"description": "Example Gist"
}
]
Health Check
Used by Load Balancers and K8s.

URL: /healthz

Method: GET

Response: {"status": "ok"}

☸️ Deployment (Kubernetes)
Manifests are located in the k8s/ directory. They include Resource Limits and Security Contexts.

Bash
# Apply the deployment and service
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -l app=gist-api
Production Configuration:

Replicas: 2 (High Availability)

CPU Limit: 200m (Prevents CPU starvation of node)

Memory Limit: 128Mi (Prevents Memory Leaks affecting node)

Readiness Probe: Ensures traffic isn't sent until the app is fully up.

🔧 Troubleshooting & Runbook
Refer to this section if the service is misbehaving.

Scenario A: "The Container won't start"
Symptom: docker run exits immediately.

Check Logs:

Bash
docker logs gist-app
Root Cause Analysis:

If you see Permission denied: Ensure you aren't trying to bind to port 80 inside the container (non-root users cannot bind ports < 1024). We use port 8080.

Scenario B: "I'm getting 503 / 502 Errors"
Symptom: API returns upstream errors.

Is GitHub Down?

Check curl -I https://api.github.com/users/octocat/gists from your machine.

Check Rate Limits:

If running from a shared IP (office VPN), GitHub may have blocked the IP.

Fix: Rotate IP or wait 60 minutes.

Scenario C: "Kubernetes Pods are Restarting"
Symptom: kubectl get pods shows high restart counts.

Inspect Events:

Bash
kubectl describe pod <pod-name>
Look for OOMKilled:

If present, the container needs more memory. Increase limits.memory in k8s/deployment.yaml.

Look for LivenessProbe failures:

The app might be "frozen." Check application logs for deadlocks or extremely slow startup times.

Scenario D: "403 Forbidden / Rate Limit"
Symptom: Logs show API rate limit exceeded.

Immediate Fix: The current implementation is unauthenticated (60 req/hr).

Code Fix: Inject a GITHUB_TOKEN env var and update src/main.py to add Authorization: Bearer <token> header to the request.

Maintained by the Operability Team.