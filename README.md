# TravelStyle AI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python Version](https://img.shields.io/badge/python-3.13-blue)
[![TypeScript](https://img.shields.io/badge/typescript-4.0+-blue.svg)](https://www.typescriptlang.org/)

## 📊 Quality & Status

[![CI/CD](https://github.com/techgenii/travelstyle/workflows/Backend%20Quality%20CI%2FCD/badge.svg)](https://github.com/techgenii/travelstyle/actions)
[![codecov](https://codecov.io/github/techgenii/travelstyle/branch/main/graph/badge.svg?token=09BL7TAJDH)](https://codecov.io/github/techgenii/travelstyle)
[![Ruff](https://img.shields.io/badge/ruff-0%20issues-brightgreen)](https://github.com/techgenii/travelstyle/actions)
[![Bandit](https://img.shields.io/badge/bandit-0%20issues-brightgreen)](https://github.com/techgenii/travelstyle/actions)
[![Tests](https://img.shields.io/badge/tests-0%20passed-brightgreen)](https://github.com/techgenii/travelstyle/actions)

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

---

**Made with ❤️ by [TechGenii](https://github.com/techgenii)**
