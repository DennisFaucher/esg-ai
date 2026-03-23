# ESG AI Search

A web app that researches any company's **Environmental, Social, and Governance (ESG)** efforts using Perplexity AI, then cross-checks the results for accuracy using Claude. (NB: Claude helped me write this)

<img width="881" height="933" alt="image" src="https://github.com/user-attachments/assets/280ba194-b497-4eff-a55f-a99de657d833" />


## How It Works

1. Enter a company name in the search box
2. **Perplexity** searches the web for the company's ESG initiatives, ratings, and commitments
3. **Claude** reviews the Perplexity results and provides an accuracy assessment — highlighting what's credible, what's questionable, and what may be missing
4. Both results are displayed side-by-side with source citations

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A [Perplexity API key](https://www.perplexity.ai/settings/api)
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DennisFaucher/esg-ai.git
   cd esg-ai
   ```

2. **Configure your API keys**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your keys:
   ```
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Build and run**
   ```bash
   docker-compose up --build
   ```

4. **Open the app**
   Navigate to [http://localhost:5000](http://localhost:5000)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| ESG Research | Perplexity API (`sonar` model) |
| Accuracy Check | Anthropic Claude (`claude-opus-4-6`) |
| Serving | Gunicorn |
| Deployment | Docker / Docker Compose |

## Project Structure

```
esg-ai/
├── app.py               # Flask backend & API integrations
├── templates/
│   └── index.html       # Frontend UI
├── requirements.txt     # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── .env.example         # API key template
```
