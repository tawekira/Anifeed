const API_BASE =  "http://127.0.0.1:8000";

const form = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const errorMessage = document.getElementById("error-message");

usernameInput.addEventListener('input', () => errorMessage.classList.add('hidden'));
passwordInput.addEventListener('input', () => errorMessage.classList.add('hidden'));

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const urlEncodedData = new URLSearchParams(formData);

    try {
        const response = await fetch(`${API_BASE}/auth/token`, {
            method: 'POST',
            body: urlEncodedData
        });

        if (!response.ok) {
            const errorDetails = await response.json();
            console.error('Server Validation Error:', errorDetails);
            form.reset();
            errorMessage.classList.remove('hidden');
            return;
        }

        const result = await response.json();
        console.log('Login Success');

        localStorage.setItem('access_token', result.access_token);

        window.location.replace("index.html");

    } catch (error) {
        console.error('Submisson failed:', error);
    }

});

