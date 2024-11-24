document.addEventListener('DOMContentLoaded', function () {
    // Check if the user is logged in by checking if there's a userId in the URL
    const userId = window.location.pathname.split('/').pop();
    if (userId) {
        fetchSummaries(userId); // Fetch summaries for the logged-in user
    }

    // Registration Form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = {
                name: formData.get('regName'),
                email: formData.get('regEmail'),
                portfolio: formData.get('regPortfolio').split(',').map(stock => stock.trim())
            };

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                // Handle Flask redirect
                if (response.redirected) {
                    window.location.href = response.url; // Redirect to homepage if successful
                } else {
                    const result = await response.json();
                    alert(result.message || "Registration failed.");
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault(); // Prevent default form submission

            const data = {
                logEmail: document.getElementById("logEmail").value
            };

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.redirected) {
                    window.location.href = response.url; // Redirect to homepage if successful
                } else {
                    const error = await response.json();
                    alert(error.message || "Login failed.");
                }
            } catch (err) {
                console.error("Error during login:", err);
                alert("An error occurred. Please try again later.");
            }
        });
    }
});

// Function to fetch and display personalized summaries for the user
async function fetchSummaries(userId) {
    console.log(`Fetching summaries for user ID: ${userId}`);
    try {
        const response = await fetch(`/summaries/${userId}`);
        const summaries = await response.json();
        const summariesDiv = document.getElementById('summaries');

        if (summariesDiv) {
            summariesDiv.innerHTML = summaries.map(article => `
                <div class="article">
                    <h2>${article[1]}</h2>
                    <p class="summary" id="summary-${article[0]}" data-fulltext="${encodeURIComponent(article[2])}">${truncateText(article[2], 100)}</p>
                    <a href="javascript:void(0);" onclick="toggleSummary(${article[0]})">Read more</a>
                    <a href="${article[3]}" target="_blank">Full Article</a>
                    <button onclick="sendFeedback(${article[0]}, 'relevant')">Relevant</button>
                    <button onclick="sendFeedback(${article[0]}, 'not_relevant')">Not Relevant</button>
                </div>
            `).join('');
        } else {
            console.error("Element with ID 'summaries' not found in the DOM.");
        }
    } catch (error) {
        console.error("Error fetching summaries:", error);
    }
}

// Function to truncate text
function truncateText(text, maxLength) {
    if (text.length > maxLength) {
        return text.slice(0, maxLength) + '... <a href="javascript:void(0);" onclick="toggleSummary()">Read more</a>';
    }
    return text;
}

// Function to toggle the visibility of the summary text
function toggleSummary(id) {
    const summary = document.getElementById(`summary-${id}`);
    const fullText = decodeURIComponent(summary.getAttribute('data-fulltext'));
    if (summary.classList.contains('expanded')) {
        summary.innerHTML = truncateText(fullText, 100);
        summary.classList.remove('expanded');
    } else {
        summary.innerHTML = fullText + ' <a href="javascript:void(0);" onclick="toggleSummary(' + id + ')">Show less</a>';
        summary.classList.add('expanded');
    }
}

// Function to send feedback for articles (Relevant/Not Relevant)
async function sendFeedback(articleId, feedback) {
    try {
        const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ articleId, feedback })
        });

        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error("Error sending feedback:", error);
    }
}
