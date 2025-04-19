import json

class MiddlewareToCaptureRequestHeader:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request headers
        print("*" * 100)
        print("📥 Headers:", request.headers)
        print("*" * 100)

        # Log request body
        try:
            body = request.body.decode('utf-8')
            print("📥 Body:", body)
        except Exception as e:
            print("⚠️ Could not decode request body:", e)

        response = self.get_response(request)
        print("*" * 100)

        # Log JSON response only
        content_type = response.get('Content-Type', '')

        if 'application/json' in content_type:
            try:
                json_body = json.loads(response.content)
                pretty = json.dumps(json_body, indent=2)
                # print("📤 JSON Response:\n", pretty)
            except Exception as e:
                print("⚠️ Could not parse JSON response:", e)
        else:
            print("⚠️ Response is not JSON. Skipping output.")

        print("*" * 100)

        return response
