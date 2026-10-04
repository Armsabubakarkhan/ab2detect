# AB2DETECT — Abstract

**Title:** AB2DETECT: A Span-Level Hallucination Detection System for Retrieval-Augmented Generation Pipelines

**Authors:** Abubakar Khan (1RUA24CSE0010), Abhishek D Nagoor (1RUA24CSE0009)

**Institution:** School of Computer Science & Engineering, RV University, Bengaluru

**Guide:** Dr. Ramakrishnan Varadharajan

---

Large Language Models (LLMs) integrated with Retrieval-Augmented Generation (RAG) pipelines frequently generate hallucinations — plausible but factually unsupported claims that erode trust in AI systems. AB2DETECT addresses this by performing span-level token classification on LLM outputs using the ModernBERT encoder (149M parameters, 4K context window, Flash Attention 2). Given a retrieved context, user question, and generated answer, the system assigns binary labels to each answer token (0: supported, 1: hallucinated), groups contiguous hallucinated tokens into spans, and presents results with red-highlight visualization. On the RAGTruth benchmark, AB2DETECT achieves 68.2 span-level F1 — surpassing GPT-4 (61 F1) at 10× lower latency (~150ms) and zero inference cost. The project contributes a domain-gap study on medical QA, an original Cricket dataset with annotated hallucination spans, Kannada-language detection examples, and a production stack comprising a Streamlit web app, FastAPI backend, and Chrome extension.

*(149 words)*
