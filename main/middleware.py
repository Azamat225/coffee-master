class PanelNoIndexMiddleware:
    """Запрещает индексацию панели управления поисковиками."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/panel/'):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
