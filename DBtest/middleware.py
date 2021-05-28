class RemoveHeaders(object):
    def process_response(self, request, response):
        del response['Server']
        return response