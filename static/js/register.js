// js/register.js
const registerForm = document.getElementById("register-form");
const errorMessage = document.getElementById("error-message");
const successMessage = document.getElementById("success-message");

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    errorMessage.classList.add("hidden");
    successMessage.classList.add("hidden");

    const submitBtn = registerForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Creating account...";

    try {
      await api.post("/users/", { username, password });

      successMessage.textContent = "Account created! Redirecting to login...";
      successMessage.classList.remove("hidden");
      setTimeout(() => (window.location.href = "login.html"), 1000);
    } catch (err) {
      errorMessage.textContent = err.message || "Could not create account";
      errorMessage.classList.remove("hidden");
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign up";
    }
  });
}