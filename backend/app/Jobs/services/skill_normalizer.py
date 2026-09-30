"""
Jarvis AIOS — Skill Normalizer Engine
--------------------------------------
Normalizes skill variations, abbreviations, and aliases to standard canonical forms.
e.g. "python", "Python 3", "Python3" -> "Python"
     "react.js", "ReactJS", "React" -> "React"
     "ml", "machine learning" -> "Machine Learning"
"""

import re
from typing import Dict, List, Set
from app.Jobs.models.candidate_profile import SkillCategory

# Canonical skill mappings (alias lowercase -> canonical title)
CANONICAL_SKILL_MAP: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "python 3": "Python",
    "python3": "Python",
    "py": "Python",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "dart": "Dart",
    "scala": "Scala",
    "r": "R",
    "sql": "SQL",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "bash": "Bash",
    "shell": "Shell Scripting",

    # AI / ML / Data Science
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "large language models": "LLMs",
    "llm": "LLMs",
    "llms": "LLMs",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "reinforcement learning": "Reinforcement Learning",
    "rl": "Reinforcement Learning",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "llamaindex": "LlamaIndex",
    "llama-index": "LlamaIndex",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "transformers": "Transformers",
    "opencv": "OpenCV",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",

    # Web & App Frameworks
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "nuxt": "Nuxt.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "svelte": "Svelte",
    "sveltekit": "SvelteKit",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",

    # Databases
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "neo4j": "Neo4j",
    "pinecone": "Pinecone",
    "chromadb": "ChromaDB",
    "chroma": "ChromaDB",
    "weaviate": "Weaviate",
    "qdrant": "Qdrant",
    "vector database": "Vector Databases",
    "vector dbs": "Vector Databases",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "unix": "Linux",
    "serverless": "Serverless",

    # Tools & Platforms
    "git": "Git",
    "github": "Git",
    "gitlab": "GitLab",
    "jira": "Jira",
    "confluence": "Confluence",
    "postman": "Postman",
    "figma": "Figma",
    "tableau": "Tableau",
    "powerbi": "Power BI",
    "power bi": "Power BI",
}

# Skill Categorization Lookups
CATEGORY_LOOKUP = {
    "programming_languages": {
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Dart", "Scala", "R",
        "SQL", "HTML5", "CSS3", "Bash", "Shell Scripting"
    },
    "ai_ml_skills": {
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "LLMs",
        "Generative AI", "RAG", "Reinforcement Learning", "TensorFlow", "PyTorch",
        "Keras", "Scikit-Learn", "Pandas", "NumPy", "SciPy", "LangChain",
        "LangGraph", "LlamaIndex", "Hugging Face", "Transformers", "OpenCV",
        "XGBoost", "LightGBM"
    },
    "frameworks": {
        "React", "Next.js", "Vue.js", "Nuxt.js", "Angular", "Svelte", "SvelteKit",
        "FastAPI", "Flask", "Django", "Node.js", "Express.js", "NestJS",
        "Spring Boot", "GraphQL", "REST APIs", "Tailwind CSS"
    },
    "databases": {
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "Neo4j", "Pinecone", "ChromaDB", "Weaviate",
        "Qdrant", "Vector Databases"
    },
    "cloud_devops": {
        "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible",
        "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "Linux", "Serverless"
    },
    "tools": {
        "Git", "GitLab", "Jira", "Confluence", "Postman", "Figma", "Tableau", "Power BI"
    }
}


class SkillNormalizer:
    """Normalizes skill aliases, clean punctuation, and categorizes technical competencies."""

    def normalize_single(self, skill: str) -> str:
        """Normalize a single skill string to its canonical form, or capitalize nicely if unknown."""
        cleaned = skill.strip().lower()
        # Remove trailing punctuation or parentheticals like "Python (expert)"
        cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned).strip()
        cleaned = re.sub(r"[,;]+$", "", cleaned).strip()

        if cleaned in CANONICAL_SKILL_MAP:
            return CANONICAL_SKILL_MAP[cleaned]

        # Check with hyphens replaced with spaces or vice versa
        alt_cleaned = cleaned.replace("-", " ")
        if alt_cleaned in CANONICAL_SKILL_MAP:
            return CANONICAL_SKILL_MAP[alt_cleaned]

        # Return title-cased fallback if unknown
        return skill.strip().title()

    def normalize_list(self, skills: List[str]) -> List[str]:
        """Normalize a list of skills, deduplicating while preserving canonical casing."""
        seen: Set[str] = set()
        result: List[str] = []

        for s in skills:
            if not s or not s.strip():
                continue
            canonical = self.normalize_single(s)
            canonical_lower = canonical.lower()
            if canonical_lower not in seen:
                seen.add(canonical_lower)
                result.append(canonical)

        return result

    def categorize_skills(self, normalized_skills: List[str]) -> SkillCategory:
        """Organize a list of normalized skills into structured domain categories."""
        cat = SkillCategory()

        for skill in normalized_skills:
            if skill in CATEGORY_LOOKUP["programming_languages"]:
                if skill not in cat.programming_languages:
                    cat.programming_languages.append(skill)
            elif skill in CATEGORY_LOOKUP["ai_ml_skills"]:
                if skill not in cat.ai_ml_skills:
                    cat.ai_ml_skills.append(skill)
            elif skill in CATEGORY_LOOKUP["frameworks"]:
                if skill not in cat.frameworks:
                    cat.frameworks.append(skill)
            elif skill in CATEGORY_LOOKUP["databases"]:
                if skill not in cat.databases:
                    cat.databases.append(skill)
            elif skill in CATEGORY_LOOKUP["cloud_devops"]:
                if skill not in cat.cloud_devops:
                    cat.cloud_devops.append(skill)
            elif skill in CATEGORY_LOOKUP["tools"]:
                if skill not in cat.tools:
                    cat.tools.append(skill)
            else:
                # Default unknown technical skills to tools or frameworks
                if skill not in cat.tools:
                    cat.tools.append(skill)

        return cat


skill_normalizer = SkillNormalizer()
