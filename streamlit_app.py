import streamlit as st
import requests

st.set_page_config(page_title="ReVend AI Assistant", page_icon="♻️")
st.title("📄 Document AI Assistant")

question = st.text_input("Enter your question here:")

if st.button("Get Answer"):
    if question:
        with st.spinner("Analyzing..."):
            try:
                # Backend running on port 10000
                res = requests.post("http://127.0.0.1:10000/ask", json={"question": question})
                
                if res.status_code == 200:
                    data = res.json()
                    
                    # 1. Clean Answer Paragraph
                    st.subheader("Answer")
                    st.write(data["answer"])
                    
                    # 2. Confidence Label
                    st.info(f"Confidence Level: {data['confidence'].upper()}")
                    
                    # 3. Ranked Sources
                    st.subheader("Source Rankings (Most to Least Relatable)")
                    sorted_sources = sorted(data["sources"], key=lambda x: x['score'], reverse=True)
                    
                    for i, s in enumerate(sorted_sources):
                        st.markdown(f"**Rank {i+1}** (Score: `{s['score']}`)")
                        with st.expander(f"Snippet from {s['document']}"):
                            st.caption(s['snippet'])
                else:
                    st.error(f"Backend Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")