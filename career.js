document.getElementById('careerForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission

    let keyword = document.getElementById('keyword').value;
    let location = document.getElementById('location').value;

    // Send a POST request to Flask
    fetch('/findcareer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `keyword=${encodeURIComponent(keyword)}&location=${encodeURIComponent(location)}`
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        let occupationsList = document.getElementById('occupations');
        occupationsList.innerHTML = ''; // Clear the list before appending new results

        // If occupations are returned, display them
        if (data.occupations) {
            data.occupations.forEach((occupation, index) => {
                let listItem = document.createElement('li');
                listItem.innerText = `${occupation.OnetTitle}: ${occupation.OccupationDescription}`;
                occupationsList.appendChild(listItem);
            });
        } else {
            alert("No occupations found");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error fetching data: ' + error.message);
    });
});
