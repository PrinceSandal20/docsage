from app.services import llm_client


def answer_question(question: str, relevant_chunks: list[str]) -> str:
    context = "\n---\n".join(relevant_chunks)

    prompt = f"""You are a helpful assistant answering questions about a document.

Use ONLY the excerpts below to answer. If the answer isn't in the excerpts,
say so honestly instead of guessing.

DOCUMENT EXCERPTS:
{context}

QUESTION:
{question}

ANSWER:"""

    return llm_client.complete_text(prompt, temperature=0.3)