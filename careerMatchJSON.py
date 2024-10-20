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
            occupations = data["OccupationList"]

            itemNum = 1
            for item in occupations:
                print(f'[{itemNum}] {item["OnetTitle"]} : {item["OccupationDescription"]}')
                itemNum += 1
        else:
            print(f"Error fetching occupation details: {response.status_code}")
            return None

        occupation_choice = int(input("\nEnter the number representing your desired career: "))
        print("\n\n\n\nYour selected occupation:", occupations[occupation_choice - 1]["OnetTitle"])
        return occupations[occupation_choice - 1]["OnetCode"]

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

                # Remove unnecessary fields
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
                    "Job Growth Projections": occupation_detail["Projections"]["Projections"],
                    "Related Careers": occupation_detail.get("RelatedOnetTitles", {}),
                    "Training Programs": occupation_detail.get("TrainingPrograms", []),
                    "Minimum Education Requirement": occupation_detail["EducationTraining"]["EducationTitle"]
                }

                # Fetch certifications
                certifications = self.list_certifications(occupation_info["Title"])
                if certifications:
                    occupation_info["Certifications"] = certifications

                # Output the data in JSON format
                print(json.dumps(occupation_info, indent=4))

            else:
                print("No occupation details found.")

        else:
            print(f"Error fetching occupation details: {response.status_code}")

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
        keyword = input("Enter the name of your career of choice: ")
        location = int(input("Enter your zip code: "))

        # Get the OnetCode from the selected career
        onet_code = self.find_career(keyword)

        if onet_code:  # Check if we successfully got an OnetCode
            self.detailed_occupation_data(onet_code, location)

api = CareerMatch()
api.main()
