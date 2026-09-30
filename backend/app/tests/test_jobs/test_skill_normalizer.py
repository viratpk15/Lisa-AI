"""
Tests for Skill Normalizer Engine
"""

from app.Jobs.services.skill_normalizer import skill_normalizer


def test_normalize_python_variations():
    assert skill_normalizer.normalize_single("python") == "Python"
    assert skill_normalizer.normalize_single("Python 3") == "Python"
    assert skill_normalizer.normalize_single("python3") == "Python"
    assert skill_normalizer.normalize_single("py") == "Python"


def test_normalize_react_variations():
    assert skill_normalizer.normalize_single("react") == "React"
    assert skill_normalizer.normalize_single("React.js") == "React"
    assert skill_normalizer.normalize_single("reactjs") == "React"


def test_normalize_ai_ml_variations():
    assert skill_normalizer.normalize_single("ml") == "Machine Learning"
    assert skill_normalizer.normalize_single("machine learning") == "Machine Learning"
    assert skill_normalizer.normalize_single("deep learning") == "Deep Learning"
    assert skill_normalizer.normalize_single("dl") == "Deep Learning"
    assert skill_normalizer.normalize_single("nlp") == "NLP"
    assert skill_normalizer.normalize_single("natural language processing") == "NLP"
    assert skill_normalizer.normalize_single("rag") == "RAG"


def test_normalize_devops_cloud_variations():
    assert skill_normalizer.normalize_single("k8s") == "Kubernetes"
    assert skill_normalizer.normalize_single("kubernetes") == "Kubernetes"
    assert skill_normalizer.normalize_single("amazon web services") == "AWS"
    assert skill_normalizer.normalize_single("aws") == "AWS"
    assert skill_normalizer.normalize_single("docker") == "Docker"
    assert skill_normalizer.normalize_single("postgres") == "PostgreSQL"
    assert skill_normalizer.normalize_single("postgresql") == "PostgreSQL"


def test_normalize_list_and_deduplicate():
    raw = ["python", "Python 3", "React.js", "react", "ML", "Machine Learning", "FastAPI", "fast api"]
    normalized = skill_normalizer.normalize_list(raw)
    assert normalized == ["Python", "React", "Machine Learning", "FastAPI"]


def test_categorize_skills():
    skills = ["Python", "TypeScript", "Machine Learning", "PyTorch", "React", "FastAPI", "PostgreSQL", "Docker", "Git"]
    categories = skill_normalizer.categorize_skills(skills)

    assert "Python" in categories.programming_languages
    assert "TypeScript" in categories.programming_languages
    assert "Machine Learning" in categories.ai_ml_skills
    assert "PyTorch" in categories.ai_ml_skills
    assert "React" in categories.frameworks
    assert "FastAPI" in categories.frameworks
    assert "PostgreSQL" in categories.databases
    assert "Docker" in categories.cloud_devops
    assert "Git" in categories.tools
