
import streamlit as st
import os
import tempfile
import pandas as pd

from src.extractor import extract_requirements
from src.nlp import (
    classify_with_llm,
    explain_classification,
    score_ambiguity
)
from src.traceability import (
    simulate_traceability_data,
    build_trace_links,
    build_trace_links_llm,
    display_traceability_graph
)

st.set_page_config(page_title="🧠 AI Requirements Assistant", layout="wide")
st.title("🧠 AI-Based Requirements Engineering Assistant")

# === Upload block ===
uploaded_file = st.file_uploader(
    "📤 Upload your requirements file (.docx, .pdf, .txt, .xlsx)",
    type=["docx", "pdf", "txt", "xlsx"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.info(f"📄 Processing file: {uploaded_file.name}")
    
    try:
        requirements = extract_requirements(file_path, uploaded_file.name)

        if not requirements:
            st.warning("⚠️ No requirements found.")
        else:
            st.success(f"✅ Extracted {len(requirements)} requirements.")

            # Create tabbed layout
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔖 Classification", "💬 Explanation", "⚠️ Ambiguity", "🔁 Traceability Matrix"
            ])

            with tab1:
                st.subheader("🔖 Requirement Classification(FR/NFR)")
                data = []
                for req in requirements:
                    data.append({
                        "Requirement": req,
                        "Classification": classify_with_llm(req)
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

            with tab2:
                st.subheader("💬 Explanation for Each Classification")
                expl_data = []
                for req in requirements:
                    label = classify_with_llm(req)
                    explanation = explain_classification(req)
                    expl_data.append({
                        "Requirement": req,
                        "Classification": label,
                        "Explanation": explanation
                    })
                df2 = pd.DataFrame(expl_data)
                st.dataframe(df2, use_container_width=True)

            with tab3:
                st.subheader("⚠️ Ambiguity Detection")
                amb_data = []
                for req in requirements:
                    amb = score_ambiguity(req)
                    amb_data.append({
                        "Requirement": req,
                        "Keyword Matches": ", ".join(amb["vague_terms"]),
                        "Heuristic Score": amb["keyword_score"],
                        "LLM Score (0-10)": amb["llm_score"]
                    })
                df3 = pd.DataFrame(amb_data)
                st.dataframe(df3, use_container_width=True)

        with tab4:
                st.subheader("🔁 Traceability Matrix from Uploaded Files")

                st.markdown("""
                Upload 3 Excel files below:
                - 🧑‍💼 Stakeholder Requirements (ID, Description)
                - ⚙️ System Requirements (ID, Description)
                - 🧪 Test Cases (ID, Description)
                """)

                col1, col2, col3 = st.columns(3)
                with col1:
                    stakeholder_file = st.file_uploader("🧑‍💼 Stakeholder Reqs", type=["xlsx"], key="sr")
                with col2:
                    system_file = st.file_uploader("⚙️ System Reqs", type=["xlsx"], key="sysr")
                with col3:
                    test_file = st.file_uploader("🧪 Test Cases", type=["xlsx"], key="tc")

                if stakeholder_file and system_file and test_file:
                    sr_df = pd.read_excel(stakeholder_file)
                    sysr_df = pd.read_excel(system_file)
                    tc_df = pd.read_excel(test_file)

                    st.success("✅ All files uploaded!")

                    st.write("📋 Stakeholder Requirements")
                    st.dataframe(sr_df, use_container_width=True)

                    st.write("⚙️ System Requirements")
                    st.dataframe(sysr_df, use_container_width=True)

                    st.write("🧪 Test Cases")
                    st.dataframe(tc_df, use_container_width=True)

                    use_llm = st.checkbox("🧠 Use LLM for smarter linking (slower)", value=False)

                    if st.button("🔗 Generate Traceability Matrix"):
                        with st.spinner("🔗 Generating traceability links..."):
                            if use_llm:
                                matrix_df = build_trace_links_llm(sr_df, sysr_df, tc_df)
                            else:
                                matrix_df = build_trace_links(sr_df, sysr_df, tc_df)

                        st.success("✅ Traceability Matrix Created!")
                        st.dataframe(matrix_df, use_container_width=True)

                        with st.expander("🕸️ Show Traceability Graph"):
                            display_traceability_graph(matrix_df)

                        export_format = st.radio("📤 Export format", ["None", "CSV", "Excel"])
                        if export_format == "CSV":
                            csv = matrix_df.to_csv(index=False).encode('utf-8')
                            st.download_button("⬇️ Download CSV", csv, file_name="traceability_matrix.csv")
                        elif export_format == "Excel":
                            excel_path = os.path.join(tempfile.gettempdir(), "full_traceability_export.xlsx")
                            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                                sr_df.to_excel(writer, sheet_name="Stakeholder Reqs", index=False)
                                sysr_df.to_excel(writer, sheet_name="System Reqs", index=False)
                                tc_df.to_excel(writer, sheet_name="Test Cases", index=False)
                                matrix_df.to_excel(writer, sheet_name="Traceability Matrix", index=False)
                            with open(excel_path, "rb") as f:
                                st.download_button("⬇️ Download Excel", f, file_name="full_traceability_export.xlsx")
                else:
                    st.info("📥 Please upload all three Excel files to generate the traceability matrix.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
