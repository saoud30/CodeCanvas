import streamlit as st
import os
from dotenv import load_dotenv
import groq
import base64

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="CodeCanvas", page_icon="🎨", layout="wide")

# Initialize Groq client
def init_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your Groq API Key:", type="password")
        if not api_key:
            st.warning("Please enter a valid Groq API Key to use AI-powered features.")
            return None
    try:
        return groq.Groq(api_key=api_key)
    except groq.GroqError as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        return None

client = init_groq_client()

# Sidebar navigation
st.sidebar.title("CodeCanvas 🎨")
page = st.sidebar.radio("Navigate", ["README.md Generator", ".gitignore Generator", "Requirements.txt Generator", "AI Guide", "File Converter"])

# Theme toggle
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {
        background-color: #2b2b2b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Groq AI Chat function
def groq_ai_chat(query, system_message):
    if client:
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                model="mixtral-8x7b-32768",
                max_tokens=1000
            )
            return response.choices[0].message.content
        except groq.GroqError as e:
            st.error(f"Error generating response: {str(e)}")
            return ""
    return ""

# Add chat input to each section
def add_chat_input(section_name):
    st.subheader(f"Chat with AI about {section_name}")
    query = st.text_input(f"Ask a question about {section_name}:")
    if query:
        system_message = f"You are a helpful assistant providing information about {section_name}."
        response = groq_ai_chat(query, system_message)
        st.write("AI Response:")
        st.write(response)

def readme_generator():
    st.header("README.md Generator")
    
    # AI-powered search bar
    search_query = st.text_input("Enter project details for AI-generated README:")
    if search_query and client:
        generated_content = groq_ai_chat(f"Generate a README.md for a project with the following description: {search_query}", "You are a helpful assistant that generates README.md content based on project descriptions.")
    else:
        generated_content = ""

    # Editable section
    readme_content = st.text_area("Edit your README.md content:", value=generated_content, height=300)
    
    # Real-time preview
    st.subheader("Preview")
    st.markdown(readme_content)
    
    # Download button
    if st.button("Download README.md"):
        st.download_button(
            label="Click to download",
            data=readme_content,
            file_name="README.md",
            mime="text/markdown"
        )
    
    add_chat_input("README.md Generator")

def gitignore_generator():
    st.header(".gitignore Generator")
    
    project_type = st.text_input("Enter project type (e.g., Python, Node.js):")
    exclusions = st.text_input("Enter files to exclude (comma-separated):")
    
    if st.button("Generate .gitignore") and client:
        gitignore_content = groq_ai_chat(f"Generate a .gitignore file for a {project_type} project. Include these files: {exclusions}", "You are a helpful assistant that generates .gitignore files based on project types and exclusions.")
        st.text_area("Generated .gitignore:", value=gitignore_content, height=300)
        st.download_button(
            label="Download .gitignore",
            data=gitignore_content,
            file_name=".gitignore",
            mime="text/plain"
        )
    
    add_chat_input(".gitignore Generator")

def requirements_generator():
    st.header("Requirements.txt Generator")
    
    python_code = st.text_area("Enter your Python code:", height=200)
    
    if st.button("Generate requirements.txt") and client:
        requirements_content = groq_ai_chat(f"Generate a requirements.txt file for the following Python code:\n\n{python_code}", "You are a helpful assistant that generates requirements.txt files based on Python code. Provide only the package names and versions, one per line, without any additional text or explanations.")
        requirements_list = [line.strip() for line in requirements_content.split('\n') if line.strip() and not line.startswith('#')]
        cleaned_requirements = '\n'.join(requirements_list)
        st.text_area("Generated requirements.txt:", value=cleaned_requirements, height=200)
        st.download_button(
            label="Download requirements.txt",
            data=cleaned_requirements,
            file_name="requirements.txt",
            mime="text/plain"
        )
    
    add_chat_input("Requirements.txt Generator")

def ai_guide():
    st.header("AI Guide")
    
    python_script = st.text_area("Paste your Python script here:", height=200)
    
    if st.button("Get Guide") and client:
        guide_content = groq_ai_chat(f"Provide a step-by-step guide for running the following Python script, including setting up folders, virtual environments, and installing dependencies:\n\n{python_script}", "You are a helpful assistant that provides step-by-step guides for running Python scripts, including setup instructions.")
        st.markdown(guide_content)
    
    if st.button("AI Suggestion for Improvement") and client:
        suggestion_content = groq_ai_chat(f"Suggest improvements for the following Python script:\n\n{python_script}", "You are a helpful assistant that provides suggestions for improving Python scripts.")
        st.markdown(suggestion_content)
    
    add_chat_input("AI Guide")

def file_converter():
    st.header("File Converter")
    
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "md", "py"])
    if uploaded_file is not None:
        file_contents = uploaded_file.read().decode("utf-8")
        st.text_area("File contents:", value=file_contents, height=200)
        
        target_format = st.selectbox("Convert to:", ["Base64", "HTML", "Markdown"])
        
        if st.button("Convert"):
            if target_format == "Base64":
                converted = base64.b64encode(file_contents.encode()).decode()
            elif target_format == "HTML":
                converted = f"<pre>{file_contents}</pre>"
            else:  # Markdown
                converted = f"```\n{file_contents}\n```"
            
            st.text_area("Converted content:", value=converted, height=200)
            st.download_button(
                label=f"Download as {target_format}",
                data=converted,
                file_name=f"converted.{target_format.lower()}",
                mime=f"text/{target_format.lower()}"
            )
    
    add_chat_input("File Converter")

# Main app logic
if page == "README.md Generator":
    readme_generator()
elif page == ".gitignore Generator":
    gitignore_generator()
elif page == "Requirements.txt Generator":
    requirements_generator()
elif page == "AI Guide":
    ai_guide()
elif page == "File Converter":
    file_converter()