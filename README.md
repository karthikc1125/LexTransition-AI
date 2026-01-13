# LexTransition-AI
LexTransition AI is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new **BNS/BNSS/BSA** frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.
# ⚖️ LexTransition AI: Law Mapper & Document Analyzer

**LexTransition AI** is an open-source, offline-first legal assistant. It helps users navigate the transition from old Indian laws (IPC/CrPC/IEA) to the new **BNS/BNSS/BSA** frameworks. Using local Machine Learning and OCR, it analyzes legal documents and maps law sections with 100% grounded accuracy.

---

## 🚀 Key Modules

* **🔄 The Law Transition Mapper:** The core engine that maps old IPC sections to new BNS equivalents. It highlights specific changes in wording, penalties, and scope.
* **🖼️ Multimodal Document Analysis (OCR):** Upload photos of legal notices or FIRs. The system extracts text using local OCR and explains "action items" in simple language.
* **📚 Grounded Fact-Checking:** Every response is backed by official citations. The AI identifies the exact Section, Chapter, and Page from the official Law PDFs to prevent hallucinations.

---

## 🛠️ Offline Tech Stack (No-API Approach)

To ensure privacy and offline accessibility, this project can be configured to run without external APIs:

* **Backend:** Python, LangChain/LlamaIndex.
* **OCR:** `EasyOCR` or `PyTesseract` (Local engines).
* **Vector DB:** `ChromaDB` or `FAISS` (Local storage instead of Pinecone/Milvus).
* **Local LLM:** `Llama 3` or `Mistral` via **Ollama** or **LM Studio** (Runs on your GPU/CPU).
* **Frontend:** Streamlit Dashboard.

---

## 📂 Project Structure

```text
LexTransition-AI/
├── app.py                 # Streamlit UI
├── requirements.txt       # Local ML libraries
├── engine/
│   ├── ocr_processor.py   # Local OCR logic
│   ├── mapping_logic.py   # IPC to BNS mapping dictionary
│   └── rag_engine.py      # Local Vector Search logic
└── models/                # Local LLM weights (Quantized)
```
⚙️ Installation & Local Setup
1.Clone the repo
2.Install Local Dependencies
