class RemoveHeaders(object):
    def process_response(self, response):
        del response.headers['Server']
        return response