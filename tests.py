import os

from db import DataBase
from language_utilities import choose_noun_case


def test_noun_case():
    "Noun case function test"
    assert choose_noun_case(1) == '1 балл'
    assert choose_noun_case(3) == '3 балла'
    assert choose_noun_case(12) == '12 баллов'
    assert choose_noun_case(34) == '34 балла'
    assert choose_noun_case(256) == '256 баллов'


def test_database():
    "Pure database test"
    if os.path.exists("db/test.sqlite"):
        os.remove('db/test.sqlite')
    db = DataBase('test.sqlite')
    db.create_database()
    db.save_points("Бекендор", 100)
    db.save_points("Фрондерин", 15)
    db.save_points("Бекендор", 50)
    assert db.get_all_points() == [('Бекендор', 150), ('Фрондерин', 15)]
    db.close()


test_noun_case()
test_database()