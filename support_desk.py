import os
import json
from collections import Counter

from groq import Groq, APIError
from dotenv import load_dotenv

# loads GROQ_API_KEY from the .env file
load_dotenv()

MODEL = "openai/gpt-oss-20b"

CATEGORIES = ["billing", "technical", "account", "general_question", "feature_request"]
URGENCIES = ["low", "medium", "high", "critical"]

PROMPT = """You are a support ticket triage tool. Read the ticket and reply with ONLY a JSON object, nothing else (no markdown, no explanation).

The JSON must look exactly like this:
{"category": "...", "urgency": "...", "suggested_action": "..."}

category must be one of: billing, technical, account, general_question, feature_request
urgency must be one of: low, medium, high, critical
suggested_action is one or two sentences saying what the support agent should do next.

Use critical for outages, high for angry customers or wrongly charged money, medium for broken things with a workaround, low for questions and suggestions.
If the ticket is too vague, use medium and make the suggested_action ask the customer for more details."""


def classify(client, ticket):
    message = f"Subject: {ticket['subject']}\n\n{ticket['body']}"
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": message},
        ],
    )
    text = response.choices[0].message.content.strip()

    # sometimes the model wraps the json in ``` fences, so strip them
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]

    data = json.loads(text)

    # make sure we actually got what we asked for
    for key in ["category", "urgency", "suggested_action"]:
        if key not in data:
            raise ValueError(f"missing key: {key}")
    data["category"] = data["category"].lower()
    data["urgency"] = data["urgency"].lower()
    if data["category"] not in CATEGORIES:
        raise ValueError(f"bad category: {data['category']}")
    if data["urgency"] not in URGENCIES:
        raise ValueError(f"bad urgency: {data['urgency']}")
    return data


def main():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("No GROQ_API_KEY found. Put it in a .env file first.")
        return

    client = Groq(api_key=api_key)

    with open("tickets.json") as f:
        tickets = json.load(f)

    results = []
    for ticket in tickets:
        try:
            data = classify(client, ticket)
            results.append({"id": ticket["id"], "subject": ticket["subject"], **data})
            print(f"Ticket {ticket['id']}: {data['category']} / {data['urgency']}")
            print(f"   -> {data['suggested_action']}")
        except json.JSONDecodeError:
            print(f"Ticket {ticket['id']}: model didn't return valid JSON, skipping")
            results.append({"id": ticket["id"], "subject": ticket["subject"], "error": "invalid JSON"})
        except ValueError as e:
            print(f"Ticket {ticket['id']}: unexpected response ({e}), skipping")
            results.append({"id": ticket["id"], "subject": ticket["subject"], "error": str(e)})
        except APIError as e:
            print(f"Ticket {ticket['id']}: API call failed ({e}), skipping")
            results.append({"id": ticket["id"], "subject": ticket["subject"], "error": "API error"})

    # summary
    good = [r for r in results if "error" not in r]
    by_category = Counter(r["category"] for r in good)
    by_urgency = Counter(r["urgency"] for r in good)

    lines = []
    lines.append(f"Tickets processed: {len(results)} ({len(good)} ok, {len(results) - len(good)} failed)")
    lines.append("")
    lines.append("By category:")
    for name, count in by_category.most_common():
        lines.append(f"  {name}: {count}")
    lines.append("")
    lines.append("By urgency:")
    for name in reversed(URGENCIES):
        if by_urgency[name]:
            lines.append(f"  {name}: {by_urgency[name]}")
    summary = "\n".join(lines)

    print("\n" + summary)

    os.makedirs("results", exist_ok=True)
    with open("results/results.json", "w") as f:
        json.dump(results, f, indent=2)
    with open("results/summary.txt", "w") as f:
        f.write(summary)


if __name__ == "__main__":
    main()
