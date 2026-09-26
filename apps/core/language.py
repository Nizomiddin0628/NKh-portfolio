"""Language selection.

Django normally redirects "/" to the browser's language, so a visitor with a
Russian browser lands on /ru/. The site should open in English unless the
visitor chose otherwise:

- the browser's Accept-Language header is ignored
- opening any /uz/ or /ru/ page stores that choice in the language cookie,
  so "/" sends the visitor back to it next time
"""
from django.conf import settings

LANGUAGE_CODES = {code for code, _name in settings.LANGUAGES}
ONE_YEAR = 60 * 60 * 24 * 365


class DefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META.pop("HTTP_ACCEPT_LANGUAGE", None)
        response = self.get_response(request)

        prefix = request.path.strip("/").split("/", 1)[0]
        cookie = settings.LANGUAGE_COOKIE_NAME
        if prefix in LANGUAGE_CODES and request.COOKIES.get(cookie) != prefix:
            response.set_cookie(cookie, prefix, max_age=ONE_YEAR, samesite="Lax")
        return response
