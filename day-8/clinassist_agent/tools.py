# clinassist_agent/tools.py
# Tools for ClinAssist v0.1.
# Note: RAG pipeline is added on Day 9. Today the tool returns
# structured general information based on symptom keywords only.


# def lookup_symptoms(query: str) -> dict:
#     """Looks up general health information for a reported symptom or set of symptoms.

#     Use this when the user describes physical or mental health symptoms and
#     wants general information. This tool does NOT diagnose conditions. It
#     returns publicly available health education information only.

#     Args:
#         query: A description of the symptom(s) reported by the user.

#     Returns:
#         A dict with 'status' and 'data' containing general information,
#         or 'error_message' on failure.
#     """
#     if not query or not query.strip():
#         return {
#             "status": "error",
#             "error_message": "Query cannot be empty.",
#         }

#     # Placeholder: on Day 9 this will call a RAG retrieval pipeline.
#     # Today it returns a structured stub so the pipeline runs end-to-end.
#     return {
#         "status": "success",
#         "data": {
#             "query": query,
#             "general_info": (
#                 f"General information retrieved for: '{query}'. "
#                 "This is a placeholder response. On Day 9, this will "
#                 "be replaced by RAG-retrieved evidence from a medical "
#                 "knowledge base with source citations."
#             ),
#             "when_to_seek_care": (
#                 "Seek immediate medical attention if symptoms are severe, "
#                 "sudden, or accompanied by chest pain, difficulty breathing, "
#                 "loss of consciousness, or severe allergic reaction."
#             ),
#             "source": "placeholder --- RAG pipeline added Day 9",
#         },
#     }

# In clinassist_agent/tools.py
# Replace the stub lookup_symptoms with this RAG-backed version.
# Everything else in tools.py (record_confirmation, record_rejection)
# stays unchanged.

# from .rag import build_index, retrieve

# Build/load the index when the module is first imported.
# This is fast if the index already exists on disk.
# build_index()


def lookup_symptoms(query: str) -> dict:
    """Retrieves relevant general health information for a reported symptom or

    set of symptoms from the local knowledge base. Use this when the user
    describes physical or mental health symptoms and wants general information.
    This tool does NOT diagnose conditions. It returns evidence from curated
    health education documents with source citations.

    Args:
        query: A description of the symptom(s) reported by the user.

    Returns:
        A dict with 'status' and 'data' containing retrieved evidence
        and citations, or 'error_message' on failure.
    """
    
    from .rag import build_index, retrieve   # lazy import — breaks the cycle
    build_index()
    
    if not query or not query.strip():
        return {"status": "error", "error_message": "Query cannot be empty."}

    try:
        results = retrieve(query)
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

    if not results:
        return {
            "status": "error",
            "error_message": (
                "No relevant information found in the knowledge base for this query. "
                "Please consult a healthcare professional."
            ),
        }

    # Format retrieved chunks with source citations
    evidence_blocks = []
    for i, r in enumerate(results, 1):
        evidence_blocks.append(
            f"[Source {i}: {r['source']} | relevance: {r['score']}]\n{r['text']}"
        )

    return {
        "status": "success",
        "data": {
            "query": query,
            "evidence": evidence_blocks,
            "sources": [r["source"] for r in results],
            "when_to_seek_care": (
                "Seek immediate medical attention if symptoms are severe, sudden, "
                "or accompanied by chest pain, difficulty breathing, loss of consciousness, "
                "or severe allergic reaction."
            ),
        },
    }

# In tools.py --- add these alongside lookup_symptoms

from google.adk.tools.tool_context import ToolContext

def record_confirmation(tool_context: ToolContext) -> dict:
    """
    Records human approval in session state. Call this when the
    user sends 'confirm' to approve the triage draft.
    """
    tool_context.state["user:confirmed"] = True
    return {"status": "confirmed"}


def record_rejection(tool_context: ToolContext) -> dict:
    """
    Records human rejection in session state. Call this when the
    user sends 'reject' to discard the triage draft.
    """
    tool_context.state["user:confirmed"] = False
    tool_context.state["triage_draft"] = ""
    return {"status": "rejected"}