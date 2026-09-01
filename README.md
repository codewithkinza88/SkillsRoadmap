# 🗺️ Skills Roadmap

AI-powered personalized learning roadmap generator built with **Gradio + Groq**.

## Run locally

```bash
pip install -r requirements.txt
```

Set `GROQ_API_KEY` as an environment variable, then:

```bash
python app.py
```

## Hugging Face Spaces

Create a Gradio Space, upload `app.py` and `requirements.txt`, then add `GROQ_API_KEY` under Space Settings → Secrets. Never commit the real API key to GitHub.
