# AWS Lambda Deployment Guide

This guide explains how to deploy the TravelStyle AI FastAPI application to AWS Lambda.

## Prerequisites

1. **AWS CLI** installed and configured
2. **AWS Lambda** permissions
3. **GitHub Secrets** configured (for CI/CD)

## Manual Deployment

### 1. Automated Deployment (Recommended)

The GitHub Actions workflow (`.github/workflows/lambda-deploy.yml`) handles the entire deployment process automatically.

**To deploy:**
1. Set up GitHub Secrets (see below)
2. Push to main branch or manually trigger the workflow
3. The workflow will create, package, and deploy everything

### 2. Manual Deployment Package (Alternative)

If you need to create a deployment package manually:

```bash
cd backend
mkdir -p lambda-package
cp -r app lambda-package/
pip install -r requirements.txt -t lambda-package/
cd lambda-package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf lambda-package
```

This will create a `lambda-deployment.zip` file.

### 2. Create Lambda Function

```bash
aws lambda create-function \
  --function-name travelstyle-api \
  --runtime python3.11 \
  --handler app.main.handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 30 \
  --memory-size 512 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role
```

### 3. Configure Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name travelstyle-api \
  --environment Variables='{
    "OPENAI_API_KEY":"your_openai_key",
    "OPENAI_ORG_ID":"your_org_id",
    "QLOO_API_KEY":"your_qloo_key",
    "OPENWEATHER_API_KEY":"your_weather_key",
    "EXCHANGE_API_KEY":"your_exchange_key",
    "SUPABASE_URL":"your_supabase_url",
    "SUPABASE_KEY":"your_supabase_key"
  }'
```

### 4. Update Function Code

```bash
aws lambda update-function-code \
  --function-name travelstyle-api \
  --zip-file fileb://lambda-deployment.zip
```

## Automated Deployment (GitHub Actions)

The `.github/workflows/lambda-deploy.yml` file handles automated deployment.

### Required GitHub Secrets

Configure these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `OPENAI_API_KEY`
- `OPENAI_ORG_ID`
- `QLOO_API_KEY`
- `OPENWEATHER_API_KEY`
- `EXCHANGE_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Lambda Configuration

### Handler
- **Handler**: `app.main.handler`
- **Runtime**: `python3.11`
- **Timeout**: 30 seconds
- **Memory**: 512 MB (minimum recommended)

### Environment Variables
All API keys and configuration values are set as environment variables.

## API Gateway Integration

After deploying to Lambda, you'll need to:

1. **Create API Gateway** REST API
2. **Create Resource** for your API
3. **Create Methods** (GET, POST, etc.)
4. **Integrate** with your Lambda function
5. **Deploy** the API

### Example API Gateway Setup

```bash
# Create API
aws apigateway create-rest-api \
  --name "TravelStyle API" \
  --description "TravelStyle AI API"

# Get API ID and root resource ID
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`TravelStyle API`].id' --output text)
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create proxy resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part "{proxy+}"

# Get proxy resource ID
PROXY_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/{proxy+}`].id' --output text)

# Create ANY method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $PROXY_ID \
  --http-method ANY \
  --authorization-type NONE

# Set Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $PROXY_ID \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$AWS_REGION:$ACCOUNT_ID:function:travelstyle-api/invocations
```

## Testing

### Local Testing

```bash
# Test the handler locally
python -c "
from app.main import handler
import json

event = {
    'httpMethod': 'GET',
    'path': '/health',
    'headers': {},
    'queryStringParameters': None,
    'body': None
}

result = handler(event, {})
print(json.dumps(result, indent=2))
"
```

### Lambda Testing

Use the AWS Lambda console or CLI to test your function:

```bash
aws lambda invoke \
  --function-name travelstyle-api \
  --payload '{"httpMethod":"GET","path":"/health","headers":{},"queryStringParameters":null,"body":null}' \
  response.json
```

## Monitoring

- **CloudWatch Logs**: View function logs
- **CloudWatch Metrics**: Monitor performance
- **X-Ray**: Trace requests (optional)

## Troubleshooting

### Common Issues

1. **Timeout Errors**: Increase timeout or optimize code
2. **Memory Errors**: Increase memory allocation
3. **Import Errors**: Check all dependencies are included
4. **Environment Variables**: Verify all required variables are set

### Debugging

```bash
# View function logs
aws logs tail /aws/lambda/travelstyle-api --follow

# Get function configuration
aws lambda get-function --function-name travelstyle-api
```

## Cost Optimization

- Use **Provisioned Concurrency** for consistent performance
- Monitor **Cold Start** times
- Consider **Lambda Layers** for shared dependencies
- Use **Reserved Concurrency** to control costs
