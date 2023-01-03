from datetime import datetime

def year(request):
    """Добавляет переменную с текущим годом."""
    # d = datetime.now()
    return {
       'year': datetime.now().year
    }
