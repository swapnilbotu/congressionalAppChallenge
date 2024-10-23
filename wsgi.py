from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from careermatch import CareerMatch
import os
import json
from careerMatchAIChatbot import CareerChatbot  # Adjust the import based on your actual class/function

class SimpleWSGIApp:
    def __init__(self):
        self.api = CareerMatch()
        # Initialize CareerChatbot with default values
        self.chatbot = CareerChatbot("Software Engineer", "95678")  # Replace with actual values or adjust accordingly
        self.occupations = []

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        if path == '/':
            return self.serve_html(environ, start_response, 'career.html')
        elif path == '/index.html':  
            return self.serve_html(environ, start_response, 'index.html')  
        elif path == '/aboutus.html':  
            return self.serve_html(environ, start_response, 'aboutus.html')  
        elif path == '/get_careers':
            if environ['REQUEST_METHOD'] == 'POST':
                return self.get_careers(environ, start_response)
            else:  
                return self.show_career_form(environ, start_response)
        elif path == '/get_details':
            return self.get_details(environ, start_response)
        elif path == '/chatbot':  
            if environ['REQUEST_METHOD'] == 'POST':
                return self.get_chatbot_response(environ, start_response)
            else:
                start_response('405 Method Not Allowed', [('Content-Type', 'text/html')])
                return [b"Method not allowed."]

        elif path == '/styles.css':
            return self.serve_static(environ, start_response)

    def render_navbar(self):
        return """
        <nav>
            <ul>
                <li><a href="/index.html">Home</a></li>
                <li><a href="/aboutus.html">About Us</a></li>
                <li><a href="/get_careers">Career Finder</a></li>
            </ul>
        </nav>
        """

    def show_career_form(self, environ, start_response):
        response_body = f"""
        <html>
        <head>
            <link rel="stylesheet" href="styles.css">
            <title>Career Finder</title>
        </head>
        <body>
            <div class="careers-background">
                <div class="careers-section">
                    <h2>Find Your Career</h2>
                    <form method="POST" action="/get_careers">
                        <label for="keyword">Keyword:</label>
                        <input type="text" id="keyword" name="keyword" required><br>
                        <label for="zip_code">Zip Code:</label>
                        <input type="text" id="zip_code" name="zip_code" required><br>
                        <input type="submit" value="Search">
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    def get_careers(self, environ, start_response):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        keyword = form_data.get('keyword', [''])[0]
        zip_code = form_data.get('zip_code', [''])[0]

        self.occupations = self.api.find_career(keyword)

        job_listings = "".join(
            f"""
            <div class="job-listing">
                <input type="radio" name="onet_id" value="{occupation["OnetCode"]}" required>
                <h3>{occupation["OnetTitle"]}</h3>
                <p>{occupation["OccupationDescription"]}</p>
            </div>
            """ for occupation in self.occupations
        )

        response_body = f"""
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
                        <div class="job-listings">
                            {job_listings}
                        </div>
                        <input type="hidden" name="zip_code" value="{zip_code}">
                        <input type="submit" value="Get Details">
                    </form>
                </div>
            </div>
        </body>
        </html>
        """

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    def get_details(self, environ, start_response):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        print("Form data received:", form_data)

        onet_id_list = form_data.get('onet_id', [])
        zip_code_list = form_data.get('zip_code', [])

        print("onet_id_list:", onet_id_list)
        print("zip_code_list:", zip_code_list)

        onet_id = onet_id_list[0] if onet_id_list else None
        zip_code = zip_code_list[0] if zip_code_list else None

        if not onet_id:
            start_response('400 Bad Request', [('Content-Type', 'text/html')])
            return [b"Error: No occupation selected. Please go back and select an occupation."]

        occupation_info = self.api.detailed_occupation_data(onet_id, zip_code)

        if not occupation_info:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            return [b"An error occurred while fetching the occupation details."]

        details_content = '<div class="careers-background"><div class="careers-section"><h2>Occupation Details:</h2>'

        for key, value in occupation_info.items():
            if key not in ['Related Careers', 'Training Programs', 'Tasks']:
                details_content += f'<strong>{key}:</strong> {value}<br><br>'

        related_careers = occupation_info.get('Related Careers', {})
        if related_careers:
            details_content += '<strong>Related Careers:</strong><ul>'
            for career_code, career_title in related_careers.items():
                details_content += f'<li>{career_code}: {career_title}</li>'
            details_content += '</ul><br>'
        else:
            details_content += '<strong>Related Careers:</strong> Not available<br><br>'

        tasks = occupation_info.get('Tasks', [])
        if tasks:
            details_content += '<strong>Tasks:</strong><ul>'
            for task in tasks:
                details_content += f'<li>{task}</li>'
            details_content += '</ul><br>'
        else:
            details_content += '<strong>Tasks:</strong> Not available<br><br>'

        training_programs = occupation_info.get('Training Programs', [])
        if training_programs:
            details_content += '<strong>Training Programs:</strong><ul>'
            for program in training_programs:
                details_content += f'<li>{program}</li>'
            details_content += '</ul><br>'
        else:
            details_content += '<strong>Training Programs:</strong> Not available<br><br>'

        details_content += '</div></div></body></html>'

        response_body = f'<html><head><link rel="stylesheet" href="styles.css"><title>Occupation Details</title></head><body>{details_content}'

        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    def get_chatbot_response(self, environ, start_response):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
        data = json.loads(post_data)
        user_input = data.get('message', '')

        # Fetch the chatbot response from the chatbot instance
        response = self.chatbot.get_response(user_input)  # Ensure this method matches your chatbot's implementation

        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({"response": response}).encode('utf-8')]

    def serve_static(self, environ, start_response):
        path = environ.get('PATH_INFO', '').lstrip('/')
        full_path = os.path.join(os.path.dirname(__file__), path)
        
        try:
            with open(full_path, 'rb') as f:
                start_response('200 OK', [('Content-Type', 'text/css')])
                return [f.read()]
        except IOError:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b"404 Not Found"]

    def serve_html(self, environ, start_response, filename):
        try:
            with open(filename, 'rb') as f:
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [f.read()]
        except IOError:
            start_response('404 Not Found', [('Content-Type', 'text/html')])
            return [b"404 Not Found"]

if __name__ == '__main__':
    app = SimpleWSGIApp()
    server = make_server('localhost', 8000, app)
    print("Serving on http://localhost:8000...")
    server.serve_forever()
