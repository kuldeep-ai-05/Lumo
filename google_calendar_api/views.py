from django.http import JsonResponse
from .utils import get_upcoming_events
import traceback # Import traceback

def calendar_events(request):
    try:
        events = get_upcoming_events()
        return JsonResponse({'events': events})
    except Exception as e:
        # Include traceback for debugging purposes
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)