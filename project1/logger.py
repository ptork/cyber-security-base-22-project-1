import traceback

class LogMiddleware():
  def __init__(self, get_response):
    self.get_response = get_response

  # A09:2021 – Security Logging and Monitoring Failures
  def __call__(self, request):
    # This middleware is useful during development, but
    # in production will log every header there is. Including
    # session cookies. If someone has access to the logs they
    # may use it to hijack someones session 
    print(request.headers)
    return self.get_response(request)
