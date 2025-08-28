
# Standard Django imports
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Third-party imports
import google.generativeai as genai
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

@csrf_exempt
def process_url(request):
    """
    Process a news article URL and generate a comprehensive critical analysis report in PDF format.
    
    This view function:
    1. Accepts a POST request with a URL parameter
    2. Scrapes the article content from the provided URL
    3. Analyzes the content using multiple AI-powered critical thinking prompts
    4. Generates a professionally formatted PDF report with color-coded sections
    
    Args:
        request (HttpRequest): Django request object containing the URL in POST data
        
    Returns:
        HttpResponse: PDF file containing the analysis report if successful
                     404 error if article content cannot be found
    """
    # Get URL from request or use default
    url = request.POST.get('url') or "https://www.hindustantimes.com/trending/us/indian-student-at-penn-state-gives-university-apartment-tour-candid-video-goes-viral-101756006453089.html?articleno=1&utm_source=taboola_widget&utm_medium=taboola_widget&utm_campaign=article_detail_page"

    # Extract unique dataid from URL path
    parsed_url = urlparse(url)
    data_id = parsed_url.path

    # Fetch HTML content from the article URL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the main article div using dataid
    main_div = soup.find("div", {"dataid": data_id})

    if main_div:
        # Extract all paragraph texts inside the main div
        paragraphs = main_div.find_all("p")
        article_text = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Load prompt templates from the prompts folder
        import os
        prompt_dir = os.path.join(os.path.dirname(__file__), '../prompts')
        prompt_files = [
            'core_claims.txt',
            'language_tone.txt',
            'red_flags.txt',
            'verification_questions.txt',
            'entity_recognition.txt',
            'counter_argument.txt',
        ]
        prompts = {}

        # Use OpenAI new client for analysis
        from openai import OpenAI
        
        # Initialize OpenAI client with API key from environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        client = OpenAI(api_key=api_key)

        # Read each prompt file
        for fname in prompt_files:
            with open(os.path.join(prompt_dir, fname), encoding='utf-8') as f:
                prompts[fname] = f.read().strip()

        def get_openai_response(prompt, article_text):
            """
            Generate an AI-powered analysis response using OpenAI's chat completion API.
            
            Args:
                prompt (str): The specific analysis prompt to be used (e.g., core claims, red flags)
                article_text (str): The full text of the article to be analyzed
                
            Returns:
                str: AI-generated analysis response, limited to 100 words
                
            Note:
                Uses system role as 'critical thinking assistant' for focused analysis
                Enforces a 100-word limit for concise, relevant responses
            """
            messages = [
                {"role": "system", "content": "You are a critical thinking assistant."},
                {"role": "user", "content": f"{prompt}\n\nLimit your response to 100 words.\n\nArticle:\n{article_text}"}
            ]
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Use the latest model as per your example
                messages=messages,
                max_tokens=300
            )
            return completion.choices[0].message.content.strip()

        # Run all prompts and collect results
        results = {}
        for key, prompt in prompts.items():
            try:
                results[key] = get_openai_response(prompt, article_text)
            except Exception as e:
                results[key] = f"Error: {e}"

        # Build Markdown report from all responses
        report = f"# Critical Analysis Report for: {url}\n"
        report += "\n### Core Claims\n" + results.get('core_claims.txt', '')
        report += "\n### Language & Tone Analysis\n" + results.get('language_tone.txt', '')
        report += "\n### Potential Red Flags\n" + results.get('red_flags.txt', '')
        report += "\n### Verification Questions\n" + results.get('verification_questions.txt', '')
        report += "\n### Entity Recognition\n" + results.get('entity_recognition.txt', '')
        report += "\n### Counter-Argument Simulation\n" + results.get('counter_argument.txt', '')

        # --- PDF Generation ---
        import io
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        def markdown_to_sections(report):
            """
            Convert a markdown-formatted report into a dictionary of sections.
            
            Args:
                report (str): The full markdown report containing multiple sections
                
            Returns:
                dict: A dictionary where keys are section titles and values are lists of content lines
                
            Note:
                - Sections are identified by '### ' prefix in the markdown
                - Content lines are grouped under their respective section titles
                - Empty lines are filtered out
            """
            sections = {}
            current_title = None
            for line in report.splitlines():
                if line.startswith('### '):
                    current_title = line.replace('### ', '').strip()
                    sections[current_title] = []
                elif current_title and line.strip():
                    sections[current_title].append(line)
            return sections

        sections = markdown_to_sections(report)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               leftMargin=50, rightMargin=50, topMargin=60, bottomMargin=40)
        styles = getSampleStyleSheet()
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], leftIndent=20, spaceAfter=6)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], leftIndent=0, spaceAfter=6)
        title_style = ParagraphStyle('Title', parent=styles['Heading2'], textColor=colors.black, spaceAfter=12, fontSize=16, fontName='Helvetica-Bold')

        section_colors = {
            "Core Claims": colors.lightblue,
            "Language & Tone Analysis": colors.lightgreen,
            "Potential Red Flags": colors.pink,
            "Verification Questions": colors.lightyellow,
            "Entity Recognition": colors.lavender,
            "Counter-Argument Simulation": colors.beige,
        }

        story = []
        # Title
        story.append(Paragraph(f"<b>Critical Analysis Report for:</b> {url}", ParagraphStyle('MainTitle', fontSize=18, textColor=colors.darkblue, spaceAfter=18, fontName='Helvetica-Bold')))

        for title, content in sections.items():
            color = section_colors.get(title, colors.white)
            # Section title with background color
            story.append(Spacer(1, 12))
            story.append(Paragraph(f'<para backColor="{color}"><b>{title}</b></para>', title_style))
            story.append(Spacer(1, 8))
            numbered_prefixes = tuple(str(i)+'.' for i in range(1,10))
            for line in content:
                if line.startswith("*") or line.strip().startswith(numbered_prefixes):
                    story.append(Paragraph(line, bullet_style))
                else:
                    story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        doc.build(story)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
    else:
        return HttpResponse("Could not find article div with given dataid", status=404)
        title_style = ParagraphStyle('Title', parent=styles['Heading2'], textColor=colors.black, spaceAfter=12, fontSize=16, fontName='Helvetica-Bold')

        section_colors = {
            "Core Claims": colors.lightblue,
            "Language & Tone Analysis": colors.lightgreen,
            "Potential Red Flags": colors.pink,
            "Verification Questions": colors.lightyellow,
            "Entity Recognition": colors.lavender,
            "Counter-Argument Simulation": colors.beige,
        }

        story = []
        # Title
        story.append(Paragraph("<b>Critical Analysis Report Of News Article</b>", ParagraphStyle('MainTitle', fontSize=18, textColor=colors.darkblue, spaceAfter=18, fontName='Helvetica-Bold')))

        for title, content in sections.items():
            color = section_colors.get(title, colors.white)
            # Section title with background color
            story.append(Spacer(1, 12))
            story.append(Paragraph(f'<para backColor="{color}"><b>{title}</b></para>', title_style))
            story.append(Spacer(1, 8))
            numbered_prefixes = tuple(str(i)+'.' for i in range(1,10))
            for line in content:
                if line.startswith("*") or line.strip().startswith(numbered_prefixes):
                    story.append(Paragraph(line, bullet_style))
                else:
                    story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        doc.build(story)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
        # p.drawString(40, y, f"Critical Analysis Report for: {url}")
        y -= 40

        for title, content in sections.items():
            color = section_colors.get(title, colors.white)
            p.setFillColor(color)
            p.rect(30, y-20, width-60, 25, fill=1, stroke=0)
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(40, y, title)
            y -= 30
            p.setFont("Helvetica", 12)
            for line in content:
                numbered_prefixes = tuple(str(i)+"." for i in range(1,10))
                if line.startswith("*") or line.strip().startswith(numbered_prefixes):
                    p.setFillColor(colors.darkblue)
                else:
                    p.setFillColor(colors.black)
                p.drawString(50, y, line)
                y -= 18
                if y < 50:
                    p.showPage()
                    y = height - 50
            y -= 10

        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
    # else:
    #     return HttpResponse("Could not find article div with given dataid", status=404)
    


