from django.http import JsonResponse


# Create your views here.
def health_check(request):
    return JsonResponse({"status_code": 200, "detail": "ok", "result": "working"})
