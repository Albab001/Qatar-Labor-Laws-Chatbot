# Quick Setup Guide

## For Recruiters & Evaluators

**Want to see it in action?** Just visit the live demo:
👉 [https://huggingface.co/spaces/albab0001/Qatar_labor_MVP](https://huggingface.co/spaces/albab0001/Qatar_labor_MVP)

No installation needed!

## For Developers

### Minimum Setup (5 minutes)

If you want to run this locally:

1. **Clone and install:**
```bash
git clone https://github.com/Albab001/Qatar-Labor-Laws-Chatbot.git
cd Qatar-Labor-Laws-Chatbot
pip install -r requirements.txt
```

2. **Get API keys:**
- Supabase: Sign up at [supabase.com](https://supabase.com)
- Cohere: Get free API key at [cohere.com](https://cohere.com)
- n8n: Self-host or use [n8n.cloud](https://n8n.cloud)

3. **Configure:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run:**
```bash
python app.py
```

### Full Production Setup

For complete implementation including the n8n workflows:

1. Import the n8n workflows from `/workflows/` directory
2. Configure the workflows with your Supabase credentials
3. Set up the MCP server workflow
4. Point the Gradio app to your MCP webhook URL

Detailed instructions in `/docs/PRODUCTION_SETUP.md`

## Architecture Overview

```
Qatar Government PDF → n8n → Cohere Embeddings → Supabase → MCP → Gradio UI
```

### What Each Component Does:

- **n8n**: Automatically fetches and processes labor law PDFs
- **Cohere**: Creates semantic embeddings (supports Arabic)
- **Supabase**: Stores embeddings for fast similarity search
- **MCP**: Orchestrates the RAG pipeline
- **Gradio**: Provides the user interface

## Questions?

Open an issue or reach out on LinkedIn!
