# ✨ PresentAI - AI-Powered PowerPoint Generator

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://ai-powerpoint-generator-t6tj.onrender.com)
[![Streamlit](https://img.shields.io/badge/Built%20With-Streamlit-FF4B4B)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)

PresentAI is an interactive web application that acts as your personal Copilot to create beautiful, cohesive, and strictly structured PowerPoint presentations in seconds using Google's powerful **Gemini 2.5 Flash** AI model. 

## 🚀 Live Demo
Experience the generator for yourself here: **[PresentAI on Render](https://ai-powerpoint-generator-t6tj.onrender.com)**

## ✨ Key Features
- **Prompt to Presentation**: Just drop in a topic and select your desired length, and the AI will extrapolate an entire presentation flow.
- **Target Audience Tuning**: Natively tailor the vocabulary, complexity, and tone of your slides by choosing between *Professional*, *Academic*, *Casual*, or *Investor* audiences.
- **Editable Outlines**: Unlike rigid "one-shot" generators, PresentAI lets you intercept the generation process. Review, tweak, and perfect the AI's slide titles, bullet points, and slide formats (content vs. image) *before* the `.pptx` file is permanently compiled.
- **Automated Visuals**: The system autonomously generates image search parameters based on contextual slide content and fetches beautiful, royalty-free stock imagery (via Pexels/Unsplash keys) to embed right into your slides.
- **Native Export**: Downloads strictly as a customizable Microsoft `.pptx` file, meaning you still retain full layout control in PowerPoint after the fact.

## 🛠️ Technology Stack
- **Frontend / Interface**: [Streamlit](https://streamlit.io/)
- **Core Engine**: Python 3
- **AI Brain**: `google-generativeai` (Gemini 2.5 Flash)
- **Document Rendering**: `python-pptx`

## 💻 Running Locally

### Prerequisites
1. You will need a functioning API Key from [Google AI Studio](https://aistudio.google.com/).
2. *(Optional but Highly Recommended)* An API Key from [Pexels](https://www.pexels.com/api/) to circumvent Unsplash rate-limits for high-quality slide imagery.

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

## 🤝 Contributing
Feel free to open issues or submit pull requests if you want to extend functionality (like adding new PPT templates, injecting custom fonts, or adding more LLM providers!).