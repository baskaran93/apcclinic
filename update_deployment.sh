#!/bin/bash
set -e

# ---------------------------
# Configuration
# ---------------------------
PROJECT_ID="apcclinic"
REGION="asia-south1"
SERVICE_NAME="apcclinic"
IMAGE="asia-south1-docker.pkg.dev/$PROJECT_ID/apcclinic-repo/apcclinic:latest"

# Environment variables for the app
ENV_VARS="DB_SERVER=insightexpertz.database.windows.net,DB_NAME=APCDB,DB_USERNAME=<USERNAME,DB_PASSWORD='<PASSWORD>',DB_DRIVER='ODBC Driver 18 for SQL Server',SECRET_KEY='your-secret-key'"

# ---------------------------
# Authenticate gcloud (optional if already logged in)
# ---------------------------
# gcloud auth login
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# ---------------------------
# Deploy the new container to Cloud Run
# ---------------------------
echo "Updating Cloud Run service '$SERVICE_NAME' with new image '$IMAGE'..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --update-env-vars $ENV_VARS

echo "✅ Deployment complete!"
