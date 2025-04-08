class MiddlewareToCaptureRequestHeader:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print("This is the header: ",request.headers)
        print("*"*100)
        print("This is the request body: ", request.body.decode('utf-8'))
        response = self.get_response(request)

        # print request data
        print("*"*100)

        print("This is the response: ", response.content.decode('utf-8'))
        print("*"*100)

        # Code to be executed for each request/response after
        # the view is called.

        return response