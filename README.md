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
<a href="https://github.com/techgenii/travelstyle/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-98%25-brightgreen.svg" /></a><details><summary>Code Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>app</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py">main.py</a></td><td>32</td><td>4</td><td>88%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py#L27-L30">27&ndash;30</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py#L82">82</a></td></tr><tr><td colspan="5"><b>app/api/v1</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py">auth.py</a></td><td>117</td><td>3</td><td>97%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L179">179</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L207">207</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L250">250</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py">user.py</a></td><td>27</td><td>3</td><td>89%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L38-L40">38&ndash;40</a></td></tr><tr><td colspan="5"><b>app/core</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py">security.py</a></td><td>45</td><td>3</td><td>93%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L77-L79">77&ndash;79</a></td></tr><tr><td colspan="5"><b>app/services</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py">auth_service.py</a></td><td>150</td><td>1</td><td>99%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L162">162</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py">openai_service.py</a></td><td>55</td><td>1</td><td>98%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L77">77</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py">orchestrator.py</a></td><td>73</td><td>2</td><td>97%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L159-L160">159&ndash;160</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py">qloo_service.py</a></td><td>55</td><td>3</td><td>95%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L65">65</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L67">67</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L108">108</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py">supabase_cache.py</a></td><td>72</td><td>3</td><td>96%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L46-L48">46&ndash;48</a></td></tr><tr><td colspan="5"><b>app/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py">error_handlers.py</a></td><td>9</td><td>1</td><td>89%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py#L16">16</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1326</b></td><td><b>24</b></td><td><b>98%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

**Made with ❤️ by [TechGenii](https://github.com/techgenii)**
