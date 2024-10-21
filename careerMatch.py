
import requests
import json

class CareerMatch:
    def __init__(self):
        self.base_url = 'https://api.careeronestop.org/v1/occupation/'
        self.user_id = 'sVQnlKszaDUTONy'
        self.token = 'q+l+ly1k20xUelwYUiIspbtsvIESZKxFI0vPgbExyNm3nFFbEu8GTn732mF/2mJp7PeAXRduwHGMDYnsi3LC7Q=='

    def find_career(self, keyword):
        jobs_url = f'{self.base_url}{self.user_id}/{keyword}/N/0/30'

        # Headers with token
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
        # API endpoint and parameters
        occupation_url = f'{self.base_url}{self.user_id}/{onetID}/{location}'

        # Headers with token
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

        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()

            # Ensure that we have at least one occupation detail
            if data.get("RecordCount", 0) > 0:
                occupation_detail = data['OccupationDetail'][0]  # Get the first occupation detail

                entries_to_remove = ("NationalWagesList","BLSAreaWagesList","WageYear", "SocData", "SocWageInfo", "SocTitle", "SocDescription")
                for k in entries_to_remove:
                    occupation_detail["Wages"].pop(k, None)

                # Extract relevant details
                occupation_info = {
                    "Title": occupation_detail.get("OnetTitle"),
                    "Description": occupation_detail.get("OnetDescription"),
                    "Salary Info": occupation_detail.get("Wages", {}),
                    "Education": occupation_detail.get("EducationTraining", {}),
                    "Tasks": [dwa.get("DwaTitle") for dwa in occupation_detail.get("Dwas", [])],  # Get only the DWAS titles
                    "Job Growth Prediction": str(occupation_detail.get("BrightOutlook")) + ". This job is/has " + str(occupation_detail.get("BrightOutlookCategory")) + " in employment.",
                    "Video Relating to the Career": occupation_detail.get("COSVideoURL"),
                    "Job Growth Projections": occupation_detail.get("Projections", {}).get("Projections", "N/A"),
                    "Related Careers": occupation_detail.get("RelatedOnetTitles", {}),
                    "Training Programs": occupation_detail.get("TrainingPrograms", []),
                    "Minimum Education Requirement": occupation_detail.get("EducationTraining", {}).get("EducationTitle", "N/A")
                }

                return occupation_info  # Return the dictionary with details

            else:
                print("No occupation details found.")
                return {}

        else:
            print(f"Error fetching occupation details: {response.status_code}")
            return {}

    def list_certifications(self, occupation_title):
        certifications_url = f'https://api.careeronestop.org/v1/certificationfinder/{self.user_id}/{occupation_title}/0/0/0/0/0/0/0/0/0/5'

        # Headers with token
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
        keyword = input("Enter a keyword related to your career of choice: ")
        location = int(input("Enter your zip code: "))

        # Get the OnetCode from the selected career
        onet_codes = self.find_career(keyword)

        if onet_codes:  # Check if we successfully got OnetCodes
            print("Available Occupations:")
            for idx, career in enumerate(onet_codes):
                print(f"{idx + 1}: {career['OnetTitle']} (Code: {career['OnetCode']})")

            choice = int(input("Select an occupation by number: ")) - 1
            if 0 <= choice < len(onet_codes):
                selected_onet_code = onet_codes[choice]['OnetCode']
                self.detailed_occupation_data(selected_onet_code, location)
            else:
                print("Invalid selection.")
        else:
            print("No occupations found.")

# Uncomment to run
# api = CareerMatch()
# api.main()