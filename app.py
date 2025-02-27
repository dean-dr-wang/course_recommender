import streamlit as st
import PyPDF2
import docx
from openai import AzureOpenAI
from io import BytesIO

# Azure OpenAI API Config (Replace with your details)
OPENAI_API_KEY = "5e039b23f6474c2cb5f05e486f3b916f"
OPENAI_API_VERSION = "2024-06-01"
OPENAI_API_BASE = "https://datarobot-genai-enablement.openai.azure.com/"
OPENAI_API_DEPLOYMENT_ID = "gpt-35-turbo-16k"

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_BASE
)

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def extract_text_from_docx(uploaded_file):
    doc = docx.Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_txt(uploaded_file):
    text = uploaded_file.read().decode("utf-8")
    return text

def call_openai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=OPENAI_API_DEPLOYMENT_ID,
            messages=[
                {"role": "system", "content": "You are a helpful career assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in generating response: {str(e)}"

def generate_job_recommendations(profile_text):
    prompt = f"Based on the following professional profile, suggest 3 relevant job roles with short descriptions:\n{profile_text}"
    return call_openai_api(prompt).split("\n")

def generate_training_recommendations(profile_text, aspirations):
    prompt = f"Based on the following profile and career aspirations, suggest 3 relevant courses or trainings for the next 6-12 months:\nProfile: {profile_text}\nAspirations: {aspirations}"
    return call_openai_api(prompt).split("\n")

# Streamlit App
st.title("Professional Training Recommender")

tabs = ["Upload Profile", "Job Recommendations", "Training Recommendations"]
tab1, tab2, tab3 = st.tabs(tabs)

with tab1:
    st.header("Upload Your CV or LinkedIn Profile")
    uploaded_file = st.file_uploader("Upload CV (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"], key="cv_upload")
    linkedin_text = st.text_area("Or paste your LinkedIn profile details manually", key="linkedin_input")
    
    profile_text = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            profile_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            profile_text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "text/plain":
            profile_text = extract_text_from_txt(uploaded_file)
        st.text_area("Extracted Profile Data", profile_text, height=300, key="profile_display")
    
    if linkedin_text:
        profile_text += "\n" + linkedin_text
        st.text_area("Extracted LinkedIn Data", linkedin_text, height=300, key="linkedin_display")

    # Store profile_text in session state for use in other tabs
    st.session_state['profile_text'] = profile_text

with tab2:
    st.header("Job Recommendations")
    profile_text_input = st.text_area("Your Extracted Profile (from Tab 1)", st.session_state.get('profile_text', ''), height=150, key="profile_text_tab2")
    
    if st.button("Generate Job Recommendations"):
        if profile_text_input:
            job_recs = generate_job_recommendations(profile_text_input)
            st.write("### Recommended Jobs")
            for job in job_recs:
                st.write(f"- {job}")
        else:
            st.warning("Please upload a profile or enter LinkedIn details in Tab 1.")
    
    uploaded_job_desc = st.file_uploader("Upload a Job Description (Optional)", type=["pdf", "docx"], key="job_desc_upload")
    aspirations = st.text_area("Or enter your career/lifestyle aspirations", key="aspirations_input")
    
    # Store aspirations in session state for use in Tab 3
    st.session_state['aspirations'] = aspirations

with tab3:
    st.header("Training Recommendations")
    profile_text_input = st.text_area("Your Extracted Profile (from Tab 1)", st.session_state.get('profile_text', ''), height=150, key="profile_text_tab3")
    aspirations_input = st.text_area("Your Career/Lifestyle Aspirations (from Tab 2)", st.session_state.get('aspirations', ''), height=150, key="aspirations_text_tab3")
    
    if st.button("Generate Training Recommendations"):
        if profile_text_input and aspirations_input:
            training_recs = generate_training_recommendations(profile_text_input, aspirations_input)
            st.write("### Recommended Trainings")
            for training in training_recs:
                st.write(f"- {training}")
        else:
            st.warning("Please complete Tab 1 and Tab 2 to generate training recommendations.")