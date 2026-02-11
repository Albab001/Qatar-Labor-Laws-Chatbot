# 🇶🇦 Qatar Labor Laws AI Assistant

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-yellow)](https://huggingface.co/spaces/albab0001/Qatar_labor_MVP)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Albab001/Qatar-Labor-Laws-Chatbot)

An intelligent bilingual chatbot that provides accurate answers to Qatar labor law questions using RAG (Retrieval-Augmented Generation) architecture. Built with n8n workflow automation, Supabase vector storage, and Cohere embeddings.

## 🎯 Problem Statement

Navigating Qatar's labor laws can be complex for employees, employers, and HR professionals. This AI assistant makes legal information instantly accessible by:
- Providing precise answers from official Qatar labor law documents
- Supporting both Arabic and English queries
- Maintaining conversation context for follow-up questions
- Restricting responses strictly to labor law topics (prevents hallucination)

## ✨ Key Features

- **📚 Comprehensive Coverage**: Trained on complete Qatar labor law PDFs from official government sources
- **🌍 Bilingual Support**: Handles queries in both Arabic and English
- **🎯 Context-Aware**: Maintains conversation history for natural follow-up questions
- **✅ Accurate & Grounded**: Only answers labor law questions, explicitly states when information isn't available
- **⚡ Real-Time**: Instant responses with source-grounded answers

## 🏗️ Architecture

This project showcases a production-grade RAG pipeline with workflow automation:

```
Official Qatar Labor PDFs
        ↓
   n8n Workflow (Document Processing)
        ↓
   Cohere Embeddings
        ↓
   Supabase Vector Store
        ↓
   MCP Server (Orchestration)
        ↓
   AI Agent (Query Processing)
        ↓
   Gradio Interface
```

### Technical Stack

**Backend & Orchestration:**
- **n8n**: Workflow automation for document ingestion and processing
- **Supabase**: PostgreSQL with pgvector for semantic search
- **Cohere**: Enterprise-grade embeddings for Arabic/English
- **MCP (Model Context Protocol)**: Server orchestration layer

**AI & Interface:**
- **LangChain**: RAG pipeline orchestration
- **Gradio**: Interactive web interface
- **Python**: Core application logic

## 🚀 Live Demo

**Try it now:** [https://huggingface.co/spaces/albab0001/Qatar_labor_MVP](https://huggingface.co/spaces/albab0001/Qatar_labor_MVP)

### Example Questions:
- "What are the standard working hours in Qatar?" / "ما هي ساعات العمل القياسية في قطر؟"
- "Explain annual leave entitlement under Qatar Labour Law"
- "What are workers' rights in Qatar?" / "ما هي حقوق العاملين في قطر؟"

## 📸 Screenshots

### Bilingual Interface
![Chatbot Interface](https://raw.githubusercontent.com/Albab001/Qatar-Labor-Laws-Chatbot/main/screenshots/interface.png)

*Arabic interface with example questions and chat history*

### Example Query
![Example Interaction](https://raw.githubusercontent.com/Albab001/Qatar-Labor-Laws-Chatbot/main/screenshots/example.png)

*Answering labor law questions with context awareness*

## 🛠️ Local Setup

### Prerequisites
```bash
Python 3.9+
n8n instance (local or cloud)
Supabase account
Cohere API key
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Albab001/Qatar-Labor-Laws-Chatbot.git
cd Qatar-Labor-Laws-Chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - COHERE_API_KEY
# - N8N_WEBHOOK_URL
```

4. **Run the application**
```bash
python app.py
```

Access the interface at `http://localhost:7860`

## 🔧 How It Works

### 1. Document Processing (n8n Workflow)
- Fetches official Qatar labor law PDFs from government website
- Chunks documents into semantic segments
- Generates Cohere embeddings for each chunk
- Stores in Supabase vector database with metadata

### 2. Query Processing
- User submits question in Arabic or English
- Query is embedded using Cohere
- Vector similarity search retrieves relevant law sections
- AI agent generates answer using only retrieved context
- Returns response with chat history support

### 3. Safeguards
- Strict scope limiting (only answers labor law questions)
- Source attribution to prevent hallucination
- "I don't know" responses when information isn't in the database

## 📊 Project Structure

```
Qatar-Labor-Laws-Chatbot/
├── app.py                 # Main Gradio application
├── workflows/
│   ├── document_processor.json    # n8n document ingestion workflow
│   └── mcp_server.json           # MCP orchestration workflow
├── requirements.txt
├── .env.example
└── README.md
```

## 🎓 Key Learnings & Skills Demonstrated

- **RAG Implementation**: Production-grade retrieval-augmented generation
- **Workflow Automation**: Complex n8n workflows for document processing
- **Vector Databases**: Supabase/pgvector for semantic search
- **Multilingual NLP**: Handling Arabic and English with Cohere embeddings
- **MCP Integration**: Modern AI orchestration patterns
- **UI/UX**: Clean, bilingual Gradio interface

## 🚧 Current Limitations & Future Enhancements

**Current Scope:**
- Only answers questions directly related to Qatar labor laws
- Requires exact or closely related queries to retrieve accurate information

**Planned Improvements:**
- [ ] Add citation of specific law articles in responses
- [ ] Expand to other GCC country labor laws
- [ ] Implement query reformulation for better retrieval
- [ ] Add PDF export of chat conversations
- [ ] Build FastAPI backend for production deployment

## 📝 Use Cases

- **Employees**: Understand rights, leave policies, termination rules
- **Employers**: Quick reference for compliance requirements
- **HR Professionals**: Instant access to labor regulations
- **Legal Consultants**: Fast fact-checking tool

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional language support (Urdu, Hindi, Tagalog)
- Enhanced retrieval strategies
- Mobile-responsive interface improvements

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

**Your Name**
- GitHub: [@Albab001](https://github.com/Albab001)


## 🙏 Acknowledgments

- Qatar Ministry of Labour for official documentation
- Cohere for multilingual embedding support
- n8n community for workflow automation patterns

---

⭐ **Star this repo if you find it helpful!**

**Live Demo:** [https://huggingface.co/spaces/albab0001/Qatar_labor_MVP](https://huggingface.co/spaces/albab0001/Qatar_labor_MVP)
