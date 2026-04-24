import streamlit as st
from openai import OpenAI
import fitz  # pymupdf

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="YT-Audit",
    page_icon="📊",
    layout="wide"
)

# ── Password protection ───────────────────────────────────
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔐 YT-Audit")
        st.text_input(
            "Enter password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔐 YT-Audit")
        st.text_input(
            "Enter password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("Incorrect password. Please try again.")
        return False
    else:
        return True


# ── Main app ──────────────────────────────────────────────
if check_password():

    st.title("📊 YT-Audit — Ad Alignment & Suitability Analyser")
    st.markdown(
        "Upload the campaign PDF report and click **Analyse Report** "
        "to get the full structured analysis."
    )
    st.markdown("---")

    # ── File uploader ─────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload Campaign Report PDF",
        type="pdf",
        help="Upload the Looker Studio exported PDF report"
    )

    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyse_button = st.button(
                "🔍 Analyse Report",
                type="primary",
                use_container_width=True
            )

        if analyse_button:

            with st.spinner(
                "Analysing report... this may take 30–60 seconds"
            ):

                try:
                    # Extract text from each PDF page
                    pdf_bytes = uploaded_file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    report_text = ""
                    for i, page in enumerate(doc, start=1):
                        report_text += f"\n\n--- SLIDE {i} ---\n"
                        report_text += page.get_text()
                    doc.close()

                    # Load system prompt from file
                    with open("prompt.txt", "r", encoding="utf-8") as f:
                        system_prompt = f.read()

                    # Initialise OpenAI client
                    client = OpenAI(
                        api_key=st.secrets["OPENAI_API_KEY"]
                    )

                    # Send extracted text to GPT-4o
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        max_tokens=4000,
                        messages=[
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": f"Here is the full text content extracted from the YouTube campaign audit PDF report, slide by slide. Analyse it and produce the full structured output exactly as instructed.\n\n{report_text}"
                            }
                        ]
                    )

                    analysis = response.choices[0].message.content

                    # ── Display output ────────────────────
                    st.markdown("---")
                    st.subheader("📋 Analysis Output")
                    st.markdown(analysis)
                    st.markdown("---")

                    # ── Download button ───────────────────
                    st.download_button(
                        label="⬇️ Download Analysis",
                        data=analysis,
                        file_name=f"analysis_{uploaded_file.name}.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
                    st.info(
                        "Please check your API key in secrets "
                        "and try again."
                    )
