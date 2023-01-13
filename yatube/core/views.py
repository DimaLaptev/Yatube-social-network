from django.shortcuts import render
from http import HTTPStatus


def page_not_found(request, exception):
    return render(request, 'core/404.html',
                  {'path': request.path}, status=HTTPStatus.NOT_FOUND)


def forbidden(request, reason=''):
    return render(request, 'core/403csrf.html',
                  status=HTTPStatus.FORBIDDEN)
