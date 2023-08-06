from django.utils.encoding import force_str
from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return force_str(data, encoding=self.charset)


class XMLRenderer(renderers.BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'

    def render(
            self,
            data,
            media_type=None,
            renderer_context=None
    ):
        return force_str(data, encoding=self.charset)
