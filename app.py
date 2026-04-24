import streamlit as st
from openai import OpenAI
import base64

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Silverpush Campaign Analyser",
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
        st.markdown("### 🔐 Silverpush Campaign Analyser")
        st.text_input(
            "Enter password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔐 Silverpush Campaign Analyser")
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

    st.title("📊 Silverpush — Ad Alignment & Suitability Analyser")
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
                    # Read and encode PDF to base64
                    pdf_bytes = uploaded_file.read()
                    pdf_base64 = base64.standard_b64encode(
                        pdf_bytes
                    ).decode("utf-8")

                    # Load system prompt and API key from secrets
                    system_prompt = st.secrets["SYSTEM_PROMPT"]

                    # Initialise OpenAI client
                    client = OpenAI(
                        api_key=st.secrets["OPENAI_API_KEY"]
                    )

                    # Send to GPT-4o with vision
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
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyse this report."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:application/pdf;base64,{pdf_base64}",
                                            "detail": "high"
                                        }
                                    }
                                ]
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
