"""
Interview question scheduler for daily automated posting
"""
import random
from datetime import datetime, timedelta
from threading import Timer

from config import logger, settings
from db import DataBase
from interview_questions import get_all_questions


def post_daily_interview_question(bot):
    """Posts a random interview question to the chat"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        db = DataBase()
        
        # Check if we already posted a question today
        existing_question = db.get_daily_question(today)
        if existing_question:
            logger.info(f"Daily question already posted for {today}")
            db.close()
            return
        
        # Get a random unused question
        question_data = db.get_random_unused_question()
        
        if not question_data:
            # If no unused questions, reset all questions and try again
            logger.info("No unused questions left, resetting all questions")
            db.reset_all_questions()
            question_data = db.get_random_unused_question()
        
        if question_data:
            question_id, category, question_text = question_data
            
            # Mark question as used
            db.mark_question_as_used(question_id)
            
            # Save as daily question
            db.save_daily_question(today, question_id, question_text, category)
            
            # Format and send message
            category_emoji = {
                "behavioral": "🧠",
                "soft_skill": "💪", 
                "culture_fit": "🏢",
                "it_specific": "💻"
            }
            
            category_names = {
                "behavioral": "Поведенческий",
                "soft_skill": "Навыки", 
                "culture_fit": "Культура компании",
                "it_specific": "IT-специфичный"
            }
            
            emoji = category_emoji.get(category, "❓")
            category_name = category_names.get(category, category.title())
            
            message = f"Сегодняшний вопрос для подготовки к собеседованию: {question_text} {emoji} Подумай и потренируйся отвечать вслух!"
            
            # Send to the main chat
            if hasattr(settings, 'CHAT_ALERT') and settings.CHAT_ALERT:
                bot.send_message(settings.CHAT_ALERT, message, parse_mode="Markdown")
                logger.info(f"Posted daily interview question: {category} - {question_text[:50]}...")
            else:
                logger.warning("CHAT_ALERT not configured, couldn't send daily question")
                
        else:
            logger.error("Could not get any interview question from database")
            
        db.close()
        
    except Exception as e:
        logger.error(f"Error posting daily interview question: {e}")


def schedule_daily_questions(bot):
    """Schedules daily interview questions"""
    def check_and_post():
        """Check if it's time to post and schedule next check"""
        try:
            now = datetime.now()
            
            # Post at 11:00 AM every day
            target_hour = 11
            target_minute = 0
            
            # Check if it's the right time (within 1 minute window)
            if now.hour == target_hour and now.minute == target_minute:
                post_daily_interview_question(bot)
            
            # Schedule next check in 60 seconds
            timer = Timer(60.0, check_and_post)
            timer.daemon = True
            timer.start()
            
        except Exception as e:
            logger.error(f"Error in interview question scheduler: {e}")
            # Reschedule even if there's an error
            timer = Timer(60.0, check_and_post)
            timer.daemon = True
            timer.start()
    
    # Start the scheduler
    check_and_post()
    logger.info("Interview question scheduler started")


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