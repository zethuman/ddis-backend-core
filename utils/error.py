from django.http import JsonResponse


def error_msg(msg):
    return JsonResponse(data={
        "status": "failed",
        "message": msg
    }, safe=True)