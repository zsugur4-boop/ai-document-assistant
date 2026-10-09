import streamlit as st
from pypdf import PdfReader
from anthropic import Anthropic
from io import BytesIO

st.set_page_config(page_title="AI Document Assistant", page_icon="📄")
st.title("📄 AI Document Assistant")
st.write("Upload a PDF, read its contents, and summarize it with Claude AI.")

with st.sidebar:
    st.header("Claude AI")
    api_key = st.text_input("Anthropic API key", type="password")
    st.caption("Your API key is not stored in this app.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file:
    try:
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = [page.extract_text() or "" for page in reader.pages]
        document_text = "\n".join(pages)

        st.success(f"PDF loaded: {len(pages)} pages")

        with st.expander("View extracted text"):
            st.text(document_text[:15000] or "No readable text found.")

        if not document_text.strip():
            st.warning("This PDF has no extractable text. Scanned PDFs need OCR.")
        elif st.button("Summarize with Claude", type="primary"):
            if not api_key:
                st.error("Enter your Anthropic API key in the sidebar.")
            else:
                try:
                    with st.spinner("Claude is summarizing your document..."):
                        client = Anthropic(api_key=api_key)
                        response = client.messages.create(
                            model="claude-haiku-4-5",
                            max_tokens=1500,
                            messages=[{
                                "role": "user",
                                "content": (
                                    "Summarize this document in simple English. "
                                    "List the key points and important dates or amounts. "
                                    "If the document is incomplete, say so.\n\n"
                                    + document_text[:100000]
                                )
                            }]
                        )
                        summary = "\n".join(
                            block.text for block in response.content
                            if block.type == "text"
                        )
                    st.subheader("Document Summary")
                    st.write(summary)
                    st.download_button(
                        "Download summary",
                        summary,
                        file_name="document_summary.txt"
                    )
                except Exception as error:
                    st.error(f"Request failed: {error}")
    except Exception as error:
        st.error(f"Could not read this PDF: {error}")

st.divider()
st.caption("Prototype version. API usage may incur charges.")
