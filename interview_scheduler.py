"""
Interview questions utilities: database initialization and statistics.
"""
from config import logger
from db import DataBase
from interview_questions import get_all_questions


def initialize_questions_database():
    """Initialize the database with interview questions if it's empty"""
    try:
        db = DataBase()
        
        # Check if questions are already loaded
        stats = db.get_question_stats()
        if stats:
            total_questions = sum(stat[1] for stat in stats)
            logger.info(f"Database already has {total_questions} interview questions")
            db.close()
            return
        
        # Load all questions
        questions = get_all_questions()
        db.populate_interview_questions(questions)
        
        logger.info(f"Loaded {len(questions)} interview questions into database")
        db.close()
        
    except Exception as e:
        logger.error(f"Error initializing questions database: {e}")


def get_question_statistics():
    """Get statistics about interview questions"""
    try:
        db = DataBase()
        stats = db.get_question_stats()
        db.close()
        
        if not stats:
            return "Нет данных о вопросах для собеседования"
        
        message = "📊 **Статистика вопросов для собеседования:**\n\n"
        
        total_all = 0
        used_all = 0
        
        for category, total, used, remaining in stats:
            category_names = {
                "behavioral": "Поведенческие",
                "soft_skill": "Навыки", 
                "culture_fit": "Культура компании",
                "it_specific": "IT-специфичные"
            }
            
            category_name = category_names.get(category, category.title())
            message += f"**{category_name}:**\n"
            message += f"  • Всего: {total}\n"
            message += f"  • Использовано: {used}\n"
            message += f"  • Осталось: {remaining}\n\n"
            
            total_all += total
            used_all += used
        
        message += f"**Итого:** {total_all} вопросов ({used_all} использовано, {total_all - used_all} осталось)"
        
        return message
        
    except Exception as e:
        logger.error(f"Error getting question statistics: {e}")
        return "Ошибка при получении статистики"