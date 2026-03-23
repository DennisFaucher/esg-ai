import os
import json
import requests
import anthropic
from flask import Flask, render_template, request, Response, stream_with_context

app = Flask(__name__)

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def search_perplexity(company: str) -> dict:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an ESG research assistant. Provide detailed, factual information "
                    "about a company's Environmental, Social, and Governance (ESG) efforts, "
                    "initiatives, ratings, and commitments. Include specific programs, targets, "
                    "certifications, and any notable achievements or controversies."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"What are the known ESG (Environmental, Social, and Governance) efforts, "
                    f"initiatives, and commitments of {company}? Please provide detailed information "
                    f"including environmental programs, social responsibility efforts, governance "
                    f"practices, ESG ratings if available, and any recent sustainability reports."
                ),
            },
        ],
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])
    return {"content": content, "citations": citations}


def check_accuracy_with_claude(company: str, perplexity_content: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": (
                    f"The following is a summary of ESG (Environmental, Social, and Governance) "
                    f"information about {company}, retrieved from an AI search tool:\n\n"
                    f"---\n{perplexity_content}\n---\n\n"
                    f"Please review this information and provide an accuracy assessment. Specifically:\n"
                    f"1. Identify any claims that are likely accurate based on your knowledge\n"
                    f"2. Flag any claims that seem questionable, outdated, or potentially incorrect\n"
                    f"3. Note any important ESG aspects about {company} that may be missing\n"
                    f"4. Give an overall accuracy rating (High / Medium / Low) with a brief justification\n\n"
                    f"Be specific and concise in your assessment."
                ),
            }
        ],
    )
    return message.content[0].text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    company = request.form.get("company", "").strip()
    if not company:
        return Response(
            f"data: {json.dumps({'error': 'Please enter a company name.'})}\n\n",
            content_type="text/event-stream",
        )

    def generate():
        try:
            # Step 1: Perplexity search
            yield f"data: {json.dumps({'step': 'perplexity_start'})}\n\n"
            perplexity_result = search_perplexity(company)
            yield f"data: {json.dumps({'step': 'perplexity_done', 'content': perplexity_result['content'], 'citations': perplexity_result['citations']})}\n\n"

            # Step 2: Claude accuracy check
            yield f"data: {json.dumps({'step': 'claude_start'})}\n\n"
            claude_result = check_accuracy_with_claude(company, perplexity_result["content"])
            yield f"data: {json.dumps({'step': 'claude_done', 'content': claude_result})}\n\n"

            yield f"data: {json.dumps({'step': 'complete'})}\n\n"
        except requests.exceptions.HTTPError as e:
            yield f"data: {json.dumps({'error': f'Perplexity API error: {str(e)}'})}\n\n"
        except anthropic.APIError as e:
            yield f"data: {json.dumps({'error': f'Claude API error: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"

    return Response(stream_with_context(generate()), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
