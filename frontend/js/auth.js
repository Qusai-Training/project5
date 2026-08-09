/**
 * AUTH.JS - Pure Vanilla JavaScript handling JWT Login & Registration
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const authAlert = document.getElementById("authAlert");
  const skillsContainer = document.getElementById("skillsContainer");

  function showAlert(msg, isError = true) {
    if (!authAlert) return;
    authAlert.textContent = msg;
    authAlert.className = `auth-alert ${isError ? "error" : "success"}`;
    authAlert.classList.remove("hidden");
  }

  // Handle User Login
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      try {
        const response = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.token) {
          localStorage.setItem("jwt_token", data.token);
          window.location.href = "courses.html";
        } else {
          showAlert(data.message || "Invalid username or password.");
        }
      } catch (err) {
        showAlert("Server connection failed. Please try again later.");
      }
    });
  }

  // Load available skills list for Registration form checkbox choices
  async function loadSkillsForRegistration() {
    if (!skillsContainer) return;

    try {
      const response = await fetch(`${API_BASE}/skills`);
      if (response.ok) {
        const skills = await response.json();
        skillsContainer.innerHTML = "";
        
        skills.forEach(skill => {
          const label = document.createElement("label");
          label.className = "skill-checkbox-label";
          label.innerHTML = `
            <input type="checkbox" name="skills" value="${skill.id}">
            <span>${skill.name}</span>
          `;
          skillsContainer.appendChild(label);
        });
      } else {
        skillsContainer.innerHTML = `<span style="font-size:0.8rem; color:gray;">Default skills selection active</span>`;
      }
    } catch (err) {
      skillsContainer.innerHTML = `<span style="font-size:0.8rem; color:gray;">Failed to load skills list</span>`;
    }
  }

  // Handle User Registration
  if (registerForm) {
    loadSkillsForRegistration();

    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const selectedSkillIds = Array.from(
        document.querySelectorAll('input[name="skills"]:checked')
      ).map(cb => parseInt(cb.value));

      const payload = {
        username: document.getElementById("regUsername").value.trim(),
        email: document.getElementById("regEmail").value.trim(),
        password: document.getElementById("regPassword").value,
        phone: document.getElementById("regPhone").value.trim(),
        age: parseInt(document.getElementById("regAge").value) || null,
        major: document.getElementById("regMajor").value.trim(),
        skills: selectedSkillIds
      };

      try {
        const response = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
          alert("Registration successful! Please log in.");
          window.location.href = "login.html";
        } else {
          showAlert(data.message || "Registration failed.");
        }
      } catch (err) {
        showAlert("Registration failed due to network error.");
      }
    });
  }
});