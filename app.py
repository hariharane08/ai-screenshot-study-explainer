import streamlit as st
import boto3
from PIL import Image
import io
import base64
from botocore.exceptions import NoCredentialsError

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Screenshot Explainer",
    page_icon="📸",
    layout="wide"
)

st.title("📸 AI Screenshot Study Explainer")
st.caption("Hackathon Project • AI-powered screenshot study assistant using Amazon Nova")

st.write("Upload a screenshot and Nova AI will explain it.")

# ---------------- SESSION STATE ----------------

if "ai_text" not in st.session_state:
    st.session_state.ai_text = ""

# ---------------- SIDEBAR ----------------

st.sidebar.title("📚 AI Study Explainer")

st.sidebar.write("""
### How to Use
1. Upload a screenshot
2. Select explanation difficulty
3. Click **Analyze Screenshot**
4. Get explanation and study notes
5. Ask follow-up questions
""")

st.sidebar.write("### Supported Images")

st.sidebar.write("""
✔ Notes  
✔ Diagrams  
✔ Code screenshots  
✔ Textbook pages  
""")

st.sidebar.info("Powered by Amazon Nova AI")

# ---------------- DIFFICULTY SELECTOR ----------------

difficulty = st.selectbox(
    "Select Explanation Difficulty",
    ["School Student", "College Student", "Beginner Friendly"]
)

# ---------------- AWS CLIENT ----------------

try:
    client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1"
    )
except Exception:
    client = None

MODEL_ID = "global.amazon.nova-2-lite-v1:0"

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload Screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Screenshot")

    # Convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    with col2:

        if st.button("Analyze Screenshot"):

            with st.spinner("Nova AI is analyzing..."):

                try:

                    message = [{
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": "png",
                                    "source": {
                                        "bytes": img_base64
                                    }
                                }
                            },
                            {
                                "text": f"""
Analyze this screenshot and convert it into clear study material.

Difficulty Level: {difficulty}

Give the output in this format:

1. Simple Explanation
2. Key Points
3. Important Concepts
4. 3 Quiz Questions for revision

Explain clearly for the selected difficulty level.
"""
                            }
                        ]
                    }]

                    response = client.converse(
                        modelId=MODEL_ID,
                        messages=message,
                        inferenceConfig={
                            "maxTokens": 800,
                            "temperature": 0.5
                        }
                    )

                    st.session_state.ai_text = response["output"]["message"]["content"][0]["text"]

                    st.success("Analysis Complete!")

                except NoCredentialsError:

                    st.error("⚠ AWS credentials not configured yet. Run 'aws configure' to connect Nova AI.")

                except Exception as e:

                    st.error("⚠ AI service not available yet. Please configure AWS credentials or try again later.")

# ---------------- OUTPUT ----------------

if st.session_state.ai_text:

    tab1, tab2 = st.tabs(["Explanation", "Study Notes"])

    with tab1:
        st.write(st.session_state.ai_text)

    with tab2:
        st.markdown("### Key Points")
        st.write(st.session_state.ai_text)

    st.download_button(
        "Download Notes",
        st.session_state.ai_text,
        file_name="study_notes.txt"
    )

# ---------------- AI TUTOR ----------------

if st.session_state.ai_text:

    st.divider()

    st.subheader("🤖 AI Tutor")

    question = st.text_input(
        "Ask a follow-up question about the screenshot"
    )

    if st.button("Ask AI") and question:

        with st.spinner("Nova AI is thinking..."):

            try:

                followup_message = [{
                    "role": "user",
                    "content": [
                        {
                            "text": f"""
A student uploaded a screenshot and received the explanation below:

{st.session_state.ai_text}

Now answer this follow-up question clearly:

{question}
"""
                        }
                    ]
                }]

                response = client.converse(
                    modelId=MODEL_ID,
                    messages=followup_message,
                    inferenceConfig={
                        "maxTokens": 500,
                        "temperature": 0.5
                    }
                )

                answer = response["output"]["message"]["content"][0]["text"]

                st.write(answer)

            except NoCredentialsError:

                st.error("⚠ AWS credentials not configured yet.")

            except Exception:

                st.error("⚠ AI tutor unavailable. Configure AWS credentials first.")
