from django.http import JsonResponse

def info(request):
    return JsonResponse({

  "proyecto": "vamos a la luna",

  "version": "1.0",

  "autor": "kevin ayala supremo"

})