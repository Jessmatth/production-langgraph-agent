# GCP setup for Vertex AI Agent Engine

Complete these steps before running `python deploy.py deploy`.

## 1. Create a Google Cloud project

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and note the **Project ID** (IAM & Admin → Settings)
3. Attach a **billing account** (required for Vertex AI)

**Use only the Project ID** (e.g. `agents-production-demo`), not the project number (digits only).

| Field | Use for deploy? |
|-------|-----------------|
| Project ID | Yes |
| Project number | No |
| Project name | No (display label) |

## 2. Enable APIs

```bash
export PROJECT_ID="your-project-id"
gcloud config set project "${PROJECT_ID}"
gcloud services enable aiplatform.googleapis.com storage.googleapis.com
```

Or enable [Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com) and Cloud Storage API in the console.

## 3. Authenticate locally

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project "${PROJECT_ID}"
```

## 4. Create staging bucket

```bash
export PROJECT_ID="your-project-id"
export LOCATION="us-central1"
export BUCKET_NAME="${PROJECT_ID}-agent-engine-staging"

test -n "${PROJECT_ID}" && [ "${PROJECT_ID}" != "your-project-id" ] || \
  { echo "Set PROJECT_ID to your GCP project ID first"; exit 1; }

gcloud storage buckets create "gs://${BUCKET_NAME}" \
  --project="${PROJECT_ID}" \
  --location="${LOCATION}" \
  --uniform-bucket-level-access
```

Verify:

```bash
gcloud storage ls "gs://${BUCKET_NAME}/"
```

## 5. IAM

Grant your Google account:

- `roles/aiplatform.user`
- Storage access on the staging bucket (`roles/storage.objectAdmin` on the bucket, or `roles/storage.admin` on the project for a simple demo)

Console: **IAM & Admin** → **Grant Access**.

## 6. Configure `.env`

```bash
cp .env.example .env
```

Example for project `agents-production-demo`:

```
GOOGLE_CLOUD_PROJECT=agents-production-demo
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_ENGINE_STAGING_BUCKET=gs://agents-production-demo-agent-engine-staging
AGENT_DISPLAY_NAME=production-langgraph-agent
AGENT_DESCRIPTION=LangGraph product agent on Vertex Agent Engine
```

## 7. Sanity check

```bash
gcloud config get-value project
python -c "import vertexai; print('ok')"
```

## Cost and cleanup

- Agent Engine bills while a deployment exists; run `python deploy.py delete` after demos
- Staging bucket storage is inexpensive; optional cleanup: `gcloud storage rm --recursive gs://BUCKET_NAME/**`
