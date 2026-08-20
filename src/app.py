import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).parent / "pipeline"))

from rag_chain import answer_query

st.set_page_config(page_title="Vehicle Connect RAG", page_icon="🚗")

st.title("Vehicle Connect RAG")
st.caption(
    "Trace analysis assistant for a connected-vehicle infotainment platform. "
    "Ask about a connect-module problem (bluetooth, wifi, infotainment boot, "
    "cloud sync, navigation, voice assistant)."
)

query = st.text_input(
    "Question",
    placeholder="e.g. why does bluetooth lose signal",
)

if st.button("Ask", type="primary") and query:
    with st.spinner("Retrieving evidence and generating an answer..."):
        result = answer_query(query, synthesize=True)

    st.subheader("Answer")
    st.write(result["answer"])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Resolution path", result["resolution_path"])
    with col2:
        st.metric("Error code", result["error_code"] or "none found")

    if result["doc_chunk"]:
        with st.expander("Documentation evidence"):
            st.markdown(result["doc_chunk"]["text"])

    if result["log_sessions"]:
        with st.expander(f"Log evidence ({len(result['log_sessions'])} session(s))"):
            for session in result["log_sessions"]:
                st.markdown(f"**Session `{session['session_id']}`**")
                for e in session["trace"]:
                    st.text(
                        f"{e['timestamp']}  {e['event_type']:16} "
                        f"{e['severity']:5} {e['message']}"
                    )
    else:
        st.info("No matching log events found for this query.")
