import json
from datetime import datetime, timedelta, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import routing
from planning.service import generate_plan

@csrf_exempt
@require_POST
def plan(request):
    try:
        b = json.loads(request.body)
        dep = datetime.fromisoformat(b["departure"].replace("Z", "+00:00"))
        dep = dep if dep.tzinfo else dep.replace(tzinfo=timezone.utc)
        load, step = float(b["load_lb"]), int(b.get("interval_mi", 25))
        if step not in (10, 25, 50): raise ValueError("interval_mi must be 10, 25 or 50")
        if not 0 <= load <= 100000: raise ValueError("load_lb must be 0-100,000")
        if dep < datetime.now(timezone.utc) - timedelta(hours=1): raise ValueError("Departure is in the past")
        if dep > datetime.now(timezone.utc) + timedelta(days=14): raise ValueError("Forecast covers 14 days max")
        o, d = routing.geocode(b["origin"]), routing.geocode(b["destination"])
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Upstream service error: {e}"}, status=502)

    try:
        res = generate_plan(o, d, dep, load, step)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=502)
    
    return JsonResponse(res)
