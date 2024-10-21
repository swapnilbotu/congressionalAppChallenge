import requests
import re

class CareerMatch:
    def __init__(self):
        self.base_url = 'https://api.careeronestop.org/v1/occupation/'
        self.user_id = 'sVQnlKszaDUTONy'
        self.token = 'q+l+ly1k20xUelwYUiIspbtsvIESZKxFI0vPgbExyNm3nFFbEu8GTn732mF/2mJp7PeAXRduwHGMDYnsi3LC7Q=='

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

                entries_to_remove = ("NationalWagesList","BLSAreaWagesList","WageYear", "SocData", "SocWageInfo", "SocTitle", "SocDescription")
                for k in entries_to_remove:
                    occupation_detail["Wages"].pop(k, None)

                annualWage = occupation_detail.get("Wages", {})["StateWagesList"][0]["Median"]
                hourlyWage = occupation_detail.get("Wages", {})["StateWagesList"][1]["Median"]

                occupation_info = {
                    "Title": occupation_detail.get("OnetTitle"),
                    "Description": occupation_detail.get("OnetDescription"),
                    "Salary Info": f"Annual Wage: ${annualWage}, Hourly Wage: ${hourlyWage}",
                    "Education": occupation_detail.get("EducationTraining", {}),
                    "Tasks": [dwa.get("DwaTitle") for dwa in occupation_detail.get("Dwas", [])],
                    "Job Growth Prediction": str(occupation_detail.get("BrightOutlook")) + ". This job is/has " + str(occupation_detail.get("BrightOutlookCategory")) + " in employment.",
                    "Video Relating to the Career": occupation_detail.get("COSVideoURL"),
                    "Job Growth Projections": occupation_detail.get("Projections", {}).get("Projections", "N/A"),
                    "Related Careers": occupation_detail.get("RelatedOnetTitles", {}),
                    "Training Programs": occupation_detail.get("TrainingPrograms", []),
                    "Minimum Education Requirement": occupation_detail.get("EducationTraining", {}).get("EducationTitle", "N/A")
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
        keyword = input("Enter a keyword related to your career of choice: ")
        
        # Ask for zip code with validation
        while True:
            location = input("Enter your zip code: ")
            if self.is_valid_zip(location):
                if self.validate_zip_with_api(location):
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
                occupation_info = self.detailed_occupation_data(selected_onet_code, location)
                if occupation_info:
                    print(f"Your selected occupation: {occupation_info['Title']}")
                    print(f"Title: {occupation_info['Title']}")
                    print(f"Description: {occupation_info['Description']}")
                    print(f"Salary Info: {occupation_info['Salary Info']}")
                    print(f"Education: {occupation_info['Education']}")
                    print(f"Job Growth Prediction: {occupation_info['Job Growth Prediction']}")
                    print(f"Video Relating to the Career: {occupation_info['Video Relating to the Career']}")
                    print(f"Job Growth Projections: {occupation_info['Job Growth Projections']}")
                    print(f"Training Programs: {occupation_info['Training Programs']}")
                    print(f"Minimum Education Requirement: {occupation_info['Minimum Education Requirement']}")
                    
                        # Fetch certifications and display at the end
                    certifications = self.list_certifications(occupation_info["Title"])
                    if certifications:
                        print("\nCertifications available:")
                        for cert in certifications:
                            print(f"Name: {cert['Name']}")
                            print(f"Organization: {cert['Organization']}")
                            print(f"URL: {cert['Url']}")
                            print(f"Description: {cert['Description']}")

                            # Displaying detailed certification info (if available)
                            if "CertDetailList" in cert:
                                print("\nCertification Details:")
                                for detail in cert["CertDetailList"]:
                                    print(f"  {detail['Name']}: {detail['Value']}")

                            print("\n" + "-"*40 + "\n")  # Divider for readability
                else:
                    print("No details found for the selected occupation.")
            else:
                print("Invalid selection.")
        else:
            print("No occupations found.")


# Uncomment to run
# api = CareerMatch()
# api.main()
