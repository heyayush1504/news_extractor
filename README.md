<<<<<<< HEAD
# Digital Skeptic AI

A Django-based web application that performs critical analysis of news articles using AI. The application analyzes news articles for credibility, bias, and potential misinformation, generating detailed PDF reports stored in the `pdfs` folder.

## Features

- Accepts news article URLs via POST request
- Performs comprehensive analysis of article content
- Generates detailed PDF reports including:
  - Core claims analysis
  - Counter-arguments identification
  - Entity recognition
  - Language tone analysis
  - Red flags detection
  - Verification questions

## Project Setup

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Virtual environment (recommended)
- OpenAI API key (sign up at https://platform.openai.com)

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd Darwix-Interview
```

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

5. Run the development server:
```bash
python manage.py runserver
```

## Usage

The application exposes an API endpoint that accepts POST requests:

```bash
POST http://localhost:8000/
Content-Type: application/x-www-form-urlencoded

url=<news-article-url>
```

### Example using cURL:
```bash
curl -X POST -d "url=https://example.com/article" http://localhost:8000/
```

### Response

- The API processes the article and generates a PDF report
- Reports are stored in the `pdfs` folder
- The API returns a success message with details about the generated report

## Project Structure

```
├── digital_skeptic_ai/    # Main application directory
│   ├── views.py          # Core logic and API endpoint
│   ├── urls.py           # URL routing
│   └── models.py         # Database models
├── .env                  # Environment variables (API keys)
├── .gitignore           # Git ignore file
├── pdfs/                 # Generated PDF reports
├── prompts/              # AI analysis prompt templates
│   ├── core_claims.txt
│   ├── counter_argument.txt
│   ├── entity_recognition.txt
│   ├── language_tone.txt
│   ├── red_flags.txt
│   └── verification_questions.txt
├── project/              # Django project settings
├── manage.py            # Django management script
└── requirements.txt     # Project dependencies
```

## Result Location

Generated PDF reports can be found in the `pdfs` folder. Each report is named based on the analyzed article and includes:
- Critical analysis of the article
- Identified potential biases
- Fact-checking suggestions
- Overall credibility assessment


=======
# news_extractor
>>>>>>> 3c233087cc709eda8ee698525ab947c3d7a864a8
