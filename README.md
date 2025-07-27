# TravelStyle AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
[![TypeScript](https://img.shields.io/badge/typescript-4.0+-blue.svg)](https://www.typescriptlang.org/)

## 📊 Quality & Status

[![CI/CD](https://github.com/techgenii/travelstyle/workflows/Backend%20Quality%20CI%2FCD/badge.svg)](https://github.com/techgenii/travelstyle/actions)
[![codecov](https://codecov.io/github/techgenii/travelstyle/branch/main/graph/badge.svg?token=09BL7TAJDH)](https://codecov.io/github/techgenii/travelstyle)
[![Ruff](https://img.shields.io/badge/ruff-0%20issues-brightgreen)](https://github.com/techgenii/travelstyle/actions)
[![Bandit](https://img.shields.io/badge/bandit-1%20issues-orange)](https://github.com/techgenii/travelstyle/actions)

## Product Vision
TravelStyle AI is an intelligent travel companion chat application that provides personalized wardrobe recommendations, cultural style guidance, and currency conversion tools to help travelers dress appropriately and confidently for any destination.

## Key Features
- **AI-Powered Wardrobe Planning:** Personalized packing and clothing suggestions based on destination, weather, and user preferences.
- **Cultural Style Intelligence:** Qloo-powered insights on local dress codes, etiquette, and style recommendations.
- **Currency Conversion:** Daily updated currency conversion and location-based rates.
- **Conversational Chat Interface:** Natural language chat powered by ChatGPT, with context awareness and multi-turn conversation support.
- **User Preference Learning:** Remembers and applies user style and packing preferences across sessions.

## Technical Architecture
- **Backend:** FastAPI (Python), async architecture
- **Database:** PostgreSQL (via Supabase)
- **Cache:** Redis (for API rate limiting and caching)
- **AI & APIs:**
  - Qloo Taste AI™ (cultural intelligence, style, etiquette)
  - OpenAI ChatGPT (conversational interface)
  - OpenWeatherMap (weather data)
  - ExchangeRate-API (currency data)
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

## Project Structure
```plaintext
travelstyle-ai
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── api
│   │   ├── core
│   │   ├── main.py
│   │   ├── models
│   │   ├── services
│   │   └── utils
│   ├── env.example
│   ├── Makefile
│   ├── pytest.ini
│   ├── pytest.xml
│   ├── requirements-test.txt
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth_service.py
│       ├── test_auth.py
│       ├── test_chat_convs.py
│       ├── test_chat_feedback.py
│       ├── test_chat_sessions.py
│       ├── test_chat.py
│       ├── test_currency_service.py
│       ├── test_database_helpers_comprehensive.py
│       ├── test_database_helpers_simple.py
│       ├── test_deps.py
│       ├── test_main.py
│       ├── test_rate_limiter.py
│       ├── test_recommendations.py
│       ├── test_security.py
│       ├── test_supabase_cache.py
│       ├── test_user_api.py
│       ├── test_user_models.py
│       ├── test_user_session_management.py
│       ├── test_user_utils.py
│       └── test_weather_service.py
├── LICENSE
├── pyproject.toml
├── README.md
└── supabase
    └── migrations
        ├── travelstyle_index.sql
        ├── travelstyle_schema.sql
        └── travelstyle_triggers.sql
```


## Getting Started

### Prerequisites
- Python 3.13+
- PostgreSQL (via Supabase)

### Where to get API Keys
- OpenAI: https://platform.openai.com/api-keys

- Qloo: https://www.qloo.com/api

- OpenWeather: https://openweathermap.org/api

- Exchange Rate API: https://www.exchangerate-api.com/

- Supabase: https://supabase.com/dashboard

### Setup
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd backend
   ```
2. **Install dependencies:**
   ```bash
   make install
   ```
3. **Configure environment variables:**
   - Copy `env.example` to `.env` and fill in your API keys and secrets.
4. **Run locally:**
   ```bash
   make run
   ```

### Running Tests
```bash
cd backend
make test
```

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
<a href="https://github.com/techgenii/travelstyle/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-97%25-brightgreen.svg" /></a><details><summary>Code Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>app</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py">main.py</a></td><td>45</td><td>10</td><td>10</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py#L 78%"> 78%</a></td></tr><tr><td colspan="5"><b>app/api</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/deps.py">deps.py</a></td><td>22</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/api/v1</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py">auth.py</a></td><td>118</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L 97%"> 97%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/chat.py">chat.py</a></td><td>91</td><td>5</td><td>5</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/chat.py#L 95%"> 95%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/currency.py">currency.py</a></td><td>54</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py">recommendations.py</a></td><td>78</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py">user.py</a></td><td>76</td><td>5</td><td>5</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L 93%"> 93%</a></td></tr><tr><td colspan="5"><b>app/core</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/config.py">config.py</a></td><td>26</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py">security.py</a></td><td>45</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L 93%"> 93%</a></td></tr><tr><td colspan="5"><b>app/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/auth.py">auth.py</a></td><td>46</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/responses.py">responses.py</a></td><td>23</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/travel.py">travel.py</a></td><td>113</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/user.py">user.py</a></td><td>96</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/services</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py">auth_service.py</a></td><td>145</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_conversion_service.py">currency_conversion_service.py</a></td><td>75</td><td>7</td><td>7</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_conversion_service.py#L 91%"> 91%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_service.py">currency_service.py</a></td><td>69</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/database_helpers.py">database_helpers.py</a></td><td>117</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py">openai_service.py</a></td><td>67</td><td>3</td><td>3</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L 96%"> 96%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py">orchestrator.py</a></td><td>82</td><td>2</td><td>2</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L 98%"> 98%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py">qloo_service.py</a></td><td>57</td><td>9</td><td>9</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L 84%"> 84%</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py">supabase_cache.py</a></td><td>76</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py">weather_service.py</a></td><td>110</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>app/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py">error_handlers.py</a></td><td>9</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py">rate_limiter.py</a></td><td>51</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/user_utils.py">user_utils.py</a></td><td>18</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><b>TOTAL</b></td><td><b>1709</b></td><td><b>50</b></td><td><b>97%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

**Made with ❤️ by [TechGenii](https://github.com/techgenii)**
