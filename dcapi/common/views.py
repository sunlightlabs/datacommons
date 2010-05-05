from django.http import HttpResponseBadRequest

def no_format(request, emitter_format):
    return HttpResponseBadRequest('%s is not a valid response format for this method' % emitter_format)