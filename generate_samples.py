"""
generate_samples.py

Generates sample PDF resumes and a sample JD for testing.
Run: python generate_samples.py
"""
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent / "sample_data"
SAMPLE_DIR.mkdir(exist_ok=True)


def create_sample_jd():
    jd = """Senior Python Developer - AI/ML Team

We are looking for an experienced Senior Python Developer to join our AI/ML team.

Requirements:
- 4+ years of experience in Python development
- Strong proficiency in FastAPI, Flask, or Django
- Experience with machine learning frameworks: TensorFlow, PyTorch, or scikit-learn
- Proficiency in NLP libraries: spaCy, NLTK, or Hugging Face Transformers
- Experience with SQL databases (PostgreSQL, MySQL) and NoSQL (MongoDB, Redis)
- Familiarity with Docker, Kubernetes, and CI/CD pipelines
- Experience with AWS or GCP cloud services
- Strong understanding of REST API design and GraphQL
- Experience with pandas, numpy, and data processing pipelines
- Knowledge of Git, GitHub, and Agile/Scrum methodologies
- Bachelor's degree in Computer Science, Engineering, or related field

Responsibilities:
- Design and implement scalable AI/ML pipelines
- Build and maintain REST APIs using FastAPI
- Collaborate with data scientists to productionize ML models
- Optimize database queries and system performance
- Write clean, testable, well-documented code
- Participate in code reviews and technical discussions

Nice to have:
- Experience with Kafka or Apache Spark
- Knowledge of React or Vue.js for frontend integration
- Contributions to open-source projects
- Experience with LLMs and prompt engineering
"""
    (SAMPLE_DIR / "sample_jd.txt").write_text(jd, encoding="utf-8")
    print("✅ Created sample_data/sample_jd.txt")


def create_sample_resumes_txt():
    """Create sample resumes as TXT files (works without reportlab)."""

    resume1 = """John Smith
john.smith@email.com | +1-555-0101 | LinkedIn: linkedin.com/in/johnsmith

SUMMARY
Senior Python Developer with 5 years of experience building scalable AI/ML systems and REST APIs.
Passionate about NLP, machine learning, and cloud-native architectures.

EDUCATION
Bachelor of Technology in Computer Science
State University of Technology, 2018

EXPERIENCE
Senior Python Developer | TechCorp AI | 2021 - Present (3 years)
- Built production ML pipelines using TensorFlow and scikit-learn serving 1M+ predictions/day
- Developed FastAPI microservices with PostgreSQL and Redis caching
- Implemented NLP models using spaCy and Hugging Face Transformers for text classification
- Deployed applications on AWS using Docker and Kubernetes
- Led a team of 4 developers following Agile/Scrum methodology

Python Developer | DataSoft Inc | 2019 - 2021 (2 years)
- Developed REST APIs using Flask and Django
- Built data processing pipelines with pandas and numpy
- Worked with MongoDB and MySQL databases
- Implemented CI/CD pipelines using GitHub Actions

SKILLS
Python, FastAPI, Flask, Django, TensorFlow, PyTorch, scikit-learn, spaCy, NLTK,
Hugging Face Transformers, pandas, numpy, PostgreSQL, MySQL, MongoDB, Redis,
Docker, Kubernetes, AWS, GCP, Git, GitHub, REST API, GraphQL, Agile, Scrum,
machine learning, deep learning, NLP, natural language processing, SQL

PROJECTS
- AI Resume Screener: Built an NLP-based resume screening system using BERT and cosine similarity
- Sentiment Analysis API: FastAPI service for real-time sentiment analysis using Transformers
- Data Pipeline: Apache Kafka + Spark pipeline processing 10GB/day of user events
"""

    resume2 = """Priya Sharma
priya.sharma@email.com | +1-555-0202 | GitHub: github.com/priyasharma

SUMMARY
Python Developer with 2 years of experience in web development and basic machine learning.
Eager to grow in AI/ML domain.

EDUCATION
Bachelor of Science in Information Technology
City College, 2022

EXPERIENCE
Junior Python Developer | WebStartup Ltd | 2022 - Present (2 years)
- Developed REST APIs using Flask
- Worked with MySQL and basic SQL queries
- Used pandas for data analysis tasks
- Collaborated using Git and GitHub

Intern | CodeBase Solutions | 2021 - 2022
- Learned Python basics and Django framework
- Assisted in building simple CRUD applications

SKILLS
Python, Flask, Django, MySQL, SQL, pandas, numpy, Git, GitHub, HTML, CSS, JavaScript,
REST API, basic machine learning, scikit-learn

PROJECTS
- Student Management System: Django web app with MySQL backend
- Data Analysis Dashboard: pandas + matplotlib for sales data visualization
"""

    resume3 = """Alex Johnson
alex.j@email.com | +1-555-0303

SUMMARY
Full Stack Developer and ML Engineer with 6 years of experience.
Expert in Python, cloud architecture, and production ML systems.

EDUCATION
Master of Science in Computer Science (Machine Learning)
Tech University, 2018

Bachelor of Engineering in Software Engineering
Engineering College, 2016

EXPERIENCE
Lead ML Engineer | AI Innovations Corp | 2020 - Present (4 years)
- Architected end-to-end ML platform on AWS using SageMaker and Docker
- Built NLP pipelines using BERT, GPT, and Hugging Face Transformers
- Developed FastAPI services handling 5M+ requests/day with PostgreSQL and Redis
- Implemented Apache Kafka for real-time data streaming
- Led Agile team of 8 engineers, conducted code reviews

Python Developer | CloudTech Solutions | 2018 - 2020 (2 years)
- Built microservices with FastAPI and Flask
- Worked with PostgreSQL, MongoDB, and Redis
- Deployed on GCP using Kubernetes and Docker
- Implemented CI/CD with Jenkins and GitHub Actions

SKILLS
Python, FastAPI, Flask, Django, TensorFlow, PyTorch, scikit-learn, XGBoost,
spaCy, NLTK, Hugging Face Transformers, BERT, GPT, LLM, langchain,
pandas, numpy, matplotlib, PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch,
Docker, Kubernetes, AWS, GCP, Azure, Kafka, Apache Spark, Airflow,
Git, GitHub, GraphQL, REST API, Agile, Scrum, machine learning, deep learning,
NLP, natural language processing, computer vision, system design

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Google Cloud Professional Data Engineer
"""

    (SAMPLE_DIR / "resume_john_smith.txt").write_text(resume1, encoding="utf-8")
    (SAMPLE_DIR / "resume_priya_sharma.txt").write_text(resume2, encoding="utf-8")
    (SAMPLE_DIR / "resume_alex_johnson.txt").write_text(resume3, encoding="utf-8")
    print("✅ Created 3 sample resumes in sample_data/")


