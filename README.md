# AI Support Desk

A small Python script that sends customer support tickets to an LLM (via Groq) and gets back structured JSON with a category, urgency and suggested action. At the end it prints a summary of ticket counts by category and urgency.

## How to run

1. Install the packages:
   ```
   pip install -r requirements.txt
   ```
2. Get a free API key from console.groq.com.
3. Copy `.env.example` to `.env` and put your key in it:
   ```
   GROQ_API_KEY=your_key_here
   ```
4. Run the script:
   ```
   python support_desk.py
   ```

The results are saved in the `results/` folder (`results.json` and `summary.txt`).

## Files

- `support_desk.py` - the main script
- `tickets.json` - 7 sample support tickets
- `results/` - output from my run
- `OBSTACLE_LOG.md` - problems I ran into and how I fixed them
- `.env.example` - example of the .env file (the real `.env` is not committed)

## Notes

- Model used: `openai/gpt-oss-20b` on Groq. If Groq retires it, change the `MODEL` line at the top of the script.
- If a ticket fails (API error or bad JSON), the script skips it and keeps going.
- Never commit your real `.env` file.
