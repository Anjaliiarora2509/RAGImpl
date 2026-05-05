# RAG Interview Questions

## Fundamentals

- What is RAG and why is it used instead of fine-tuning?
- Explain the end-to-end flow of a RAG pipeline.
- What is the difference between parametric and non-parametric knowledge in LLMs?
- What are the limitations of RAG?
- What is chunking and why does chunk size matter?

---

## Retrieval & Embeddings

- What is the difference between dense retrieval and sparse retrieval (BM25)?
- What is hybrid search and how does reciprocal rank fusion work?
- How do you choose an embedding model? What tradeoffs matter?
- What is semantic search vs. keyword search — when does each fail?
- What is a vector database? How does approximate nearest neighbor (ANN) search work (HNSW, FAISS)?
- What is the curse of dimensionality and how does it affect vector search?
- How do you handle queries where the vocabulary doesn't match the document language?

---

## Chunking Strategies

- Fixed-size vs. sentence vs. paragraph chunking — tradeoffs?
- What is chunk overlap and why is it needed?
- What is contextual chunking / parent-child chunking?
- How does chunk size affect retrieval precision vs. context completeness?

---

## Advanced Retrieval

- What is re-ranking and when should you use a cross-encoder vs. bi-encoder?
- What is HyDE (Hypothetical Document Embeddings)?
- What is query expansion and how does it improve recall?
- What is multi-query retrieval?
- What is self-query retrieval / metadata filtering?
- What is RAPTOR or recursive summarization for long documents?

---

## Generation & Prompting

- How do you inject retrieved context into the prompt without exceeding the context window?
- What is the "lost in the middle" problem?
- How do you prevent hallucinations in RAG?
- What is the difference between stuff, map-reduce, and refine strategies for multi-document QA?
- When would you use RAG vs. a long-context model (e.g., Gemini 1M token)?

---

## Evaluation

- How do you evaluate a RAG system end-to-end?
- What are the RAGAS metrics — faithfulness, answer relevance, context recall, context precision?
- What is the difference between retrieval evaluation and generation evaluation?
- How do you build a golden dataset for RAG evaluation?
- How do you diagnose whether a failure is a retrieval failure or a generation failure?

---

## Production & System Design

- How would you design a RAG system for 10 million documents?
- How do you handle incremental document updates without re-embedding everything?
- How do you handle multi-turn conversations in RAG?
- How do you prevent prompt injection through retrieved documents?
- What are the latency bottlenecks in a RAG pipeline and how do you optimize them?
- How do you handle multi-modal RAG (PDFs with images, tables)?
- How do you handle multilingual documents?

---

## Project-Specific

- Why did you use Chroma over Pinecone/Weaviate/FAISS?
- Why `all-MiniLM-L6-v2` — what are its limitations?
- Why Groq / LLaMA — what tradeoffs did you make vs. OpenAI?
- What would you change if this needed to scale to thousands of documents?
- What metrics would you add to know if the pipeline is working well?
