import os
import unittest
from unittest.mock import Mock

from config import settings
from db import DataBase
from language_utilities import choose_noun_case
from main import handle_text, start

settings.DEBUG = True


def test_noun_case():
    "Noun case function test"
    assert choose_noun_case(1) == "1 балл"
    assert choose_noun_case(3) == "3 балла"
    assert choose_noun_case(12) == "12 баллов"
    assert choose_noun_case(34) == "34 балла"
    assert choose_noun_case(256) == "256 баллов"


def test_database():
    "Pure database test"
    if os.path.exists("db/tests.sqlite"):
        os.remove("db/tests.sqlite")
    db = DataBase()
    db.create_database()
    db.save_points("Бекендор", 100)
    db.save_points("Фрондерин", 15)
    db.save_points("Бекендор", 50)
    assert db.get_all_points() == [("Бекендор", 150), ("Фрондерин", 15)]
    db.close()


class TestTelebot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = DataBase()
        db.create_database()
        db.close()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("db/tests.sqlite"):
            os.remove("db/tests.sqlite")

    def setUp(self):
        self.message = Mock()
        self.message.chat.id = 82176433
        self.message.from_user.id = 82176433

    def tearDown(self):
        pass

    def test_start_command(self):
        """Tests start message of the bot"""
        self.assertTrue(start(self.message).text.startswith("I'am watching"))

    def test_adding_score(self):
        """Tests adding new score to the faculties (Backendor in this case)"""
        self.message.text = "Факультету бекендеров начислить 20 баллов"
        self.assertTrue(
            handle_text(self.message).text.startswith(
                "Фaкультет Бекендор получает 20 баллов"
            )
        )

    def test_subtracting_score(self):
        """Tests subtracting score (Fronderin in this case)"""
        self.message.text = "Минус 10 баллов факультету фронтендеров"
        self.assertTrue(
            handle_text(self.message).text.startswith(
                "Фaкультет Фрондерин теряет -10 баллов"
            )
        )


if __name__ == "__main__":
    test_noun_case()
    test_database()
    unittest.main(verbosity=2)
