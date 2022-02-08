import datetime

DATE = datetime.date.today()


def year(request):
    """Добавляет переменную с текущим годом."""
    return {'year': DATE.year}
