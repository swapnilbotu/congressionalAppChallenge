document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('careerForm');
    const keywordInput = document.getElementById('keyword');
    const zipCodeInput = document.getElementById('zipCode');
    const resultsDiv = document.getElementById('results');
    const occupationDetailsDiv = document.getElementById('occupationDetails');

    // On form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const keyword = keywordInput.value;
        const zipCode = zipCodeInput.value;

        // Clear previous results
        resultsDiv.innerHTML = '';
        occupationDetailsDiv.innerHTML = '';

        try {
            // Fetch the list of occupations
            const occupations = await findCareer(keyword);
            if (occupations.length > 0) {
                // Display the list of careers
                displayCareerList(occupations);

                // Add an event listener for career selection
                document.getElementById('selectNumber').addEventListener('change', async function () {
                    const selectedNumber = parseInt(this.value);
                    if (selectedNumber > 0 && selectedNumber <= occupations.length) {
                        const selectedOccupation = occupations[selectedNumber - 1];
                        const details = await getOccupationDetails(selectedOccupation.OnetCode, zipCode);
                        displayOccupationDetails(details);
                    } else {
                        alert('Invalid selection. Please enter a valid number.');
                    }
                });
            } else {
                resultsDiv.innerHTML = 'No occupations found for the provided keyword.';
            }
        } catch (error) {
            console.error(error);
            resultsDiv.innerHTML = 'Error fetching career data.';
        }
    });

    // Fetch list of careers using API
    async function findCareer(keyword) {
        const userId = 'sVQnlKszaDUTONy';
        const token = 'q+l+ly1k20xUelwYUiIspbtsvIESZKxFI0vPgbExyNm3nFFbEu8GTn732mF/2mJp7PeAXRduwHGMDYnsi3LC7Q==';
        const url = `https://api.careeronestop.org/v1/occupation/${userId}/${keyword}/N/0/30`;

        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        return data.OccupationList;
    }

    // Fetch detailed occupation data using API
    async function getOccupationDetails(onetCode, zipCode) {
        const userId = 'sVQnlKszaDUTONy';
        const token = 'q+l+ly1k20xUelwYUiIspbtsvIESZKxFI0vPgbExyNm3nFFbEu8GTn732mF/2mJp7PeAXRduwHGMDYnsi3LC7Q==';
        const url = `https://api.careeronestop.org/v1/occupation/${userId}/${onetCode}/${zipCode}`;

        const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
    
        // Log the entire response for debugging
        console.log("API Response:", data);
    
        return data.OccupationDetail[0];  // Return the first occupation detail
    }


    // Display the list of careers
    function displayCareerList(occupations) {
        let occupationHTML = '<h3>Select a career by number:</h3><ul>';
        occupations.forEach((occupation, index) => {
            occupationHTML += `<li>${index + 1}. ${occupation.OnetTitle}</li>`;
        });
        occupationHTML += '</ul>';
        occupationHTML += '<input type="number" id="selectNumber" placeholder="Enter a number to select a career">';
        resultsDiv.innerHTML = occupationHTML;
    }

    
    function displayOccupationDetails(occupation) {
        let detailsHTML = `
            <h3>Occupation: ${occupation.OnetTitle || 'Title not available'}</h3>
            <p><strong>Description:</strong> ${occupation.OnetDescription || 'Description not available'}</p>
            <p><strong>Salary Info:</strong> ${occupation.Wages?.MeanAnnual ? `${occupation.Wages.MeanAnnual}` : 'Salary info not available'}</p>
            <p><strong>Education:</strong> ${occupation.EducationTraining?.EducationTitle || 'Education info not available'}</p>
            <p><strong>Job Growth:</strong> ${occupation.BrightOutlookCategory || 'Job growth info not available'}</p>
        `;
    
        // Display tasks (Dwas) in a list format
        if (occupation.Dwas && Array.isArray(occupation.Dwas)) {
            detailsHTML += `<h4>Tasks:</h4><ul>`;
            occupation.Dwas.forEach(dwa => {
                detailsHTML += `<li>${dwa.DwaTitle || 'Task title not available'}</li>`;
            });
            detailsHTML += `</ul>`;
        } else {
            detailsHTML += `<p><strong>Tasks:</strong> Tasks not available</p>`;
        }
    
        // Career video
        detailsHTML += `<p><strong>Career Video:</strong> ${occupation.COSVideoURL ? `<a href="${occupation.COSVideoURL}" target="_blank">Watch Video</a>` : 'No video available'}</p>`;
    
        // Related careers
        detailsHTML += `<h4>Related Careers:</h4><ul>`;
        if (occupation.RelatedOnetTitles && occupation.RelatedOnetTitles.length > 0) {
            occupation.RelatedOnetTitles.forEach(related => {
                detailsHTML += `<li>${related.OnetTitle}</li>`;
            });
        } else {
            detailsHTML += `<li>Related careers not available.</li>`;
        }
        detailsHTML += `</ul>`;
    
        // Training programs
        if (occupation.TrainingPrograms && occupation.TrainingPrograms.length > 0) {
            detailsHTML += `<h4>Training Programs:</h4><ul>`;
            occupation.TrainingPrograms.forEach(program => {
                detailsHTML += `<li><a href="${program.ProviderURL}" target="_blank">${program.ProgramName}</a> at ${program.ProviderName}</li>`;
            });
            detailsHTML += `</ul>`;
        } else {
            detailsHTML += `<p>No training programs available.</p>`;
        }
    
        // Certifications
        detailsHTML += `<h4>Certifications:</h4><ul>`;
        if (occupation.certifications && occupation.certifications.length > 0) {
            occupation.certifications.forEach(cert => {
                detailsHTML += `<li>
                    <strong>${cert.Name}</strong><br>
                    <strong>Organization:</strong> ${cert.Organization}<br>
                    <strong>URL:</strong> <a href="${cert.Url}" target="_blank">${cert.Url}</a><br>
                    <strong>Description:</strong> ${cert.Description || 'No description available'}
                </li>`;
            });
        } else {
            detailsHTML += `<li>No certifications available.</li>`;
        }
        detailsHTML += `</ul>`;
    
        // Display the content
        occupationDetailsDiv.innerHTML = detailsHTML;
    }
    
    
    
});
