from flask import Flask, request, render_template, jsonify
from careermatch import CareerMatch

app = Flask(__name__)

# Instantiate CareerMatch class
career_match = CareerMatch()

@app.route('/')
def index():
    return render_template('career.html')

@app.route('/search_careers', methods=['POST'])
def search_careers():
    career_keyword = request.form['career']
    zip_code = request.form['zip']

    # Find careers based on the keyword
    jobs = career_match.find_career(career_keyword)

    # Pass jobs to the template for rendering
    return render_template('career.html', jobs=jobs)

@app.route('/career_details', methods=['POST'])
def career_details():
    onet_id = request.form['onet_id']
    location = request.form['location']

    # Get detailed occupation data
    occupation_info = career_match.detailed_occupation_data(onet_id, location)

    if occupation_info:
        return jsonify(occupation_info)
    else:
        return jsonify({"error": "No details found"})

if __name__ == '__main__':
    app.run(debug=True)
