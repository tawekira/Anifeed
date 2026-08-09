// js/auth.js
// Handles the login form submission. Depends on api.js being loaded first.

const loginForm = document.getElementById("login-form");
const errorMessage = document.getElementById("error-message");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    errorMessage.classList.add("hidden");

    const submitBtn = loginForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in...";

    try {
      const { access_token } = await api.login(username, password);
      setToken(access_token);
      window.location.href = "index.html";
    } catch (err) {
      errorMessage.textContent = err.message || "Invalid username and/or password";
      errorMessage.classList.remove("hidden");
      submitBtn.disabled = false;
      submitBtn.textContent = "Login";
    }
  });
}