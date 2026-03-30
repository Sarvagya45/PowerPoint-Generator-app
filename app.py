import streamlit as st
import os
import time
from dotenv import load_dotenv
from ppt_generator import PPTGenerator

# Load environment variables
load_dotenv()

# Set up Streamlit page
st.set_page_config(
    page_title="AI PowerPoint Generator",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="✨"
)

# Initialize Session State
if "step" not in st.session_state:
    st.session_state.step = 0 # Step 0 is the Landing Page
if "outline" not in st.session_state:
    st.session_state.outline = None

def reset_state():
    st.session_state.step = 0
    st.session_state.outline = None
    for key in ["topic", "num_slides", "audience"]:
        if key in st.session_state:
            del st.session_state[key]
    if "generated_pptx" in st.session_state:
        if os.path.exists(st.session_state.generated_pptx):
            try:
                os.remove(st.session_state.generated_pptx)
            except Exception:
                pass
        del st.session_state.generated_pptx

# Custom CSS for modern styling
st.markdown("""
<style>
    .hero-header {
        font-size: 4rem;
        font-weight: 800;
        color: #1E88E5;
        text-align: center;
        margin-top: 50px;
        margin-bottom: 0px;
    }
    .hero-subheader {
        font-size: 1.5rem;
        color: #555555;
        text-align: center;
        margin-bottom: 50px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 30px;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
        border: none;
    }
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stDownloadButton button:hover {
        background-color: #388E3C;
    }
    .center-btn {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Settings")
    st.info("Ensure that 'GEMINI_API_KEY' is properly set in your local .env file. 'PEXELS_API_KEY' is optional but recommended.")
    st.markdown("---")
    if st.button("Start Over", key="sidebar_reset", use_container_width=True):
        reset_state()
        st.rerun()

api_key = os.getenv("GEMINI_API_KEY")

# --- STEP 0: LANDING PAGE ---
if st.session_state.step == 0:
    st.markdown('<p class="hero-header">PresentAI</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subheader">Your Copilot for Beautiful, Professional Presentations.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        **Welcome!** Give us a topic and an audience, and we'll instantly generate a cohesive, structured PowerPoint using Google's Gemini 2.5 Flash. You will be able to review and tweak the underlying presentation outline *before* the `.pptx` file is finally generated!
        
        To begin, simply click the start button below.
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Get Started", use_container_width=True, type="primary"):
            st.session_state.step = 1
            st.rerun()

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
        # Audience Selection Buttons! Using radio for clean UI
        audience = st.radio(
            "Target Audience",
            options=["Professional / Executive", "Academic / Students", "Casual / Conversational", "Investors / Pitch"],
            label_visibility="collapsed",
            horizontal=True
        )
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Outline", use_container_width=True):
            if not topic.strip():
                st.error("Please enter a valid presentation topic.")
            else:
                with st.spinner(f"Brainstorming the outline for {audience.split(' ', 1)[1]}..."):
                    generator = PPTGenerator(api_key=api_key)
                    # Pass the audience parameter directly!
                    outline = generator.generate_content_outline(topic, num_slides, audience=audience)
                    
                    if outline:
                        # Fix for ColumnDataKind.LIST Editor Error!
                        # Some LLM outputs return 'content' as a list instead of a long string.
                        # st.data_editor throws an error if it sees a list in a TextColumn. Let's fix it!
                        for slide in outline:
                            if "content" in slide and isinstance(slide["content"], list):
                                slide["content"] = "\n".join(str(item) for item in slide["content"])
                                
                        st.session_state.outline = outline
                        st.session_state.topic = topic
                        st.session_state.num_slides = num_slides
                        st.session_state.audience = audience
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("Failed to generate outline. Please try again.")

# --- STEP 2: EDIT OUTLINE ---
elif st.session_state.step == 2:
    st.markdown('<p class="main-header">Step 2: Review and Edit Outline</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Reviewing outline for: <b>{st.session_state.topic}</b> (Audience: {st.session_state.audience})</p>', unsafe_allow_html=True)
    
    st.info("Edit the table below to modify titles, content (bullet points), and slide types. You can even add or remove rows using the handles on the left!")
    
    # Render Data Editor
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
    
    # Save edits and proceed
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
                # Properly display literal literal '\n' as linebreaks in the preview 
                st.write(content_str.replace('\\n', '\n'))
                
    with col_gen:
        st.markdown("### Generation Status")
        # Sanitize filename
        safe_topic = "".join(x for x in st.session_state.topic if x.isalnum() or x in " -_")
        output_filename = f"{safe_topic.lower().replace(' ', '_')}_present.pptx"
        
        # Subclass to inject the edited outline without changing ppt_generator.py!
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
                generator = CustomPPTGenerator(api_key=api_key)
                
                status_text.info("Building presentation...")
                generator.generate_presentation(
                    topic=st.session_state.topic,
                    num_slides=len(st.session_state.outline), # use edited length
                    output_file=output_filename,
                    progress_callback=ui_callback
                )
                st.session_state.generated_pptx = output_filename
                progress_bar.progress(100)
                status_text.success("Presentation generated successfully!")
                st.balloons()
            else:
                progress_bar.progress(100)
                status_text.success("Presentation ready!")
            
            # Read output and provide download button
            if os.path.exists(st.session_state.generated_pptx):
                with open(st.session_state.generated_pptx, "rb") as file:
                    st.download_button(
                        label="Download Presentation (.pptx)",
                        data=file,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Edit Outline Again option
                if st.button("Edit Outline Again", use_container_width=True):
                    if os.path.exists(st.session_state.generated_pptx):
                        try:
                            os.remove(st.session_state.generated_pptx)
                        except Exception:
                            pass
                    del st.session_state.generated_pptx
                    st.session_state.step = 2
                    st.rerun()
                    
                if st.button("Start Fresh!", use_container_width=True):
                    reset_state()
                    st.rerun()
                            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            error_container.error(f"An error occurred during generation:\n\n{str(e)}")
