from django.http import HttpResponse


def api_root(request):
    """Placeholder API welcome endpoint for the initial project scaffold."""
    return HttpResponse('FoodShare AI API is ready to be expanded.')
