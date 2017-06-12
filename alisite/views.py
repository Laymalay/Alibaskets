import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template.loader import get_template


# def display_meta(request):
#     values = request.META.items()
#     values.sort()
#     html = []
#     for k, v in values:
#         html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
#     return HttpResponse('<table>%s</table>' % '\n'.join(html))
# def hello(request):
#     return HttpResponse('Hello world')
# def current_datetime(request):
#     now = datetime.datetime.now()
#     return render_to_response('current_datetime.html', {'current_date': now})
# def hours_ahead(request, offset):
#     try:
#         offset = int(offset)
#     except ValueError:
#         raise Http404()
#     dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
#     return render_to_response('hours_ahead.html', {'hour_offset': offset, 'next_time':dt })