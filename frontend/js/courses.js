/**
 * COURSES.JS - Pure Vanilla JS logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";
  let currentPage = 1;

  // DOM Elements
  const coursesGrid = document.getElementById("coursesGrid");
  const searchInput = document.getElementById("searchInput");
  const skillFilter = document.getElementById("skillFilter");
  const sortFilter = document.getElementById("sortFilter");
  const prevPageBtn = document.getElementById("prevPageBtn");
  const nextPageBtn = document.getElementById("nextPageBtn");
  const pageInfo = document.getElementById("pageInfo");
  const mobileMenuToggle = document.getElementById("mobileMenuToggle");
  const navRight = document.getElementById("navRight");

  // Mobile menu toggle logic
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener("click", () => {
      navRight.classList.toggle("active");
    });
  }

  function getAuthToken() {
    return localStorage.getItem("jwt_token");
  }

  // Fetch logged in user profile (GET /api/users/me)
  async function fetchUserProfile() {
    const token = getAuthToken();
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/users/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (response.ok) {
        const user = await response.json();
        const username = user.username || "User";
        
        document.getElementById("userGreetingName").textContent = username;
        document.getElementById("navUsername").textContent = username;
        document.getElementById("heroAvatar").textContent = username.charAt(0).toUpperCase();
        document.getElementById("navAvatar").textContent = username.charAt(0).toUpperCase();
      }
    } catch (err) {
      console.error("Profile fetch error:", err);
    }
  }

  // Load skills into dropdown filter (GET /api/skills)
  async function loadSkillsFilter() {
    try {
      const response = await fetch(`${API_BASE}/skills`);
      if (response.ok) {
        const skills = await response.json();
        skills.forEach(skill => {
          const opt = document.createElement("option");
          opt.value = skill.id;
          opt.textContent = skill.name;
          skillFilter.appendChild(opt);
        });
      }
    } catch (err) {
      console.error("Skill list fetch error:", err);
    }
  }

  // Fetch course catalog (GET /api/courses)
  async function fetchCourses(page = 1) {
    const token = getAuthToken();
    const searchVal = searchInput.value.trim();
    const skillVal = skillFilter.value;

    coursesGrid.innerHTML = `<div class="loading-spinner">Loading courses...</div>`;

    let url = `${API_BASE}/courses?page=${page}&limit=6`;
    if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;
    if (skillVal) url += `&skill_id=${encodeURIComponent(skillVal)}`;

    try {
      const response = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) throw new Error("Failed to load courses");

      const data = await response.json();
      const coursesList = data.courses || data;
      renderCourses(coursesList);

      currentPage = page;
      pageInfo.textContent = `Page ${currentPage}`;
      prevPageBtn.disabled = currentPage === 1;
      nextPageBtn.disabled = !data.has_more && (coursesList.length < 6);

    } catch (err) {
      coursesGrid.innerHTML = `<p class="error-msg">Could not load courses from server.</p>`;
    }
  }

  // Render course cards dynamically
  function renderCourses(courses) {
    coursesGrid.innerHTML = "";

    if (!courses || courses.length === 0) {
      coursesGrid.innerHTML = `<p class="no-results">No courses found matching your criteria.</p>`;
      return;
    }

    courses.forEach(course => {
      const card = document.createElement("div");
      card.className = "course-card";

      const skillsArray = Array.isArray(course.skill_requirements)
        ? course.skill_requirements
        : (course.skill_requirements ? course.skill_requirements.split(",") : ["General"]);

      const skillBadges = skillsArray
        .map(s => `<span class="skill-tag">${s.trim()}</span>`)
        .join("");

      card.innerHTML = `
        <div>
          <h3 class="course-title">${course.title}</h3>
          <div class="instructor-tag"><i class="fa-solid fa-user-tie"></i> ${course.instructor || "Instructor"}</div>
          <p class="course-description">${course.description || ""}</p>
          <div class="skill-badges">${skillBadges}</div>
        </div>
        <div class="course-card-footer">
          <a href="/course-details.html?id=${course.id}" class="view-details-btn">View Details</a>
        </div>
      `;

      coursesGrid.appendChild(card);
    });
  }

  // Event Listeners
  let debounceTimer;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchCourses(1), 300);
  });

  skillFilter.addEventListener("change", () => fetchCourses(1));
  sortFilter.addEventListener("change", () => fetchCourses(1));

  prevPageBtn.addEventListener("click", () => {
    if (currentPage > 1) fetchCourses(currentPage - 1);
  });

  nextPageBtn.addEventListener("click", () => {
    fetchCourses(currentPage + 1);
  });

  // Initialize
  fetchUserProfile();
  loadSkillsFilter();
  fetchCourses(1);
});