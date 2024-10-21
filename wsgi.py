from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from careerMatch import CareerMatch

class SimpleWSGIApp:
    def __init__(self):
        self.api = CareerMatch()
        self.occupations = []  # To store the fetched occupations

    def __call__(self, environ, start_response):
        # Get the request path
        path = environ.get('PATH_INFO', '/')
        
        # Handle the requests
        if path == '/':
            return self.show_form(environ, start_response)
        elif path == '/get_careers':
            return self.get_careers(environ, start_response)
        elif path == '/get_details':
            return self.get_details(environ, start_response)
        
        # Handle 404
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

    def show_form(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"""
        <html>
        <body>
            <h2>Career Search</h2>
            <form method="POST" action="/get_careers">
                <input type="text" name="keyword" placeholder="Occupation Keyword" required><br>
                <input type="text" name="zip_code" placeholder="Zip Code" required><br>
                <input type="submit" value="Search Careers">
            </form>
        </body>
        </html>
        """]

    def get_careers(self, environ, start_response):
        # Get form data
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        keyword = form_data.get('keyword', [''])[0]
        zip_code = form_data.get('zip_code', [''])[0]

        # Fetch careers based on user input
        self.occupations = self.api.find_career(keyword)

        # Create the response
        response_body = '<h2>Choose an Occupation:</h2>'
        response_body += '<form method="POST" action="/get_details">'
        for index, occupation in enumerate(self.occupations):
            response_body += f'<input type="radio" name="onet_id" value="{occupation["OnetCode"]}" required> '
            response_body += f'{occupation["OnetTitle"]}: {occupation["OccupationDescription"]}<br>'
        response_body += f'<input type="hidden" name="zip_code" value="{zip_code}"><br>'
        response_body += '<input type="submit" value="Get Details">'
        response_body += '</form>'

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]
    
    def get_details(self, environ, start_response):
        # Get form data
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        onet_id = form_data.get('onet_id', [''])[0]
        zip_code = form_data.get('zip_code', [''])[0]

        # Fetch detailed occupation data
        occupation_info = self.api.detailed_occupation_data(onet_id, zip_code)

        if not occupation_info:  # Check if we got valid data
            start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            return [b"An error occurred while fetching the occupation details."]

        # Create the response
        response_body = '<h2>Occupation Details:</h2>'
        for key, value in occupation_info.items():
            response_body += f'<strong>{key}:</strong> {value}<br>'

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

# Start the WSGI server
httpd = make_server('', 8000, SimpleWSGIApp())
print("Serving on http://localhost:8000...")
httpd.serve_forever()
