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
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in generating response: {str(e)}"

def generate_training_recommendations(profile_text, job_desc_text, aspirations):
    prompt = f"""
    Based on the following information, suggest 3 relevant courses or trainings for the next 6-12 months that will help the user achieve their career goals:
    
    **Professional Experience:**
    {profile_text}
    
    **Job Description:**
    {job_desc_text}
    
    **Career Aspirations:**
    {aspirations}
    
    Focus on the user's career goals and aspirations. Provide a short description for each course, explaining how it will help the user achieve their desired outcomes.
    """
    return call_openai_api(prompt)

def generate_job_recommendations(profile_text):
    prompt = f"""
    Based on the following professional experience, suggest 3 relevant new job roles with short descriptions:
    
    **Professional Experience:**
    {profile_text}
    
    Provide a short description for each job role.
    """
    return call_openai_api(prompt).split("\n")

def generate_summary(text, context):
    prompt = f"Generate a concise and professional summary of the following {context}:\n{text}"
    return call_openai_api(prompt)

def chatbot_response(question, profile_text, job_desc_text, aspirations, training_recs):
    context = f"""
    **User's Professional Experience:**
    {profile_text}
    
    **User's Job Description:**
    {job_desc_text}
    
    **User's Career Aspirations:**
    {aspirations}
    
    **Recommended Trainings:**
    {training_recs}
    """
    prompt = f"""
    You are a helpful career assistant chatbot. The user has provided the following information:
    
    {context}
    
    The user has asked the following question:
    {question}
    
    Provide a helpful and concise response based on the user's profile, aspirations, and recommended trainings.
    """
    return call_openai_api(prompt)

# Streamlit App
#st.title("Professional Training Recommender")

# Inject custom CSS for background image
st.markdown(
    """
    <style>
    .title-background {
        background-image: url('https://cdn.elearningindustry.com/wp-content/uploads/2023/01/shutterstock_2160978529.jpg');
        background-size: cover;
        padding:58px;
        color: White;
        text-align: Left;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App
st.markdown('<div class="title-background"><h1>Training Course Recommender</h1></div>', unsafe_allow_html=True)


# Sidebar for inputs
with st.sidebar:
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
        st.session_state['profile_text'] = profile_text
    
    if linkedin_text:
        profile_text += "\n" + linkedin_text
        st.session_state['profile_text'] = profile_text

    st.header("Upload Job Description")
    uploaded_job_desc = st.file_uploader("Upload a Job Description (Optional)", type=["pdf", "docx"], key="job_desc_upload")
    
    job_desc_text = ""
    if uploaded_job_desc:
        if uploaded_job_desc.type == "application/pdf":
            job_desc_text = extract_text_from_pdf(uploaded_job_desc)
        elif uploaded_job_desc.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            job_desc_text = extract_text_from_docx(uploaded_job_desc)
        st.session_state['job_desc_text'] = job_desc_text

    st.header("Enter Career Aspirations")
    aspirations = st.text_area("Enter your career/lifestyle aspirations", key="aspirations_input")
    st.session_state['aspirations'] = aspirations

# Main content
tabs = ["Experience Summary", "Job Summary", "Course Recommendations"]
tab1, tab2, tab3 = st.tabs(tabs)

with tab1:
    st.header("Experience Summary")
    profile_text = st.session_state.get('profile_text', "")
    if profile_text:
        experience_summary = generate_summary(profile_text, "professional experience")
        st.write("### Professional Experience Summary")
        st.write(experience_summary)
        
        st.header("Job Recommendations")
        if st.button("Generate Job Recommendations"):
            job_recs = generate_job_recommendations(profile_text)
            job_recs = [job.strip() for job in job_recs if job.strip()]
            st.session_state['job_recs'] = job_recs
            st.write("### Recommended Jobs")
            for job in job_recs:
                job_title = job.split(":")[0].split("-")[0].strip()
                st.write(f"**{job_title}**: {job[len(job_title):].strip()}")
        
        if 'job_recs' in st.session_state:
            job_titles = [job.split(":")[0].split("-")[0].strip() for job in st.session_state['job_recs']]
            selected_job = st.selectbox("Select your desired job:", job_titles, key="selected_job")

            # Ensure the selected job is stored in session_state only when it's different
            if selected_job and st.session_state.get('selected_job') != selected_job:
                st.session_state['selected_job'] = selected_job

    else:
        st.warning("Please upload a profile or enter LinkedIn details in the sidebar.")

with tab2:
    st.header("Job Summary")
    job_desc_text = st.session_state.get('job_desc_text', '')
    selected_job = st.session_state.get('selected_job', '')
    
    if job_desc_text:
        job_summary_input = job_desc_text
        source = "Uploaded Job Description"
    elif selected_job:
        job_summary_input = selected_job
        source = "Selected Job Recommendation"
    else:
        job_summary_input = ""
        source = None
    
    if job_summary_input:
        job_summary = generate_summary(job_summary_input + "\n" + st.session_state.get('aspirations', ''), "job summary")
        st.write(f"### {source} Summary")
        st.write(job_summary)
        st.session_state['job_summary'] = job_summary
    else:
        st.warning("Please upload a job description or select a recommended job.")

with tab3:
    st.header("Course Recommendations")
    if 'profile_text' in st.session_state and 'job_summary' in st.session_state and 'aspirations' in st.session_state:
        if st.button("Generate Training Recommendations"):
            training_recs = generate_training_recommendations(
                st.session_state['profile_text'],
                st.session_state['job_summary'],
                st.session_state['aspirations']
            )
            st.session_state['training_recs'] = training_recs
            st.write("### Recommended Trainings")
            for training in training_recs.split("\n"):
                if training.strip():
                    st.write(f"**{training.split(':')[0].strip()}**: {training[len(training.split(':')[0]):].strip()}")
        
                # Chatbot for follow-up questions
        if 'training_recs' in st.session_state:
            st.header("Chatbot: Ask Follow-Up Questions")
            user_question = st.text_input("Ask a question about your recommendations, profile, or aspirations:")
            if user_question:
                chatbot_answer = chatbot_response(
                    user_question,
                    st.session_state['profile_text'],
                    st.session_state.get('job_desc_text', ''),
                    st.session_state['aspirations'],
                    st.session_state['training_recs']
                )
                st.write("**Chatbot Response:**")
                st.write(chatbot_answer)
                
    else:
        st.warning("Please upload a profile, select a job, and enter aspirations.")
