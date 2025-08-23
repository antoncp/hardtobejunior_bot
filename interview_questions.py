"""
Interview questions for behavioral, soft skill, and culture fit assessments.
These questions are commonly asked in IT industry interviews for junior positions.
"""

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time when you had to learn a new technology quickly. How did you approach it?",
    "Describe a situation where you made a mistake in your code. How did you handle it?",
    "Tell me about a time when you had to work with a difficult team member. How did you resolve it?",
    "Describe a project you're particularly proud of. What made it special?",
    "Tell me about a time when you received constructive criticism. How did you respond?",
    "Describe a situation where you had to meet a tight deadline. How did you manage it?",
    "Tell me about a time when you had to explain a technical concept to a non-technical person.",
    "Describe a situation where you had to adapt to a major change in project requirements.",
    "Tell me about a time when you took initiative to improve a process or solve a problem.",
    "Describe a situation where you had to collaborate with people from different departments.",
    "Tell me about a time when you disagreed with your supervisor or team lead. How did you handle it?",
    "Describe a project where you had to work with incomplete or unclear requirements.",
    "Tell me about a time when you had to balance multiple priorities. How did you manage them?",
    "Describe a situation where you had to learn from failure. What did you take away from it?",
    "Tell me about a time when you went above and beyond what was expected of you.",
    "Describe a situation where you had to give feedback to a peer. How did you approach it?",
    "Tell me about a time when you had to work under pressure. How did you handle the stress?",
    "Describe a situation where you had to convince others to adopt your technical solution.",
    "Tell me about a time when you had to deal with ambiguous requirements. How did you proceed?",
    "Describe a project where you had to work independently with minimal guidance."
]

SOFT_SKILL_QUESTIONS = [
    "How do you stay updated with the latest technology trends and developments?",
    "Describe your approach to debugging a complex problem.",
    "How do you prioritize tasks when everything seems urgent?",
    "What strategies do you use to improve your coding skills?",
    "How do you handle situations where you don't know the answer to a technical question?",
    "Describe your process for code review. What do you look for?",
    "How do you ensure code quality in your projects?",
    "What's your approach to learning a new programming language or framework?",
    "How do you handle interruptions while working on complex tasks?",
    "Describe your method for breaking down large projects into manageable tasks.",
    "How do you stay organized when working on multiple projects simultaneously?",
    "What's your approach to writing documentation for your code?",
    "How do you handle situations where you need to estimate time for unfamiliar tasks?",
    "Describe your process for testing your code before deployment.",
    "How do you approach pair programming or collaborative coding sessions?",
    "What strategies do you use to maintain focus during long coding sessions?",
    "How do you handle technical debt in your projects?",
    "Describe your approach to choosing between multiple technical solutions.",
    "How do you keep track of your learning goals and progress?",
    "What's your process for preparing for technical interviews or coding challenges?"
]

CULTURE_FIT_QUESTIONS = [
    "What motivates you to work in the tech industry?",
    "How do you prefer to receive feedback on your work?",
    "Describe your ideal work environment and team dynamics.",
    "What does work-life balance mean to you?",
    "How do you handle stress and prevent burnout in a fast-paced environment?",
    "What role do you typically play in team projects?",
    "How do you contribute to a positive team culture?",
    "What's your approach to continuous learning and professional development?",
    "How do you handle conflicts or disagreements in a professional setting?",
    "What values are most important to you in a workplace?",
    "How do you prefer to communicate with team members and stakeholders?",
    "Describe a time when you had to adapt to a company's culture or values.",
    "What makes you excited about coming to work each day?",
    "How do you handle situations where you need help or mentorship?",
    "What's your approach to giving and receiving constructive feedback?",
    "How do you contribute to knowledge sharing within a team?",
    "What type of projects or challenges energize you the most?",
    "How do you handle ambiguity and uncertainty in your work?",
    "What's your philosophy on work ownership and accountability?",
    "How do you maintain enthusiasm during routine or less exciting tasks?",
    "What role does diversity and inclusion play in your ideal workplace?",
    "How do you approach building relationships with new team members?",
    "What's your preferred style of leadership and being led?",
    "How do you handle situations where company priorities change frequently?",
    "What aspects of company culture matter most to you when choosing an employer?"
]

IT_SPECIFIC_QUESTIONS = [
    "How do you approach working with legacy code?",
    "Describe your experience with version control and collaborative development.",
    "How do you stay current with security best practices in your development work?",
    "What's your approach to writing maintainable and scalable code?",
    "How do you handle situations where business requirements conflict with technical best practices?",
    "Describe your experience working in an Agile/Scrum environment.",
    "How do you approach performance optimization in your applications?",
    "What's your philosophy on code comments and documentation?",
    "How do you handle technical discussions with non-technical stakeholders?",
    "Describe your approach to choosing technologies for a new project.",
    "How do you balance speed of delivery with code quality?",
    "What's your experience with different development methodologies?",
    "How do you approach mobile-first or responsive design challenges?",
    "Describe your experience with database design and optimization.",
    "How do you handle situations where you need to refactor existing code?",
    "What's your approach to API design and integration?",
    "How do you ensure accessibility in your applications?",
    "Describe your experience with different testing strategies (unit, integration, etc.).",
    "How do you approach monitoring and logging in production applications?",
    "What's your philosophy on technical innovation vs. proven solutions?"
]

def get_all_questions():
    """Returns all interview questions as a single list with categories."""
    questions = []
    
    for q in BEHAVIORAL_QUESTIONS:
        questions.append(("behavioral", q))
    
    for q in SOFT_SKILL_QUESTIONS:
        questions.append(("soft_skill", q))
        
    for q in CULTURE_FIT_QUESTIONS:
        questions.append(("culture_fit", q))
        
    for q in IT_SPECIFIC_QUESTIONS:
        questions.append(("it_specific", q))
    
    return questions

def get_questions_by_category(category):
    """Returns questions filtered by category."""
    category_map = {
        "behavioral": BEHAVIORAL_QUESTIONS,
        "soft_skill": SOFT_SKILL_QUESTIONS,
        "culture_fit": CULTURE_FIT_QUESTIONS,
        "it_specific": IT_SPECIFIC_QUESTIONS
    }
    return category_map.get(category, [])