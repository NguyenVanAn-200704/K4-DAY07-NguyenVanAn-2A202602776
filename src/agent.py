from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "No relevant information found."
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "No relevant information found."
        context_parts = []
        for idx, r in enumerate(results, 1):
            source = r.get("metadata", {}).get("source", f"Chunk {idx}")
            context_parts.append(f"[{idx}] (Source: {source})\n{r['content']}")
        context_str = "\n\n".join(context_parts)
        prompt = (
            "You are an assistant answering questions based on the provided context.\n"
            "Answer the question using only the context below. If the context does not contain "
            "the answer, state that you cannot find the answer.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
