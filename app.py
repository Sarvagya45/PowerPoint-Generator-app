import streamlit as st
import os
import time
import time
from dotenv import load_dotenv
import db
from ppt_generator import PPTGenerator

# Load environment variables
load_dotenv()

# Setting up Streamlit page
st.set_page_config(
    page_title="AI PowerPoint Generator",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="✨"
)

# Authentication State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "step" not in st.session_state:
    st.session_state.step = 0
if "outline" not in st.session_state:
    st.session_state.outline = None

def reset_state():
    st.session_state.step = 0
    st.session_state.outline = None
    for key in ["topic", "num_slides", "audience", "include_details", "theme", "font_name"]:
        if key in st.session_state:
            del st.session_state[key]
    if "generated_pptx" in st.session_state:
        del st.session_state.generated_pptx

# Custom CSS for modern styling
st.markdown("""
<style>
    .hero-header {
        font-size: 4.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 0px;
    }
    .hero-subheader {
        font-size: 1.5rem;
        color: #475569;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 400;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 30px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2), 0 2px 4px -1px rgba(59, 130, 246, 0.1);
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stExpander"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)


api_key = os.getenv("GEMINI_API_KEY")
# --- GLOBAL SIDEBAR ---
with st.sidebar:
    if st.session_state.logged_in:
        st.markdown(f"### 👋 Welcome, {st.session_state.full_name or st.session_state.username}")
        if st.session_state.user_id:
            st.caption(f"ID: {st.session_state.user_id}")
            
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        st.markdown("---")
        if st.session_state.step > 0:
            if st.button("Cancel & Return to Dashboard", use_container_width=True):
                reset_state()
                st.rerun()
    else:
        st.title("Settings")
        st.info("Ensure that 'GEMINI_API_KEY' is properly set in your local .env file. 'PEXELS_API_KEY' is optional but recommended.")

# --- STEP -1: AUTHENTICATION GATEWAY ---
if not st.session_state.logged_in:
    st.markdown('<p class="hero-header">✨ PresentAI</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subheader">Login to generate, track, and re-download your presentations.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["🔒 Secure Log In", "📝 Create Account"])
            
            with tab_login:
                st.markdown("##### Welcome Back")
                login_user = st.text_input("Username", placeholder="Enter your username")
                login_pass = st.text_input("Password", type="password", placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Log In", use_container_width=True, type="primary"):
                    success, msg, name, uid = db.authenticate_user(login_user, login_pass)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.session_state.full_name = name
                        st.session_state.user_id = uid
                        st.session_state.step = 0
                        st.rerun()
                    else:
                        st.error(msg)

            with tab_signup:
                st.markdown("##### Create a completely new account")
                reg_user = st.text_input("New Username", placeholder="Choose a unique username")
                reg_pass = st.text_input("New Password", type="password", placeholder="Enter a secure password")
                
                st.divider()
                st.caption("✨ Optional Title Slide Injection Data:")
                reg_name = st.text_input("Full Name", placeholder="e.g. John Doe (Appears on PPT title slide)")
                reg_id = st.text_input("Your ID / Reg Number", placeholder="e.g. EMP-912")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                    if reg_user and reg_pass:
                        success, msg = db.register_user(reg_user, reg_pass, reg_name, reg_id)
                        if success:
                            st.success("✅ Registration successful! Please switch to the **Log In** tab.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("⚠️ Username and Password are strictly required to create an account.")
    st.stop()


# --- STEP 0: DASHBOARD / LANDING PAGE ---
if st.session_state.step == 0:
    st.markdown('<p class="hero-header">✨ PresentAI</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subheader">Your Copilot for Beautiful, Professional Presentations.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### 🚀 Build a New Presentation")
            st.markdown("Give us a **topic** and an **audience**, review the interactive outline, and construct the `.pptx` directly.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Start Generator →", use_container_width=True, type="primary"):
                st.session_state.step = 1
                st.rerun()
                
    st.markdown("---")
    st.markdown("### 🗂️ Your Past Presentations")
    history = db.get_user_history(st.session_state.username)
    if not history:
        st.info("You haven't generated any presentations yet! Build one above.")
    else:
        for item in history:
            with st.expander(f"📊 {item['topic']} ({item['timestamp']})"):
                st.write(f"**Target Audience**: {item['audience']} | **Length**: {item['num_slides']} slides")
                if os.path.exists(item['filename']):
                    with open(item['filename'], "rb") as f:
                        st.download_button(
                            label=f"⬇️ Re-Download {os.path.basename(item['filename'])}",
                            data=f,
                            file_name=os.path.basename(item['filename']),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            key=f"dl_{item['filename']}"
                        )
                else:
                    st.warning("Presentation file has been deleted from the server.")

# --- STEP 1: INITIAL SETUP ---
elif st.session_state.step == 1:
    st.markdown('<p class="main-header">Step 1: Define Your Presentation</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Set the topic, length, and let us know who is listening.</p>', unsafe_allow_html=True)
    
    if not api_key:
        st.error("GEMINI_API_KEY is not found in the environment. Please add it to your `.env` file.")
        st.stop()

    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Enter the presentation topic:", placeholder="e.g., The Future of Remote Work")
        with col2:
            num_slides = st.slider("Number of slides:", min_value=3, max_value=20, value=5, step=1)
            
        st.markdown("### Target Audience")
        st.markdown("How should the AI tailor the vocabulary and tone?")
        audience = st.radio(
            "Target Audience",
            options=["Professional / Executive", "Academic / Students", "Casual / Conversational", "Investors / Pitch"],
            label_visibility="collapsed",
            horizontal=True
        )
        
        st.markdown("### Visual Aesthetics")
        with st.container(border=True):
            col_theme, col_font = st.columns(2)
            with col_theme:
                theme_choice = st.selectbox("Slide Theme", ["Classic Light", "Midnight Dark", "Corporate Blue", "Forest Green", "Warm Sand"])
            with col_font:
                font_choice = st.selectbox("Typography Style", ["Calibri", "Arial", "Times New Roman", "Georgia", "Courier New"])

        st.markdown("### Title Slide Options")
        include_details = False
        with st.container(border=True):
            if st.session_state.full_name or st.session_state.user_id:
                include_details = st.checkbox("Include my Name & ID heavily on the first title slide", value=True)
                st.caption(f"Will print as: *{st.session_state.full_name} | {st.session_state.user_id}*")
            else:
                st.info("💡 You didn't set a Name or ID in your profile, so the title slide will remain generic.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Outline", use_container_width=True):
            if not topic.strip():
                st.error("Please enter a valid presentation topic.")
            else:
                with st.spinner(f"Brainstorming the outline for {audience.split(' ', 1)[1]}..."):
                    generator = PPTGenerator(api_key=api_key)
                    outline = generator.generate_content_outline(topic, num_slides, audience=audience)
                    
                    if outline:
                        for slide in outline:
                            if "content" in slide and isinstance(slide["content"], list):
                                slide["content"] = "\\n".join(str(item) for item in slide["content"])
                                
                        st.session_state.outline = outline
                        st.session_state.topic = topic
                        st.session_state.num_slides = num_slides
                        st.session_state.audience = audience
                        st.session_state.theme = theme_choice
                        st.session_state.font_name = font_choice
                        st.session_state.include_details = include_details
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("Failed to generate outline. Please try again.")

# --- STEP 2: EDIT OUTLINE ---
elif st.session_state.step == 2:
    st.markdown('<p class="main-header">Step 2: Review and Edit Outline</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Reviewing outline for: <b>{st.session_state.topic}</b> (Audience: {st.session_state.audience})</p>', unsafe_allow_html=True)
    
    st.info("Edit the table below to modify titles, content (bullet points), and slide types. You can even add or remove rows using the handles on the left!")
    
    edited_outline = st.data_editor(
        st.session_state.outline,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "title": st.column_config.TextColumn("Slide Title", required=True),
            "content": st.column_config.TextColumn("Content points (use actual new lines or \\n for bullet points)", required=True),
            "slide_type": st.column_config.SelectboxColumn("Slide Type", options=["title", "content", "image", "conclusion"], required=True)
        }
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Start", use_container_width=True):
            reset_state()
            st.rerun()
    with col2:
        if st.button("Confirm & View Preview", use_container_width=True):
            st.session_state.outline = edited_outline
            st.session_state.step = 3
            st.rerun()

# --- STEP 3: PREVIEW & GENERATE PPT ---
elif st.session_state.step == 3:
    st.markdown('<p class="main-header">Step 3: Preview & Download</p>', unsafe_allow_html=True)
    
    col_preview, col_gen = st.columns([1, 1])
    
    with col_preview:
        st.markdown("### PPT Content Plan")
        for i, slide in enumerate(st.session_state.outline):
            with st.expander(f"Slide {i+1}: {slide.get('title', 'Untitled')} ({slide.get('slide_type', 'content')})", expanded=True):
                content_str = slide.get('content', '')
                if isinstance(content_str, list):
                    content_str = "\n".join(str(s) for s in content_str)
                st.write(content_str.replace('\\n', '\n'))
                
    with col_gen:
        st.markdown("### Generation Status")
        
        # Prepare output directory
        output_dir = "presentations"
        os.makedirs(output_dir, exist_ok=True)
        
        safe_topic = "".join(x for x in st.session_state.topic if x.isalnum() or x in " -_")
        timestamp_str = str(int(time.time()))
        output_filename = os.path.join(output_dir, f"{st.session_state.username}_{safe_topic.lower().replace(' ', '_')}_{timestamp_str}.pptx")
        
        class CustomPPTGenerator(PPTGenerator):
            def generate_content_outline(self, topic, num_slides, audience="General"):
                return st.session_state.outline

        progress_bar = st.progress(0)
        status_text = st.empty()
        error_container = st.empty()
        
        def ui_callback(progress_int, message_str):
            progress_bar.progress(progress_int)
            status_text.info(f"⏳ {message_str}")
            
        try:
            if "generated_pptx" not in st.session_state:
                generator = CustomPPTGenerator(
                    api_key=api_key, 
                    theme=st.session_state.get('theme', 'Classic Light'),
                    font_name=st.session_state.get('font_name', 'Calibri')
                )
                
                # Format Subtitle!
                title_subtitle = ""
                if st.session_state.get('include_details'):
                    parts = []
                    if st.session_state.full_name:
                        parts.append(f"Presented by: {st.session_state.full_name}")
                    if st.session_state.user_id:
                        parts.append(f"ID: {st.session_state.user_id}")
                    title_subtitle = " | ".join(parts)
                
                status_text.info("Building presentation...")
                generator.generate_presentation(
                    topic=st.session_state.topic,
                    num_slides=len(st.session_state.outline), 
                    output_file=output_filename,
                    progress_callback=ui_callback,
                    title_subtitle=title_subtitle
                )
                
                # Save into the SQLite History tracking
                db.save_history(
                    username=st.session_state.username,
                    topic=st.session_state.topic,
                    num_slides=len(st.session_state.outline),
                    audience=st.session_state.audience,
                    filename=output_filename
                )
                
                st.session_state.generated_pptx = output_filename
                progress_bar.progress(100)
                status_text.success("Presentation generated successfully!")
            else:
                progress_bar.progress(100)
                status_text.success("Presentation ready!")
            
            # Read output and provide download button
            if os.path.exists(st.session_state.generated_pptx):
                with open(st.session_state.generated_pptx, "rb") as file:
                    st.download_button(
                        label="Download Presentation (.pptx)",
                        data=file,
                        file_name=os.path.basename(output_filename),
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Edit Outline Again", use_container_width=True):
                    # We do NOT delete the presentation from disk anymore, because it's part of our history log!
                    del st.session_state.generated_pptx
                    st.session_state.step = 2
                    st.rerun()
                    
                if st.button("Return to Dashboard", use_container_width=True):
                    reset_state()
                    st.rerun()
                            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            error_container.error(f"An error occurred during generation:\n\n{str(e)}")
