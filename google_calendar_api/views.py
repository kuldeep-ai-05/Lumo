from django.http import JsonResponse
from .utils import get_upcoming_events

def calendar_events(request):
    try:
        events = get_upcoming_events()
        return JsonResponse({'events': events})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)