from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from careermatch import CareerMatch

class SimpleWSGIApp:
    def __init__(self):
        self.api = CareerMatch()
        self.occupations = []

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        if path == '/':
            return self.show_form(environ, start_response)
        elif path == '/get_careers':
            return self.get_careers(environ, start_response)
        elif path == '/get_details':
            return self.get_details(environ, start_response)

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

    def show_form(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"""
        <html>
        <head>
            <link rel="stylesheet" href="styles.css"> <!-- Link to your CSS file -->
            <title>Career Search</title>
        </head>
        <body>
            <div class="careers-background">
                <div class="careers-section">
                    <h2>Career Search</h2>
                    <form method="POST" action="/get_careers">
                        <input type="text" name="keyword" placeholder="Occupation Keyword" required><br>
                        <input type="text" name="zip_code" placeholder="Zip Code" required><br>
                        <input type="submit" value="Search Careers">
                    </form>
                </div>
            </div>
        </body>
        </html>
        """]

    def get_careers(self, environ, start_response):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        keyword = form_data.get('keyword', [''])[0]
        zip_code = form_data.get('zip_code', [''])[0]

        self.occupations = self.api.find_career(keyword)

        response_body = """
        <html>
        <head>
            <link rel="stylesheet" href="styles.css">
            <title>Career Search Results</title>
        </head>
        <body>
            <div class="careers-background">
                <div class="careers-section">
                    <h2>Choose an Occupation:</h2>
                    <form method="POST" action="/get_details">
        """
        for index, occupation in enumerate(self.occupations):
            response_body += f'<input type="radio" name="onet_id" value="{occupation["OnetCode"]}" required> '
            response_body += f'{occupation["OnetTitle"]}: {occupation["OccupationDescription"]}<br>'
        response_body += f'<input type="hidden" name="zip_code" value="{zip_code}"><br>'
        response_body += '<input type="submit" value="Get Details">'
        response_body += '</form></div></div></body></html>'

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]
    
    def get_details(self, environ, start_response):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        onet_id = form_data.get('onet_id', [''])[0]
        zip_code = form_data.get('zip_code', [''])[0]

        occupation_info = self.api.detailed_occupation_data(onet_id, zip_code)

        if not occupation_info:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            return [b"An error occurred while fetching the occupation details."]

        response_body = '<html><head><link rel="stylesheet" href="styles.css"><title>Occupation Details</title></head><body>'
        response_body += '<div class="careers-background"><div class="careers-section"><h2>Occupation Details:</h2>'

        # Keep the rest of the occupation details as is
        for key, value in occupation_info.items():
            response_body += f'<strong>{key}:</strong> {value}<br>'

        # Add the code to handle the Education section
        education_info = occupation_info.get('Education', {})
        if education_info:
            response_body += '<strong>Education:</strong><ul>'
            for education_type in education_info.get('EducationType', []):
                level = education_type.get('EducationLevel', 'Not available')
                value = education_type.get('Value', 'N/A')
                response_body += f'<li>{level}: {value}%</li>'
            response_body += '</ul>'
            education_title = education_info.get('EducationTitle', 'Not available')
            response_body += f'<strong>Minimum Education Requirement:</strong> {education_title}<br>'
        else:
            response_body += '<strong>Education:</strong> Not available<br>'

        # Add the code to handle Related Careers
        related_careers = occupation_info.get('Related Careers', {})
        if related_careers:
            response_body += '<strong>Related Careers:</strong><ul>'
            for career_code, career_title in related_careers.items():
                response_body += f'<li>{career_code}: {career_title}</li>'
            response_body += '</ul>'
        else:
            response_body += '<strong>Related Careers:</strong> Not available<br>'

        # Add the code to handle Training Programs
        training_programs = occupation_info.get('Training Programs', [])
        if training_programs:
            response_body += '<strong>Training Programs:</strong><ul>'
            for program in training_programs:
                response_body += f'<li>{program}</li>'
            response_body += '</ul>'
        else:
            response_body += '<strong>Training Programs:</strong> Not available<br>'

        

        response_body += '</div></div></body></html>'

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]




# Start the WSGI server
httpd = make_server('', 8000, SimpleWSGIApp())
print("Serving on http://localhost:8000...")
httpd.serve_forever()
