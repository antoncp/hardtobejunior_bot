from datetime import datetime, timedelta, timezone


def get_time(shift=None):
    """Returns real time. UTC + shift in hours."""
    now = datetime.now(timezone.utc)
    if shift:
        delta = timedelta(hours=shift, minutes=0)
        now = now + delta
    return now


def choose_noun_case(score, word="балл"):
    """Provides correct endings for words, based on number"""
    ending = ""
    remainder = score % 10
    if (
        remainder >= 5
        or remainder == 0
        or (score > 10 and 10 < int(str(score)[-2:]) < 20)
    ):
        ending = "ов"
    elif 1 < remainder < 5:
        ending = "а"
    return f"{score} {word}{ending}"
