# TravelStyle AI Backend

A FastAPI-based AI-powered travel wardrobe consultant with cultural intelligence, deployed on AWS Lambda.

## 🚀 Quick Start

### Development
```bash
# Install dependencies
make install-dev

# Run tests
make test-quick

# Start development server
make run
```

### Deployment
The application automatically deploys to AWS Lambda via GitHub Actions when you push to `main`.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Development](#development)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Lambda Deployment](#lambda-deployment)
- [Lambda Optimization](#lambda-optimization)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI with Mangum for Lambda compatibility
- **Runtime**: Python 3.11
- **Deployment**: AWS Lambda with API Gateway
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4
- **External APIs**: Qloo, OpenWeather, Exchange Rate API

### Project Structure
```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration and security
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── Makefile            # Development commands
```

## 🛠️ Development

### Prerequisites
- Python 3.11+
- AWS CLI configured
- GitHub repository with secrets configured

### Local Setup
```bash
# Clone and setup
git clone <repository>
cd backend

# Install dependencies
make install-dev

# Run tests
make test-quick

# Start development server
make run
```

### Available Commands

#### **Testing Commands**
```bash
# Run all tests with warnings disabled
make test

# Run tests quickly (no coverage)
make test-quick

# Run specific test suites
make test-chat          # Chat-related tests only
make test-currency      # Currency-related tests only
make test-orchestrator  # Orchestrator tests only
make test-recommendations # Recommendations tests only

# Run tests in watch mode (for development)
make test-watch
```

#### **Development Commands**
```bash
# Run all dev checks (lint, security, test)
make dev

# Run dev checks with clean test output
make dev-clean

# Start development server
make run

# Clean up generated files
make clean
```

#### **Production Commands**
```bash
# Run all prod checks (lint, security, test)
make prod

# Run prod checks with clean test output
make prod-clean
```

## 🧪 Testing

### Test Organization
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Service Tests**: Business logic testing
- **Mock Tests**: External API simulation

### Running Tests
```bash
# Quick test run (no warnings)
make test-quick

# Run specific feature tests
make test-chat
make test-currency
make test-orchestrator
make test-recommendations

# Full quality check before commit
make dev-clean
```

### Test Configuration
- **Coverage Target**: ≥80%
- **Warning Suppression**: Clean test output
- **Artifact Preservation**: 30-day retention
- **Badge Updates**: Automatic quality metrics

## 🔄 CI/CD Pipeline

### Automatic Triggers
- ✅ **Push** to `main` or `develop`
- ✅ **Pull Request** to `main` or `develop`

### Pipeline Stages

1. **Quality Checks** (`quality-checks` job)
   - ✅ Install dependencies
   - ✅ Run linting (Ruff)
   - ✅ Run security scan (Bandit)
   - ✅ Validate and mask secrets
   - ✅ Run tests with improved configuration
   - ✅ Run specific test suites for detailed reporting
   - ✅ Upload coverage reports to Codecov
   - ✅ Upload artifacts

2. **Badge Updates** (`update-badges` job)
   - ✅ Extract metrics from test results
   - ✅ Update README badges
   - ✅ Generate quality summary report

3. **Coverage Updates** (`update-coverage-on-readme` job)
   - ✅ Generate coverage comments
   - ✅ Update README with coverage data

4. **Lambda Deployment** (`deploy` job)
   - ✅ Create optimized Lambda package
   - ✅ Deploy to AWS Lambda
   - ✅ Setup API Gateway
   - ✅ Test deployment

### Key Improvements
- ✅ **Warnings disabled** for clean output
- ✅ **Specific test suites** for targeted testing
- ✅ **Enhanced reporting** with artifacts
- ✅ **Better error handling** and feedback
- ✅ **Optimized Lambda packages** (50% size reduction)

## 🚀 Lambda Deployment

### Automated Deployment (Recommended)

The GitHub Actions workflow (`.github/workflows/lambda-deploy.yml`) handles the entire deployment process automatically.

**To deploy:**
1. Set up GitHub Secrets (see below)
2. Push to main branch or manually trigger the workflow
3. The workflow will create, package, and deploy everything

### Required GitHub Secrets

Configure these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `LAMBDA_FUNCTION_NAME`
- `OPENAI_API_KEY`
- `OPENAI_ORG_ID`
- `QLOO_API_KEY`
- `OPENWEATHER_API_KEY`
- `EXCHANGE_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Lambda Configuration

- **Handler**: `lambda_function.handler`
- **Runtime**: `python3.11`
- **Timeout**: 30 seconds
- **Memory**: 512 MB (minimum recommended)
- **Architecture**: Lambda Layers for optimized deployment

### Manual Deployment (Alternative)

If you need to create a deployment package manually:

```bash
cd backend
mkdir -p lambda-package
cp -r app lambda-package/
pip install -r requirements-lambda.txt -t lambda-package/
cd lambda-package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf lambda-package
```

## 📦 Lambda Optimization

### Package Size Reduction

We've implemented several optimizations to reduce Lambda package size from ~17MB to ~8.7MB (50% reduction):

#### **1. Dependency Optimization**
- **File**: `requirements-lambda.txt`
- **Changes**:
  - Pinned specific versions to avoid bloat
  - Removed unnecessary dependencies
  - Used minimal versions of packages

#### **2. File Cleanup During Build**
- **Removed**:
  - `__pycache__` directories
  - `*.pyc`, `*.pyo`, `*.pyd` files
  - Test directories (`tests/`, `test/`)
  - Documentation files (`*.md`, `*.rst`, `*.html`)
  - Example directories
  - Binary files (`*.so`, `*.dll`, `*.dylib`)

#### **3. Lambda Layers Architecture**
- **Dependencies Layer**: Contains all Python packages
- **App Layer**: Contains application code
- **Function Package**: Minimal handler only

### Size Comparison

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| Dependencies | ~17MB | ~8.7MB | **50%** |
| App Code | ~252KB | ~252KB | No change |
| Total Package | ~17.2MB | ~8.9MB | **48%** |

### Benefits
1. **Faster Deployments** - Smaller packages upload faster
2. **Reduced Cold Start** - Smaller packages load faster
3. **Cost Savings** - Less storage and transfer costs
4. **Better Performance** - Faster Lambda execution

## 📊 Monitoring

### Quality Badges (Auto-updated)
- **Ruff** - Linting issues count
- **Bandit** - Security issues count
- **Tests** - Test pass/fail status

### Coverage Reports
- **Codecov integration** - Automatic coverage uploads
- **README updates** - Coverage data embedded in README
- **Detailed reports** - XML and JSON formats for CI tools

### Artifacts (30-day retention)
- `quality-reports/` - All test results
- `quality-summary.md` - Summary report
- `ruff_junit.xml` - Linting results
- `bandit_report.json` - Security scan results
- `pytest-results.xml` - Test results
- `pytest-coverage.json` - Coverage data

### AWS Monitoring
- **CloudWatch Logs**: View function logs
- **CloudWatch Metrics**: Monitor performance
- **X-Ray**: Trace requests (optional)

## 🔍 Troubleshooting

### Common Issues

#### **1. Tests Failing in CI but Passing Locally**
```bash
# Run the same test configuration locally
make test

# Check for environment variable differences
echo $OPENAI_API_KEY
echo $SUPABASE_URL
```

#### **2. Warnings Still Appearing**
```bash
# Ensure you're using the improved configuration
make test-quick

# Check pytest.ini and conftest.py for warning filters
cat pytest.ini
cat tests/conftest.py
```

#### **3. Lambda Deployment Issues**
```bash
# Check Lambda function status
aws lambda get-function --function-name $FUNCTION_NAME

# View function logs
aws logs tail /aws/lambda/$FUNCTION_NAME --follow

# Test function locally
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

#### **4. Package Size Issues**
```bash
# Check package size
du -h lambda-deploy.zip

# Verify layer creation
ls -la layers/
du -h dependencies-layer.zip app-layer.zip
```

### Debugging CI/CD

#### **1. Check Workflow Logs**
- Go to GitHub Actions tab
- Click on the specific workflow run
- Check the `quality-checks` job logs

#### **2. Download Artifacts**
- In the workflow run, go to "Artifacts" section
- Download `quality-reports` to inspect test results
- Download `quality-summary` for the summary report

#### **3. Local Reproduction**
```bash
# Reproduce CI environment locally
make install-dev
make test
```

## 📈 Success Metrics

### Quality Metrics Tracked
- **Lint Issues**: Target 0 issues
- **Security Issues**: Target 0 issues
- **Test Coverage**: Target ≥80%
- **Test Failures**: Target 0 failures

### Performance Metrics
- **Test Execution Time**: Monitored in CI logs
- **Coverage Trends**: Tracked over time
- **Failure Rates**: Per test suite
- **Lambda Package Size**: Target <10MB

## 🎯 Best Practices

### **1. Development Workflow**
```bash
# Before committing
make test-quick          # Quick feedback
make dev-clean           # Full quality check
```

### **2. Feature Development**
```bash
# When working on specific features
make test-chat           # For chat features
make test-currency       # For currency features
make test-watch          # For continuous feedback
```

### **3. Pull Request Preparation**
```bash
# Ensure all checks pass
make prod-clean          # Full production check
```

### **4. Monitoring**
- Check GitHub Actions for workflow status
- Monitor badge updates in README
- Review coverage reports in Codecov
- Check quality summary artifacts

## 🔄 Continuous Improvement

### Adding New Test Suites
1. Create new test file: `tests/test_new_feature.py`
2. Add Makefile target: `test-new-feature`
3. Update CI workflow to include new suite
4. Update documentation

### Updating Warning Filters
1. Identify new warnings in test output
2. Add filters to `pytest.ini` or `conftest.py`
3. Test locally with `make test-quick`
4. Commit and push changes

### Enhancing Reporting
1. Modify badge generation in CI workflow
2. Add new metrics to quality summary
3. Update documentation
4. Test with `make prod-clean`

## 🎉 Summary

This backend provides:
- ✅ **FastAPI-based API** with Lambda deployment
- ✅ **Comprehensive testing** with organized test suites
- ✅ **Automated CI/CD** with quality checks
- ✅ **Optimized Lambda packages** (50% size reduction)
- ✅ **Clean development experience** with warnings suppressed
- ✅ **Production-ready** quality and monitoring

The setup ensures high code quality, fast feedback loops, reliable deployments, and excellent developer experience! 🚀
