# Obstacle Log

**1. No Anthropic API key.**
I didn't have a key for the first SDK I tried, so I switched to Groq, which has a free tier. I changed the client code, the `.env` variable name (`GROQ_API_KEY`) and requirements.txt.

**2. Model not found (404).**
My first run failed on every ticket with `model_not_found` for `llama-3.3-70b-versatile`. Groq had retired it. I checked Groq's supported models page and switched to `openai/gpt-oss-20b`. I also raised `max_tokens` to 1000 because this model does some reasoning before it answers.

**3. Script kept running when the API failed.**
Because each ticket is wrapped in try/except, the 404 errors didn't crash the script. It skipped each ticket, printed the error, and still made a summary. This showed me the error handling works.

**4. Making sure the output is usable.**
The model could return text that isn't valid JSON, a made-up category, or a missing key. The prompt lists the exact JSON format and allowed values. After parsing, the code checks the keys and values and raises an error if anything is wrong. It also strips ``` fences in case the model adds them.

**5. Keeping the API key safe.**
The key is in a `.env` file loaded with python-dotenv. `.env` is in `.gitignore`, and I only commit `.env.example` with a fake placeholder.
