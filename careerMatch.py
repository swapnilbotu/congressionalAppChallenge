import requests
import re
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs
from flask import Flask, request, jsonify, render_template

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
#wwwwwww
class CareerMatch:
    def __init__(self):
        self.base_url = 'https://api.careeronestop.org/v1/occupation/'
        self.user_id = os.getenv('CAREER_USER_ID')
        self.token = os.getenv('CAREER_API_TOKEN')

    def is_valid_zip(self, zipcode):
        """Check if the given zip code is valid."""
        return bool(re.match(r'^\d{5}(-\d{4})?$', zipcode))

    def validate_zip_with_api(self, zipcode):
        """Check if the zip code corresponds to a real location using an external API."""
        url = f"http://api.zippopotam.us/us/{zipcode}"
        response = requests.get(url)
        return response.status_code == 200

    def find_career(self, keyword):
        jobs_url = f'{self.base_url}{self.user_id}/{keyword}/N/0/30'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

        response = requests.get(jobs_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            occupations = data.get("OccupationList", [])
            return [{"OnetTitle": item["OnetTitle"], "OnetCode": item["OnetCode"], "OccupationDescription": item["OccupationDescription"]} for item in occupations]
        else:
            print(f"Error fetching occupation details: {response.status_code}")
            return None

    def detailed_occupation_data(self, onetID, location):
        occupation_url = f'{self.base_url}{self.user_id}/{onetID}/{location}'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

        params = {
            "training": True,
            "interest": False,
            "videos": False,
            "tasks": False,
            "dwas": True,
            "wages": True,
            "alternateOnetTitles": False,
            "projectedEmployment": True,
            "ooh": False,
            "stateLMILinks": False,
            "relatedOnetTitles": True,
            "skills": False,
            "knowledge": False,
            "ability": False,
            "trainingPrograms": True,
            "industryEmpPattern": False,
            "toolsAndTechnology": False,
            "workValues": False,
            "enableMetaData": False
        }

        response = requests.get(occupation_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("RecordCount", 0) > 0:
                occupation_detail = data['OccupationDetail'][0]

                entries_to_remove = ("NationalWagesList", "BLSAreaWagesList", "WageYear", "SocData", "SocWageInfo", "SocTitle", "SocDescription")
                for k in entries_to_remove:
                    occupation_detail["Wages"].pop(k, None)

                if len(occupation_detail.get("Wages", {}).get("StateWagesList", [])) > 1:
                    annualWage = occupation_detail.get("Wages", {}).get("StateWagesList")[0].get("Median", "Data Not Available")
                    hourlyWage = occupation_detail.get("Wages", {}).get("StateWagesList")[1].get("Median", "Data Not Available")
                elif len(occupation_detail.get("Wages", {}).get("StateWagesList", [])) == 1:
                    annualWage = occupation_detail.get("Wages", {}).get("StateWagesList")[0].get("Median", "Data Not Available")
                    hourlyWage = "(Hourly Salary Data Not Available for this Occupation)"
                else:
                    annualWage, hourlyWage = "(Annual Salary Data Not Available for this Occupation)", "(Hourly Salary Data Not Available for this Occupation)"

                if len(occupation_detail.get("Projections", "Projection Data Not Available for this Occupation")["Projections"]) > 1:
                    stateGrowthProjection = int(occupation_detail.get("Projections").get("Projections")[0]["PerCentChange"])
                    stateName = occupation_detail.get("Projections").get("Projections")[0].get("StateName", "")
                    nationGrowthProjection = int(occupation_detail.get("Projections").get("Projections")[1]["PerCentChange"])
                    nationName = occupation_detail.get("Projections").get("Projections")[1].get("StateName", "")

                    # Determine if the growth is positive or negative
                    if stateGrowthProjection > 0:
                        stateGrowth = "increase"
                    elif stateGrowthProjection == 0:
                        stateGrowth = "not change"
                    else:
                        stateGrowth = "decrease"

                    if nationGrowthProjection > 0:
                        nationGrowth = "increase"
                    elif nationGrowthProjection == 0:
                        nationGrowth = "not change"
                    else:
                        nationGrowth = "decrease"

                    statement = f"\nWe predict the employment for this job to {stateGrowth} by %{stateGrowthProjection} in {stateName}.\nWe predict the employment for this job to {nationGrowth} by %{nationGrowthProjection} in {nationName}."
                
                elif len(occupation_detail.get("Projections", "Projection Data Not Available for this Occupation")["Projections"]) == 1:
                    stateGrowthProjection = int(occupation_detail.get("Projections").get("Projections")[0]["PerCentChange"])
                    stateName = occupation_detail.get("Projections").get("Projections")[0].get("StateName", "")

                    if stateGrowthProjection > 0:
                        stateGrowth = "increase"
                    elif stateGrowthProjection == 0:
                        stateGrowth = "not change"
                    else:
                        stateGrowth = "decrease"


                    statement = f"\nWe predict the employment for this job to {stateGrowth} by %{stateGrowthProjection} in {stateName}."
                
                else:
                    statement = "Projection Data Not Available for this Occupation"


                occupation_info = {
                    "Title": occupation_detail.get("OnetTitle"),
                    "Description": occupation_detail.get("OnetDescription"),
                    "Salary Info": f"Annual Wage: ${annualWage}, Hourly Wage: ${hourlyWage}",
                    "Minimum Education Requirement": occupation_detail.get("EducationTraining", {}).get("EducationTitle", "N/A"),
                    "Tasks": [dwa["DwaTitle"] for dwa in occupation_detail.get("Dwas", [])],
                    "Job Growth Prediction": str(occupation_detail.get("BrightOutlook")) + ". This job is/has " + str(occupation_detail.get("BrightOutlookCategory")) + " in employment.",
                    "Video Relating to the Career": occupation_detail.get("COSVideoURL"),
                    "Job Growth Projections": statement,
                    "Related Careers": occupation_detail.get("RelatedOnetTitles", {}),
                    "Training Programs": occupation_detail.get("TrainingPrograms", []),
                }

                return occupation_info

            else:
                print("No occupation details found.")
                return {}

        else:
            print(f"Error fetching occupation details: {response.status_code}")
            return {}

    def list_certifications(self, occupation_title):
        certifications_url = f'https://api.careeronestop.org/v1/certificationfinder/{self.user_id}/{occupation_title}/0/0/0/0/0/0/0/0/0/5'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

        response = requests.get(certifications_url, headers=headers)

        if response.status_code == 200:
            certifications = response.json()
            return certifications.get("CertList", [])
        else:
            print(f"Error fetching certification details: {response.status_code}")
            return []

    def main(self):
        keyword = input("Enter the name of your career of choice: ")
        
        # Ask for zip code with validation
        while True:
            self.location = input("Enter your zip code: ")
            if self.is_valid_zip(self.location):
                if self.validate_zip_with_api(self.location):
                    print("Valid zip code and corresponds to a real location.")
                    break
                else:
                    print("Valid zip code but does not correspond to a real location. Please try again.")
            else:
                print("Invalid zip code. Please enter a valid 5 or 9-digit zip code.")

        onet_codes = self.find_career(keyword)

        if onet_codes:
            print("Available Occupations:")
            for idx, career in enumerate(onet_codes):
                print(f"{idx + 1}: {career['OnetTitle']} (Code: {career['OnetCode']})")

            choice = int(input("Select an occupation by number: ")) - 1
            if 0 <= choice < len(onet_codes):
                selected_onet_code = onet_codes[choice]['OnetCode']

                self.occupation_info = self.detailed_occupation_data(selected_onet_code, self.location)

                if self.occupation_info:
                    print(f"\n\n\nTitle: {self.occupation_info['Title']}")
                    print(f"Description: {self.occupation_info['Description']}")
                    print(f"Salary Info: {self.occupation_info['Salary Info']}")
                    print(f"Minimum Education Requirement: {self.occupation_info['Minimum Education Requirement']}")
                    print(f"Tasks: {self.occupation_info['Tasks']}")
                    print(f"Job Growth Prediction: {self.occupation_info['Job Growth Prediction']}")
                    print(f"Video Relating to the Career: {self.occupation_info['Video Relating to the Career']}")
                    print(f"Job Growth Projections: {self.occupation_info['Job Growth Projections']}")
                    print(f"Training Programs: {self.occupation_info['Training Programs'][:10]}")
                    
                    # Fetch certifications and display at the end
                    certifications = self.list_certifications(self.occupation_info["Title"])
                    if certifications:
                        print("\nCertifications available:")
                        for cert in certifications:
                            print(f"Name: {cert['Name']}")
                            print(f"Organization: {cert['Organization']}")
                            print(f"URL: {cert['Url']}")
                            print(f"Description: {cert['Description']}")

                            # Displaying detailed certification info
                            for cert_detail in cert.get('CertDetails', []):
                                print(f"    Title: {cert_detail['Title']}")
                                print(f"    Certifying Body: {cert_detail['CertifyingBody']}")
                            print()
                    else:
                        print("No certifications found for this occupation.")
                else:
                    print("Occupation details unavailable.")
            else:
                print("Invalid choice. Please select a number from the list.")
        else:
            print("No occupations found for the given keyword.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/careerfinder', methods=['GET', 'POST'])
def career_finder():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        zipcode = request.form.get('zipcode')
        
        career_match = CareerMatch()
        
        if career_match.is_valid_zip(zipcode) and career_match.validate_zip_with_api(zipcode):
            careers = career_match.find_career(keyword)
            return render_template('results.html', careers=careers, keyword=keyword, zipcode=zipcode)
        else:
            return render_template('career_finder.html', error="Invalid zip code.")

    return render_template('career_finder.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    try:
        data = request.get_json()
        user_message = data.get('message')

        # Call your AI API here
        response_message = get_response_from_ai(user_message)

        return jsonify({'response': response_message})
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({'response': "Error: Unable to process your request."}), 500


def get_chatbot_response(message):
    # Placeholder for Google Generative AI integration
    return f"Chatbot response to: {message}"

if __name__ == '__main__':
    app.run(debug=True)
