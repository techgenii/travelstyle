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
<a href="https://github.com/techgenii/travelstyle/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-39%25-red.svg" /></a><details><summary>Code Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>app</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py">main.py</a></td><td>32</td><td>4</td><td>88%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py#L27-L30">27&ndash;30</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/main.py#L82">82</a></td></tr><tr><td colspan="5"><b>app/api</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/deps.py">deps.py</a></td><td>22</td><td>12</td><td>45%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/deps.py#L22-L39">22&ndash;39</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/deps.py#L49-L51">49&ndash;51</a></td></tr><tr><td colspan="5"><b>app/api/v1</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py">auth.py</a></td><td>117</td><td>38</td><td>68%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L54-L55">54&ndash;55</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L73-L75">73&ndash;75</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L90-L92">90&ndash;92</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L114-L115">114&ndash;115</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L137-L138">137&ndash;138</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L163-L164">163&ndash;164</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L179">179</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L190-L192">190&ndash;192</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L207">207</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L232-L233">232&ndash;233</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/auth.py#L247-L283">247&ndash;283</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py">recommendations.py</a></td><td>64</td><td>12</td><td>81%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py#L48-L50">48&ndash;50</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py#L74-L76">74&ndash;76</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py#L96-L98">96&ndash;98</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/recommendations.py#L123-L125">123&ndash;125</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py">user.py</a></td><td>27</td><td>9</td><td>67%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L27-L29">27&ndash;29</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L38-L40">38&ndash;40</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/api/v1/user.py#L52-L54">52&ndash;54</a></td></tr><tr><td colspan="5"><b>app/core</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py">security.py</a></td><td>45</td><td>29</td><td>36%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L26-L56">26&ndash;56</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L61-L68">61&ndash;68</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L72-L78">72&ndash;78</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L89">89</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/core/security.py#L94">94</a></td></tr><tr><td colspan="5"><b>app/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/travel.py">travel.py</a></td><td>103</td><td>103</td><td>0%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/models/travel.py#L5-L133">5&ndash;133</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/models/user.py">user.py</a></td><td>78</td><td>78</td><td>0%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/models/user.py#L5-L102">5&ndash;102</a></td></tr><tr><td colspan="5"><b>app/services</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py">auth_service.py</a></td><td>150</td><td>124</td><td>17%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L39-L41">39&ndash;41</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L45-L67">45&ndash;67</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L71-L81">71&ndash;81</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L85-L94">85&ndash;94</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L102-L109">102&ndash;109</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L113-L127">113&ndash;127</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L137-L174">137&ndash;174</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L179-L188">179&ndash;188</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L194-L203">194&ndash;203</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L209-L256">209&ndash;256</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/auth_service.py#L260-L273">260&ndash;273</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_service.py">currency_service.py</a></td><td>49</td><td>35</td><td>29%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_service.py#L33-L62">33&ndash;62</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/currency_service.py#L77-L100">77&ndash;100</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py">openai_service.py</a></td><td>55</td><td>35</td><td>36%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L52-L83">52&ndash;83</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L93">93</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L129-L137">129&ndash;137</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/openai_service.py#L141-L154">141&ndash;154</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py">orchestrator.py</a></td><td>73</td><td>56</td><td>23%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L35-L118">35&ndash;118</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L129-L133">129&ndash;133</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L137">137</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L143-L177">143&ndash;177</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/orchestrator.py#L182-L199">182&ndash;199</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py">qloo_service.py</a></td><td>55</td><td>37</td><td>33%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L36-L72">36&ndash;72</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L95-L129">95&ndash;129</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L141">141</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L166">166</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L186">186</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/qloo_service.py#L212">212</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py">supabase_cache.py</a></td><td>73</td><td>56</td><td>23%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L34-L49">34&ndash;49</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L62-L75">62&ndash;75</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L87-L103">87&ndash;103</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L117-L131">117&ndash;131</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L140-L155">140&ndash;155</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L168-L181">168&ndash;181</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/supabase_cache.py#L190-L194">190&ndash;194</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py">weather_service.py</a></td><td>108</td><td>90</td><td>17%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py#L42-L71">42&ndash;71</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py#L82-L103">82&ndash;103</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py#L115-L174">115&ndash;174</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py#L185-L187">185&ndash;187</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/services/weather_service.py#L201-L267">201&ndash;267</a></td></tr><tr><td colspan="5"><b>app/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py">error_handlers.py</a></td><td>9</td><td>1</td><td>89%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/error_handlers.py#L16">16</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py">rate_limiter.py</a></td><td>51</td><td>33</td><td>35%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py#L34-L36">34&ndash;36</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py#L43-L92">43&ndash;92</a>, <a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/rate_limiter.py#L101-L110">101&ndash;110</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/user_utils.py">user_utils.py</a></td><td>12</td><td>11</td><td>8%</td><td><a href="https://github.com/techgenii/travelstyle/blob/main/app/utils/user_utils.py#L7-L25">7&ndash;25</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1252</b></td><td><b>763</b></td><td><b>39%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

**Made with ❤️ by [TechGenii](https://github.com/techgenii)**
