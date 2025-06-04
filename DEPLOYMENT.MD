# 🚀 HappyRobot API Deployment Guide

This guide provides step-by-step instructions for deploying the HappyRobot Carrier Engagement API to various cloud platforms.

## 📋 Prerequisites

- Docker installed locally
- Cloud provider CLI tools configured

### First, try to build the docker-compose and make a curl request to the /health api to know everything builds

```bash
    docker compose up --build -d

    curl http://localhost:8000/health
```

## Google Cloud Run

We'll configure google cloud run with the gcloud cli. In order to use all the environment variables in the .env file do not forget to source it.

```bash
source .env
```

#### 1. Setup Google Cloud
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
# You must set a billing account in google cloud console to your project in order to activate these apis
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### 2. Create Cloud SQL Instance 
```bash
# Create PostgreSQL instance
gcloud sql instances create happyrobot-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create happyrobot --instance=happyrobot-db

# Create user
gcloud sql users create happyrobot-user \
  --instance=happyrobot-db \
  --password=${CLOUD_SQL_PASSWORD}
```

#### 3. Store Secrets
```bash
# Database URL
echo "postgresql://happyrobot-user:${CLOUD_SQL_PASSWORD}@/happyrobot?host=/cloudsql/${PROJECT_ID}:us-central1:happyrobot-db" | \
  gcloud secrets create DATABASE_URL --data-file=-

# API Key
echo "${API_KEY}" | \
  gcloud secrets create API_KEY --data-file=-

echo "${FMCSA_API_KEY}" | \
  gcloud secrets create FMCSA_API_KEY --data-file=-

```

#### 4. Build and Deploy
```bash
# Build container
# Beware if you are using a different CPU architecture - the --platform flag is key
export PROJECT_ID="happyrobot-interview"
gcloud auth configure-docker
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/happyrobot-api .
docker push gcr.io/$PROJECT_ID/happyrobot-api

# Grant Secret Manager Secret Accessor role to cloud Run service account
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"

# Deploy to Cloud Run
gcloud run deploy happyrobot-api \
  --image gcr.io/$PROJECT_ID/happyrobot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances $PROJECT_ID:us-central1:happyrobot-db \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets DATABASE_URL=DATABASE_URL:latest,API_KEY=API_KEY:latest,FMCSA_API_KEY=FMCSA_API_KEY:latest \
  --port 8000

# If the previous command fails, try quoting the entire cloudsql instance string
# I had to try several times but this last command does successfully run the cloud instance
gcloud run deploy happyrobot-api --image gcr.io/$PROJECT_ID/happyrobot-api --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances "${PROJECT_ID}:us-central1:happyrobot-db" --set-env-vars ENVIRONMENT=production --set-secrets DATABASE_URL=DATABASE_URL:latest,API_KEY=API_KEY:latest,FMCSA_API_KEY=FMCSA_API_KEY:latest --port 8000
```


## 🔧 Post-Deployment Setup

### 1. Initialize Database
After deployment, run the database seeding script:

**Cloud Run:**
```bash
gcloud run jobs create seed-data \
  --image gcr.io/$PROJECT_ID/happyrobot-api \
  --command python \
  --args app/core/seed_data.py \
  --region us-central1
  
gcloud run jobs execute seed-data --region us-central1
```


### Common Issues

1. **Database Connection Errors**
   - Export PROJECT_ID
   - The gcloud run deploy command fails with the cloudsql instance sometimes due to formatting
   - Verify network connectivity
   - Ensure IAM user has proper permissions

2. **API Key Authentication Failing**
   - Verify API_KEY environment variable is set
   - Check header format: `X-API-Key: your-key`
   - Ensure no trailing spaces in the key

3. **FMCSA API**
   - It's important to set the cloud run instance's region somewhere in the US. Otherwise you'll get a 403 forbidden from the FMCSA. Had to use a proxy to access the documentation and to run a first scan of the returned object.

4. **PLATFORM LINUX/AMD64**
    - When building from a mac (apple silicon) you must specify the build platform target to avoid issues with the cloud run
