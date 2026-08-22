# AI Support Agent

An intelligent, evaluation-driven AI Support Agent built to handle customer order tracking, policy inquiries via Retrieval-Augmented Generation (RAG), prompt injection defense, and PII safeguarding.

---

## Architecture & Choices

* **Framework:** Custom Python Agent orchestration using lightweight tool dispatching.
* **LLM Model:** OpenAI `gpt-4o-mini` / Google Gemini (configured via standard API bindings).
* **Embedding Model:** `text-embedding-3-small` (OpenAI) for policy chunk indexing.
* **Storage & Retrieval:** Vector similarity search using **ChromaDB** with dynamic threshold filtering and active policy precedence rules.
* **Tools**:
  * `lookup_order`: Normalizes order formats (e.g., handles lowercase, digit extraction, and prefix stripping) to query mock backend data.
  * `retriever`: Queries policy embeddings with automatic filtering for superseded documentation.

---

## Setup & Local Installation

### Prerequisites
* Python 3.10+
* Git

### Installation from Clean Clone

```powershell
# 1. Clone repository
git clone [https://github.com/ShreyaShukla1608/AI-Agent-Intern-Test.git](https://github.com/ShreyaShukla1608/AI-Agent-Intern-Test.git)
cd AI-Agent-Intern-Test

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env