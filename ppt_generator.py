import os
import re
import json
import requests
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

class PPTGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API Key not found. Please set GEMINI_API_KEY in your .env file.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.presentation = Presentation()

    def clean_content(self, text):
        """Convert HTML / markdown returned by Gemini into plain bullet text."""
        if not isinstance(text, str):
            text = str(text)
        # Replace block-level tags with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<li>', '• ', text, flags=re.IGNORECASE)
        text = re.sub(r'</?ul>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?ol>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?p>', '\n', text, flags=re.IGNORECASE)
        # Strip all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Resolve literal \n from Streamlit text editor into actual newlines
        text = text.replace('\\n', '\n')
        
        # Strip markdown asterisks
        text = text.replace('**', '')
        
        # Collapse 3+ newlines to 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def generate_content_outline(self, topic, num_slides=5, audience="General"):
        prompt = f"""
        Create a detailed outline for the PowerPoint presentation on "{topic}" with {num_slides} slides.
        The target audience for this presentation is: {audience}.
        Please tailor the tone, complexity, and vocabulary specifically for this audience.
        
        return the response as a JSON array with the following structure:
        [
            {{
                "title": "Slide Title",
                "content": "Main content points as bullet points",
                "slide_type": "title|content|image|conclusion"
            }}
        ]

        Make sure the content is engaging, informative, and well-structured.
        the response must be a valid JSON array.
        """
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()

            if not content.startswith("[") or not content.endswith(']'):
                return None

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                return None
        except Exception as e:
            print(f"Generation Error: {e}")
            return None

    def generate_image_description(self, slide_content):
        prompt = f"""
        Based on this slide content, suggest a relevant image description that would enhance the presentation.
        {slide_content}
        Return only a brief, descriptive phrase suitable for image search (max 5 words)
        """
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            return content
        except Exception as e:
            print(f"Image Description Error: {e}")
            return "professional presentation"

    def download_image(self, query, save_path="temp_image.jpg"):
        # Try Pexels first, then fallback to Unsplash
        query_encoded = query.replace(" ", "+")

        # Method 1: Pexels API
        try:
            url = "https://api.pexels.com/v1/search"
            pexels_key = os.getenv("PEXELS_API_KEY")
            if pexels_key:
                headers = {"Authorization": pexels_key}
                params = {
                    "query": query,
                    "per_page": 1,
                    "orientation": "landscape"
                }
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get('photos'):
                    image_url = data['photos'][0]['src']['large2x']
                    image_response = requests.get(image_url, timeout=15)
                    image_response.raise_for_status()
                    with open(save_path, 'wb') as f:
                        f.write(image_response.content)
                    print(f"  [Image] Downloaded from Pexels: {query}")
                    return save_path
        except Exception as e:
            print(f"  [Image] Pexels failed ({e}), trying Unsplash...")

        # Method 2: Unsplash fallback (no API key needed)
        try:
            image_url = f"https://source.unsplash.com/1280x720/?{query_encoded}"
            image_response = requests.get(image_url, timeout=15, allow_redirects=True)
            image_response.raise_for_status()
            if len(image_response.content) > 5000:  # valid image, not an error page
                with open(save_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"  [Image] Downloaded from Unsplash: {query}")
                return save_path
        except Exception as e:
            print(f"  [Image] Unsplash also failed: {e}")

        print(f"  [Image] Could not download image for: {query}")
        return None

    def create_title_slide(self, title, subtitle=""):
        slide_layout = self.presentation.slide_layouts[0]
        slide = self.presentation.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(30)
        title_shape.text_frame.paragraphs[0].font.bold = True
        title_shape.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        if subtitle:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle
            subtitle_shape.text_frame.paragraphs[0].font.size = Pt(20)
            subtitle_shape.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
            subtitle_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    def create_content_slide(self, title, content, include_image=True):
        slide_layout = self.presentation.slide_layouts[1]
        slide = self.presentation.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(30)
        title_shape.text_frame.paragraphs[0].font.bold = True

        content_shape = slide.placeholders[1]
        content_shape.text = content
        if include_image:
            content_shape.left = Inches(0.5)
            content_shape.top = Inches(1.6)
            content_shape.width = Inches(4.8)
            content_shape.height = Inches(5.4)
        else:
            content_shape.left = Inches(0.5)
            content_shape.top = Inches(1.6)
            content_shape.width = Inches(9.0)
            content_shape.height = Inches(5.4)

        text_frame = content_shape.text_frame
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = Pt(20)
            paragraph.font.color.rgb = RGBColor(0, 0, 0)

        if include_image:
            try:
                image_desc = self.generate_image_description(content)
                image_path = self.download_image(image_desc)
                if image_path and os.path.exists(image_path):
                    slide.shapes.add_picture(image_path, Inches(5.4), Inches(1.6), width=Inches(4.1), height=Inches(4.2))
                    os.remove(image_path)
            except Exception as e:
                print(f"Error adding picture: {e}")

        return slide

    def create_image_slide(self, title, image_query, content=""):
        slide_layout = self.presentation.slide_layouts[8]
        slide = self.presentation.slides.add_slide(slide_layout)

        title_box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = title
        title_frame.paragraphs[0].font.size = Pt(30)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
        title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(4), Inches(5))
        content_frame = content_box.text_frame
        content_frame.word_wrap = True
        content_frame.text = content

        for paragraph in content_frame.paragraphs:
            paragraph.font.size = Pt(20)
            paragraph.font.color.rgb = RGBColor(51, 51, 51)

        try:
            image_path = self.download_image(image_query)
            if image_path and os.path.exists(image_path):
                slide.shapes.add_picture(image_path, Inches(5.4), Inches(1.6), width=Inches(4.1), height=Inches(4.2))
                os.remove(image_path)
        except Exception as e:
            print(f"Error adding picture: {e}")

    def generate_presentation(self, topic, num_slides=5, output_file="presentation.pptx", progress_callback=None):
        """
        Generates the presentation and saves it to output_file. 
        Accepts a progress_callback(progress_int, message_str) to report status.
        """
        if progress_callback:
            progress_callback(10, "Planning the structure and generating outline with Gemini...")

        content_outline = self.generate_content_outline(topic, num_slides)

        if not content_outline:
            raise Exception("Failed to generate content outline from Gemini. Check API keys and quotas.")

        total_slides = len(content_outline)
        for i, slide_data in enumerate(content_outline):
            title = slide_data.get("title", f"Slide {i+1}")
            content = slide_data.get("content", "")
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            content = self.clean_content(content)
            slide_type = slide_data.get("slide_type", "content")

            if progress_callback:
                progress = 10 + int(((i) / total_slides) * 80)
                progress_callback(progress, f"Generating Slide {i+1} of {total_slides}: {title}")

            if i == 0 or slide_type == "title":
                self.create_title_slide(title)
            elif slide_type == "content":
                self.create_content_slide(title, content, include_image=True)
            elif slide_type == "image":
                img_query = self.generate_image_description(content)
                self.create_image_slide(title, img_query, content)
            else:
                include_image = (i % 3 == 0)
                self.create_content_slide(title, content, include_image)

        self.presentation.save(output_file)
        if progress_callback:
            progress_callback(100, f"Presentation completed successfully!")

        return output_file
