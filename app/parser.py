import re
import pdfplumber
import docx
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

COMMON_SKILLS = {
    "python", "flask", "django", "postgresql", "mysql", "sqlite", "docker", "git",
    "javascript", "typescript", "react", "vue", "angular", "node.js", "c++", "c#",
    "java", "html", "css", "tailwind", "rest api", "graphql", "aws", "gcp", "azure",
    "linux", "pandas", "numpy", "machine learning", "nlp", "spacy", "scikit-learn"
}

DEGREE_TERMS = [
    "bachelor", "b.tech", "b.e", "b.sc", "bca", 
    "master", "m.tech", "m.sc", "mca", "ph.d", 
    "degree", "computer science", "engineering"
]

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(filepath):
    if filepath.lower().endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif filepath.lower().endswith(".docx"):
        return extract_text_from_docx(filepath)
    return ""

def extract_contact_info(text):
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    email = emails[0] if emails else None
    phone = phones[0] if phones else None
    return email, phone

def extract_name(text):
    doc = nlp(text[:1000])
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.strip().split()) <= 4:
            return ent.text.strip()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[0] if lines else "Unknown"

def extract_skills(text):
    doc = nlp(text.lower())
    found_skills = set()

    for token in doc:
        if token.text in COMMON_SKILLS:
            found_skills.add(token.text.title())

    lowered = text.lower()
    for skill in COMMON_SKILLS:
        if " " in skill and skill in lowered:
            found_skills.add(skill.title())

    return list(found_skills)

def extract_education(text):
    found_education = []
    for line in text.split("\n"):
        line_clean = line.strip()
        if any(term in line_clean.lower() for term in DEGREE_TERMS):
            if len(line_clean) < 120 and line_clean not in found_education:
                found_education.append(line_clean)
    return " | ".join(found_education[:3]) if found_education else "Not Specified"

def parse_resume(filepath):
    text = extract_text(filepath)
    email, phone = extract_contact_info(text)
    name = extract_name(text)
    skills = extract_skills(text)
    education = extract_education(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": ", ".join(skills),
        "education": education,
        "raw_text": text
    }
