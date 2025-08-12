class SecurityHeaders:
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            return response
