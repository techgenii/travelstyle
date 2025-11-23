# TravelStyle AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
[![TypeScript](https://img.shields.io/badge/typescript-4.0+-blue.svg)](https://www.typescriptlang.org/)

## 📊 Quality & Status

[![CI/CD](https://github.com/techgenii/travelstyle/workflows/Backend%20Quality%20CI%2FCD/badge.svg)](https://github.com/techgenii/travelstyle/actions)
[![codecov](https://codecov.io/github/techgenii/travelstyle/branch/main/graph/badge.svg?token=09BL7TAJDH)](https://codecov.io/github/techgenii/travelstyle)
[![Ruff](https://img.shields.io/badge/ruff-0%20issues-brightgreen)](https://github.com/techgenii/travelstyle/actions)
[![Bandit](https://img.shields.io/badge/bandit-0%20issues-brightgreen)](https://github.com/techgenii/travelstyle/actions)

## Product Vision
TravelStyle AI is an intelligent travel companion chat application that provides personalized wardrobe recommendations, cultural style guidance, and currency conversion tools to help travelers dress appropriately and confidently for any destination.

## Key Features
- **AI-Powered Wardrobe Planning:** Personalized packing and clothing suggestions based on destination, weather, and user preferences.
- **Cultural Style Intelligence:** Qloo-powered insights on local dress codes, etiquette, and style recommendations.
- **Currency Conversion:** Daily updated currency conversion and location-based rates.
- **Conversational Chat Interface:** Natural language chat powered by ChatGPT, with context awareness and multi-turn conversation support.
- **User Preference Learning:** Remembers and applies user style and packing preferences across sessions.
- **Profile Picture Management:** Cloudinary-powered profile picture upload with automatic 300x300 resizing and initials fallback.

## Technical Architecture
- **Backend:** FastAPI (Python), async architecture with 97% test coverage
- **Database:** PostgreSQL (via Supabase)
- **Cache:** Redis (for API rate limiting and caching)
- **AI & APIs:**
  - Qloo Taste AI™ (cultural intelligence, style, etiquette)
  - OpenAI ChatGPT (conversational interface)
  - Visual Crossing (weather data)
  - ExchangeRate-API (currency data)
  - Cloudinary (image processing and storage)
- **Frontend:** React/Next.js (not included in this repo)

## System Overview
```
User Interface (React/Next.js)
    ↓
API Layer (FastAPI)
    ↓
AI Orchestration Layer
    ├── ChatGPT (Conversation Management)
    ├── Qloo Taste AI (Style Intelligence)
    ├── Weather API (Climate Data)
    └── Currency API (Exchange Rates)
    ↓
Database Layer (Supabase/PostgreSQL)
    ├── User Profiles
    ├── Conversation History
    └── Preferences
```

## 📚 Documentation

### **Core Documentation**
- **[README.md](README.md)** - This file - Project overview and getting started
- **[LICENSE](LICENSE)** - GNU General Public License v3.0

### **Component Documentation**
- **[Backend Documentation](backend/README.md)** - Complete backend guide with development, testing, CI/CD, and Lambda deployment
- **[Frontend Documentation](frontend/README.md)** - Frontend-specific documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - General deployment documentation

## Getting Started

### Prerequisites

#### **System Requirements**
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for version control)
- **PostgreSQL** (via Supabase)

#### **Development Tools**
- **AWS CLI** (for Lambda deployment)
- **Bolt.new** (for frontend deployment)
- **Make** (for backend development commands)

#### **Accounts & Services**
- **GitHub account** (for repository and CI/CD)
- **Supabase account** (for database)
- **Bolt.new account** (for frontend hosting)
- **AWS account** (for Lambda deployment)

### API Keys Required
- **OpenAI:** https://platform.openai.com/api-keys
- **Qloo:** https://www.qloo.com/api
- **VisualCrossing:** https://www.visualcrossing.com/
- **Exchange Rate API:** https://www.exchangerate-api.com/
- **Cloudinary:** https://cloudinary.com/ (for profile picture processing)
- **Supabase:** https://supabase.com/dashboard

### Quick Setup

#### **Backend Development:**
```bash
git clone <repo-url>
cd backend
make install-dev
# Copy env.example to .env and configure API keys
make run
```

#### **Frontend Development:**
```bash
cd frontend
npm install
npm run dev
```

#### **Environment Setup**
- **Backend**: Copy `backend/env.example` to `backend/.env` and configure API keys
- **Frontend**: Environment variables are configured in Vercel dashboard
- **Database**: Supabase project setup required for full functionality

**📖 For detailed setup instructions, see [Backend Documentation](backend/README.md#development) and [Frontend Documentation](frontend/README.md)**

## 🚀 Deployment

### Frontend (Vercel)
```bash
npm install -g vercel
vercel link
vercel --prod
```

### Backend (AWS Lambda)
The backend automatically deploys to AWS Lambda via GitHub Actions when you push to `main`.

**Features:**
- ✅ Automated deployment via GitHub Actions
- ✅ 50% package size optimization
- ✅ API Gateway integration
- ✅ Environment variable management
- ✅ Health checks and testing

**📖 For complete deployment instructions, see [Backend Documentation](backend/README.md#lambda-deployment)**

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Live Demo]() *(if available)*
- [Documentation](https://github.com/techgenii/travelstyle/wiki)
- [Report Issues](https://github.com/techgenii/travelstyle/issues)
- [Discussions](https://github.com/techgenii/travelstyle/discussions)

## 🙏 Acknowledgments

- Qloo for Taste AI capabilities
- OpenAI for AI capabilities
- Supabase for backend-as-a-service
- FastAPI for the web framework
- Open source community for tools and libraries
- Contributors and testers

## 📊 Stats

![GitHub last commit](https://img.shields.io/github/last-commit/techgenii/travelstyle)
![GitHub issues](https://img.shields.io/github/issues/techgenii/travelstyle)
![GitHub pull requests](https://img.shields.io/github/issues-pr/techgenii/travelstyle)

## 📊 Test Coverage
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/techgenii/travelstyle/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-95%25-brightgreen.svg" /></a><details><summary>Code Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>app</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/travelstyle.py">travelstyle.py</a></td><td>55</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/api</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/deps.py">deps.py</a></td><td>22</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/api/v1</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py">auth.py</a></td><td>66</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/chat.py">chat.py</a></td><td>90</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/currency.py">currency.py</a></td><td>121</td><td>5</td><td>5</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/currency.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py">recommendations.py</a></td><td>38</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py">user.py</a></td><td>220</td><td>20</td><td>20</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L 91%"> 91%</a></td></tr><tr><td colspan="5"><b>app/core</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/config.py">config.py</a></td><td>31</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py">security.py</a></td><td>45</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L 93%"> 93%</a></td></tr><tr><td colspan="5"><b>app/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/auth.py">auth.py</a></td><td>47</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/responses.py">responses.py</a></td><td>25</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/travel.py">travel.py</a></td><td>113</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/user.py">user.py</a></td><td>102</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py">auth_service.py</a></td><td>3</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/cloudinary_service.py">cloudinary_service.py</a></td><td>71</td><td>9</td><td>9</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/cloudinary_service.py#L 87%"> 87%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database_helpers.py">database_helpers.py</a></td><td>3</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py">orchestrator.py</a></td><td>258</td><td>21</td><td>21</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L 92%"> 92%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/rate_limiter.py">rate_limiter.py</a></td><td>52</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/system_settings_service.py">system_settings_service.py</a></td><td>156</td><td>12</td><td>12</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/system_settings_service.py#L 92%"> 92%</a></td></tr><tr><td colspan="5"><b>app/services/auth</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/__init__.py">__init__.py</a></td><td>5</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/constants.py">constants.py</a></td><td>25</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/exceptions.py">exceptions.py</a></td><td>14</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/helpers.py">helpers.py</a></td><td>376</td><td>36</td><td>36</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/helpers.py#L 90%"> 90%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth/validators.py">validators.py</a></td><td>45</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services/currency</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/__init__.py">__init__.py</a></td><td>5</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/api.py">api.py</a></td><td>106</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/api.py#L 97%"> 97%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/constants.py">constants.py</a></td><td>5</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/exceptions.py">exceptions.py</a></td><td>6</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/formatter.py">formatter.py</a></td><td>31</td><td>6</td><td>6</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/formatter.py#L 81%"> 81%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/helpers.py">helpers.py</a></td><td>120</td><td>20</td><td>20</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/helpers.py#L 83%"> 83%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/parser.py">parser.py</a></td><td>103</td><td>14</td><td>14</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/parser.py#L 86%"> 86%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/validators.py">validators.py</a></td><td>31</td><td>2</td><td>2</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency/validators.py#L 94%"> 94%</a></td></tr><tr><td colspan="5"><b>app/services/database</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/__init__.py">__init__.py</a></td><td>6</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/constants.py">constants.py</a></td><td>26</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/conversations.py">conversations.py</a></td><td>106</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/exceptions.py">exceptions.py</a></td><td>4</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/helpers.py">helpers.py</a></td><td>56</td><td>4</td><td>4</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/helpers.py#L 93%"> 93%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/models.py">models.py</a></td><td>7</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/users.py">users.py</a></td><td>157</td><td>13</td><td>13</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/users.py#L 92%"> 92%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database/validators.py">validators.py</a></td><td>39</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services/openai</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai/openai_service.py">openai_service.py</a></td><td>85</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services/qloo</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo/__init__.py">__init__.py</a></td><td>2</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo/qloo_service.py">qloo_service.py</a></td><td>57</td><td>7</td><td>7</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo/qloo_service.py#L 88%"> 88%</a></td></tr><tr><td colspan="5"><b>app/services/supabase</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/__init__.py">__init__.py</a></td><td>5</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_base.py">supabase_base.py</a></td><td>88</td><td>2</td><td>2</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_base.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_cache_v2.py">supabase_cache_v2.py</a></td><td>132</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_cache_v2.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_client.py">supabase_client.py</a></td><td>73</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase/supabase_config.py">supabase_config.py</a></td><td>54</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services/weather</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather/__init__.py">__init__.py</a></td><td>2</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather/weather_service.py">weather_service.py</a></td><td>75</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py">error_handlers.py</a></td><td>36</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py">rate_limiter.py</a></td><td>60</td><td>9</td><td>9</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py#L 85%"> 85%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/user_utils.py">user_utils.py</a></td><td>18</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><b>TOTAL</b></td><td><b>3478</b></td><td><b>189</b></td><td><b>95%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

**Made with ❤️ by [TechGenii](https://github.com/techgenii)**
