from datetime import datetime, timezone


def utcnow():
    """
    Возвращает текущее время в формате UTC с использованием часового пояса.

    :return: Объект datetime с текущим временем в UTC.
    """
    return datetime.now(tz=timezone.utc)