def create_sample_resumes_pdf():
    """Create sample resumes as PDF files using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT

        resumes = {
            "resume_john_smith.pdf": (SAMPLE_DIR / "resume_john_smith.txt").read_text(encoding="utf-8"),
            "resume_priya_sharma.pdf": (SAMPLE_DIR / "resume_priya_sharma.txt").read_text(encoding="utf-8"),
            "resume_alex_johnson.pdf": (SAMPLE_DIR / "resume_alex_johnson.txt").read_text(encoding="utf-8"),
        }

        styles = getSampleStyleSheet()
        body_style = ParagraphStyle('body', fontSize=10, leading=14, fontName='Helvetica')
        heading_style = ParagraphStyle('heading', fontSize=14, leading=18, fontName='Helvetica-Bold')

        for filename, content in resumes.items():
            doc = SimpleDocTemplate(str(SAMPLE_DIR / filename), pagesize=letter,
                                    leftMargin=0.75*inch, rightMargin=0.75*inch,
                                    topMargin=0.75*inch, bottomMargin=0.75*inch)
            story = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if i == 0:
                    story.append(Paragraph(line, heading_style))
                elif line.strip() == '':
                    story.append(Spacer(1, 6))
                elif line.isupper() and len(line) < 40:
                    story.append(Spacer(1, 4))
                    story.append(Paragraph(f"<b>{line}</b>", body_style))
                else:
                    story.append(Paragraph(line.replace('&', '&amp;').replace('<', '&lt;'), body_style))
            doc.build(story)
            print(f"✅ Created sample_data/{filename}")

    except ImportError:
        print("⚠️  reportlab not installed. Using TXT resumes instead.")
        print("   Install with: pip install reportlab")


if __name__ == "__main__":
    print("🔧 Generating sample data...")
    create_sample_jd()
    create_sample_resumes_txt()
    create_sample_resumes_pdf()
    print("\n✅ Sample data ready in sample_data/")
    print("   Files: sample_jd.txt, resume_*.txt, resume_*.pdf")
