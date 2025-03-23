
import pandas as pd
from difflib import SequenceMatcher
from langchain_community.llms import LlamaCpp
import os
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

# Load local model
model_path = os.path.abspath("models/mistral-7b-instruct-v0.1.Q4_K_M.gguf")
llm = LlamaCpp(
    model_path=model_path,
    n_ctx=2048,
    temperature=0.1,
    max_tokens=64,
    top_p=0.9,
    n_gpu_layers=0,
    verbose=False
)

def simulate_traceability_data():
    stakeholder_reqs = pd.DataFrame({
        "SR_ID": ["SR-001", "SR-002", "SR-003"],
        "Description": [
            "The system shall be user-friendly and accessible.",
            "The system shall ensure secure user authentication.",
            "The system shall respond to input within 1 second."
        ]
    })

    system_reqs = pd.DataFrame({
        "SYSR_ID": ["SYSR-001", "SYSR-002", "SYSR-003", "SYSR-004"],
        "Description": [
            "UI shall support accessibility features and intuitive navigation.",
            "User login shall use two-factor authentication.",
            "System shall encrypt data in transit and at rest.",
            "System must process sensor input within 1000 milliseconds."
        ]
    })

    test_cases = pd.DataFrame({
        "TC_ID": ["TC-001", "TC-002", "TC-003", "TC-004"],
        "Description": [
            "Test if UI navigation supports accessibility.",
            "Test if login process requires 2FA.",
            "Check system response time under load.",
            "Verify data is encrypted while being transmitted."
        ]
    })

    return stakeholder_reqs, system_reqs, test_cases

def compute_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def build_trace_links(sr_df, sysr_df, tc_df, threshold=0.3):
    trace_links = []
    for _, sr in sr_df.iterrows():
        sr_id = sr.iloc[0]
        sr_text = sr.iloc[1]
        linked_sysrs, linked_tcs = [], []
        for _, sysr in sysr_df.iterrows():
            if compute_similarity(sr_text, sysr.iloc[1]) >= threshold:
                linked_sysrs.append(sysr.iloc[0])
        for _, tc in tc_df.iterrows():
            if compute_similarity(sr_text, tc.iloc[1]) >= threshold:
                linked_tcs.append(tc.iloc[0])
        trace_links.append({
            "Stakeholder Requirement": sr_id,
            "System Requirements": ", ".join(linked_sysrs),
            "Test Cases": ", ".join(linked_tcs)
        })
    return pd.DataFrame(trace_links)

def llm_predict_link(req_text, candidate_text, level="system") -> bool:
    prompt = f"""
You are an expert systems engineer helping to trace requirements.

Determine if the following {'system requirement' if level=='system' else 'test case'} is related to the stakeholder requirement.

Stakeholder Requirement:
"{req_text}"

Candidate {'System Requirement' if level=='system' else 'Test Case'}:
"{candidate_text}"

Answer YES or NO only.
"""
    response = llm.invoke(prompt).strip().lower()
    return "yes" in response

def explain_link(sr_text, candidate_text):
    prompt = f"""
Explain briefly why the following candidate is related to the stakeholder requirement.

Stakeholder Requirement:
"{sr_text}"

Candidate:
"{candidate_text}"

Explanation (1-2 sentences):
"""
    try:
        return llm.invoke(prompt).strip()
    except:
        return "⚠️ No explanation returned."

def build_trace_links_llm(sr_df, sysr_df, tc_df):
    trace_links = []
    total = len(sr_df) * (len(sysr_df) + len(tc_df))
    count = 0
    progress = st.progress(0, text="🔗 Linking requirements using LLM...")
    for _, sr in sr_df.iterrows():
        sr_id = sr.iloc[0]
        sr_text = sr.iloc[1]
        linked_sysrs, linked_tcs, explanations = [], [], []
        for _, sysr in sysr_df.iterrows():
            if llm_predict_link(sr_text, sysr.iloc[1], level="system"):
                linked_sysrs.append(sysr.iloc[0])
                explanations.append(f"✔️ SYSR `{sysr.iloc[0]}` linked: {explain_link(sr_text, sysr.iloc[1])}")
            count += 1
            progress.progress(min(count / total, 1.0), text=f"Processing SYSRs... ({count}/{total})")
        for _, tc in tc_df.iterrows():
            if llm_predict_link(sr_text, tc.iloc[1], level="test"):
                linked_tcs.append(tc.iloc[0])
                explanations.append(f"🧪 TC `{tc.iloc[0]}` linked: {explain_link(sr_text, tc.iloc[1])}")
            count += 1
            progress.progress(min(count / total, 1.0), text=f"Processing TCs... ({count}/{total})")
        trace_links.append({
            "Stakeholder Requirement": sr_id,
            "System Requirements": ", ".join(linked_sysrs),
            "Test Cases": ", ".join(linked_tcs),
            "LLM Explanation": "\\n".join(explanations)
        })
    progress.empty()
    return pd.DataFrame(trace_links)

def display_traceability_graph(matrix_df):
    net = Network(height="600px", width="100%", directed=True)
    for _, row in matrix_df.iterrows():
        sr = row["Stakeholder Requirement"]
        sysrs = row["System Requirements"].split(", ")
        tcs = row["Test Cases"].split(", ")
        net.add_node(sr, label=sr, color="#ffd700", title="Stakeholder Requirement")
        for sysr in sysrs:
            if sysr.strip():
                net.add_node(sysr, label=sysr, color="#90ee90", title="System Requirement")
                net.add_edge(sr, sysr)
        for tc in tcs:
            if tc.strip():
                net.add_node(tc, label=tc, color="#87cefa", title="Test Case")
                for sysr in sysrs:
                    if sysr.strip():
                        net.add_edge(sysr, tc)
    net.repulsion(node_distance=200, spring_length=200)
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.show(path)
    components.html(open(path, "r", encoding="utf-8").read(), height=600, scrolling=True)
