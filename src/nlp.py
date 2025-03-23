from langchain_community.llms import LlamaCpp
import os

model_path = os.path.abspath("models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")

llm = LlamaCpp(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.1,
    max_tokens=128,
    top_p=0.9,
    n_gpu_layers=0,
    verbose=False
)

# 🔖 Basic requirement classification
def classify_with_llm(requirement: str) -> str:
    prompt = f"""
You are a Requirements Classification Assistant.
Classify the following requirement as one of:
- Functional
- Non-Functional
- Ambiguous

Requirement: "{requirement}"

Only respond with one label.
"""
    return llm.invoke(prompt).strip()

# 💬 Explanation of the classification
def explain_classification(requirement: str) -> str:
    prompt = f"""
You are a requirements expert.

Explain why the following requirement is categorized the way it is.
Include keywords, clarity, and purpose in your reasoning.

Requirement: "{requirement}"

Explanation:
"""
    return llm.invoke(prompt).strip()

# 🤖 Ambiguity detection (simple + LLM-enhanced)
def score_ambiguity(requirement: str) -> dict:
    # Simple keyword-based heuristics
    vague_terms = ["should", "could", "may", "might", "as soon as possible", "etc", "user-friendly"]
    score = 0
    found = []

    for term in vague_terms:
        if term.lower() in requirement.lower():
            score += 1
            found.append(term)

    # Optional: Add LLM scoring (you can disable if slow)
    prompt = f"""
Rate how ambiguous this requirement is on a scale of 0 to 10.
Ambiguous means unclear, open to interpretation, or vague.

Requirement: "{requirement}"

Just give the number.
"""
    try:
        llm_score = llm.invoke(prompt).strip()
        llm_score = int(''.join(filter(str.isdigit, llm_score))[:2])  # clean numeric output
    except:
        llm_score = None

    return {
        "vague_terms": found,
        "keyword_score": score,
        "llm_score": llm_score
    }
