import requests
import re
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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

                # Construct the volunteer link
                volunteer_link = f"https://www.volunteermatch.org/search/?l={location}&k={occupation_detail.get('OnetTitle')}&v=true"
                # Format it as an HTML link
                volunteer_link_html = f'<a href="{volunteer_link}" target="_blank">Find Volunteer Opportunities</a>'

                # Format career video link as an HTML link if available
                career_video_url = occupation_detail.get("COSVideoURL")
                if career_video_url:
                    career_video_html = f'<a href="{career_video_url}" target="_blank">Watch Career Video</a>'
                else:
                    career_video_html = "No career video available"

                occupation_info = {
                    "Title": occupation_detail.get("OnetTitle"),
                    "Description": occupation_detail.get("OnetDescription"),
                    "Salary Info": f"Annual Wage: ${annualWage}, Hourly Wage: ${hourlyWage}",
                    "Minimum Education Requirement": occupation_detail.get("EducationTraining", {}).get("EducationTitle", "N/A"),
                    "Tasks": [dwa["DwaTitle"] for dwa in occupation_detail.get("Dwas", [])],
                    "Job Growth Prediction": str(occupation_detail.get("BrightOutlook")) + ". This job is/has " + str(occupation_detail.get("BrightOutlookCategory")) + " in employment.",
                    "Video Relating to the Career": career_video_html,  # Career video as clickable link
                    "Job Growth Projections": statement,
                    "Related Careers": occupation_detail.get("RelatedOnetTitles", {}),
                    "Training Programs": occupation_detail.get("TrainingPrograms", []),
                    "Volunteer Link": volunteer_link_html  # Volunteer link as clickable link
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
                    print("Valid zip code but does not correspond to a real location. Try again.")
            else:
                print("Invalid zip code. Try again.")

        occupation_details = self.find_career(keyword)

        if occupation_details:
            print(f"List of occupations matching {keyword}:")
            for idx, occupation in enumerate(occupation_details):
                print(f"{idx + 1}. {occupation['OnetTitle']} - {occupation['OccupationDescription'][:200]}...")

            # Ask user for occupation details selection
            try:
                occupation_choice = int(input("Enter the number of the occupation you're interested in: ")) - 1
                if occupation_choice < 0 or occupation_choice >= len(occupation_details):
                    print("Invalid choice. Exiting.")
                    return
            except ValueError:
                print("Invalid input. Exiting.")
                return

            occupation_id = occupation_details[occupation_choice]['OnetCode']
            detailed_occupation = self.detailed_occupation_data(occupation_id, self.location)

            print(f"\nDetailed information for {detailed_occupation['Title']}:\n")
            print(f"Description: {detailed_occupation['Description']}")
            print(f"Salary: {detailed_occupation['Salary Info']}")
            print(f"Minimum Education Requirement: {detailed_occupation['Minimum Education Requirement']}")
            print(f"Tasks: {', '.join(detailed_occupation['Tasks'])}")
            print(f"Job Growth Projections: {detailed_occupation['Job Growth Projections']}")
            print(f"Related Careers: {', '.join(detailed_occupation['Related Careers'].keys())}")
            print(f"Volunteer Link: {detailed_occupation['Volunteer Link']}")
            print(f"Career Video: {detailed_occupation['Video Relating to the Career']}")

        else:
            print(f"No occupation details found for {keyword}.")


if __name__ == "__main__":
    cm = CareerMatch()
    cm.main()
