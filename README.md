# ✨ PresentAI - AI-Powered PowerPoint Generator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://ai-powerpoint-generator-t6tj.onrender.com)
[![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-FF4B4B)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)

PresentAI is an interactive web application that acts as your personal Copilot to create beautiful, cohesive, and strictly structured PowerPoint presentations in seconds using Google's powerful **Gemini 2.5 Flash** AI model. 

## 🚀 Live Demo
Experience the generator for yourself here: **[PresentAI on Render](https://ai-powerpoint-generator-t6tj.onrender.com)**

---

## 🌟 What We Have Built
This project evolved from a standard backend script into a full-fledged, interactive web application. Here are the major functionalities implemented:

### 1. Interactive 3-Step Wizard Frontend
- Fully transitioned the application to a slick **Streamlit** user interface.
- Built a welcoming **Landing Page** (Step 0) to greet users before launching the presentation generation process.
- Designed a step-by-step workflow preventing users from getting overwhelmed with too many options simultaneously.

### 2. Live Outline Editing (Human-in-the-Loop)
- **Intercepting the AI**: Unlike rigid generators that jump straight from prompt to download, an interactive review stage was introduced.
- Using `st.data_editor`, you can freely modify the AI's generated outline. You can rewrite bullet points, tweak slide titles, add/remove slides entirely, or manually designate slides as "title," "content," or "image" slides.
- **Backend Subclassing**: This was achieved without fundamentally rewriting the backend script (`ppt_generator.py`). Instead, the Streamlit frontend dynamically "subclasses" the `PPTGenerator` object to transparently inject your custom edits directly into the PowerPoint compile process!

### 3. Dynamic Audience Targeting
- Added an "Audience Selection" feature directly on the initial prompt screen (`Professional`, `Academic`, `Casual`, `Investors`).
- The Python backend dynamically incorporates this parameter into the prompt structure, instructing Gemini to aggressively adjust complexity, tone, and formatting depending exactly on who will be watching the slide deck.

### 4. Automated & Robust Data Parsing
- **List Flattening**: Handled annoying edge cases where Gemini returns bullet points as Python `list` objects, dynamically filtering them into clean structural string formats so the table editor doesn't crash.
- **Markdown Stripping**: Gemini frequently hallucinated bold asterisks (`**`) inside the raw text. The parser was fortified to strip these outright, guaranteeing the Microsoft PowerPoint text boxes look pristine and immediately readable. 

### 5. Smart Image Embedding
- Handled API communication with beautiful stock photography pools (Pexels / Unsplash). 
- Using Gemini, the app reads your specific slide content and reverse-engineers a 5-word image search query, automatically downloading and cleanly embedding relevant contextual photography straight into your `.pptx` slides. 

---

## 🛠️ Technology Stack
- **Frontend / Interface**: [Streamlit](https://streamlit.io/)
- **Core Engine**: Python 3
- **AI Brain**: `google-generativeai` (Gemini 2.5 Flash API)
- **Document Rendering**: `python-pptx`
- **Asset Fetching**: `requests` (Pexels/Unsplash)

## 💻 Running Locally

### Prerequisites
1. You will need a functioning API Key from [Google AI Studio](https://aistudio.google.com/).
2. *(Optional but Highly Recommended)* An API Key from [Pexels](https://www.pexels.com/api/) to fetch higher quality slide imagery.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/powerpoint-generator.git
   cd powerpoint-generator
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Environment Variables:
   Create a `.env` file in the root directory and add your secret API keys:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   PEXELS_API_KEY=your_pexels_key_here
   ```

4. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   *Your browser will automatically open to `http://localhost:8501`.*