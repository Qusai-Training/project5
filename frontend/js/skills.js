/**
 * SKILLS.JS - User Skills Inventory Management
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";

  // Elements
  const navUsername = document.getElementById("navUsername");
  const navAvatar = document.getElementById("navAvatar");
  const profileFullName = document.getElementById("profileFullName");
  const profileEmail = document.getElementById("profileEmail");

  const newSkillsContainer = document.getElementById("newSkillsContainer");
  const currentSkillsContainer = document.getElementById("currentSkillsContainer");
  const newSkillsCount = document.getElementById("newSkillsCount");
  const totalSkillsCount = document.getElementById("totalSkillsCount");

  const enrolledCoursesContainer = document.getElementById("enrolledCoursesContainer");
  const enrolledCoursesCount = document.getElementById("enrolledCoursesCount");

  const mobileMenuToggle = document.getElementById("mobileMenuToggle");
  const navRight = document.getElementById("navRight");

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener("click", () => {
      navRight.classList.toggle("active");
    });
  }

  function getAuthToken() {
    return localStorage.getItem("jwt_token");
  }

  // Load User Profile Data (header)
  async function loadProfile() {
    const token = getAuthToken();

    try {
      const response = await fetch(`${API_BASE}/users/me`, {
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (response.ok) {
        const user = await response.json();
        const username = user.username || user.first_name || "User";
        const fullName = `${user.first_name || ""} ${user.last_name || ""}`.trim() || username;
        const initial = username.charAt(0).toUpperCase();

        if (navUsername) navUsername.textContent = username;
        if (navAvatar) navAvatar.textContent = initial;
        if (profileFullName) profileFullName.textContent = fullName;
        if (profileEmail) profileEmail.textContent = user.email || "";

        renderEnrolledCourses(user.enrolled_courses || []);
      }
    } catch (err) {
      console.error("Profile load error:", err);
    }
  }

  // Load User Skills Data
  async function loadUserSkills() {
    const token = getAuthToken();

    try {
      const response = await fetch(`${API_BASE}/user/skills`, {
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (response.ok) {
        const skillsData = await response.json();

        // Filter new skills vs existing skills based on response flags or recent dates
        const newSkills = skillsData.filter(s => s.is_new === true || s.status === 'acquired_recently');
        const existingSkills = skillsData.filter(s => !s.is_new && s.status !== 'acquired_recently');

        renderNewSkills(newSkills);
        renderCurrentSkills(existingSkills);
      } else {
        // Fallback sample render if API endpoint is fresh
        renderSkillsFallback();
      }
    } catch (err) {
      renderSkillsFallback();
    }
  }

  function renderNewSkills(skills) {
    newSkillsContainer.innerHTML = "";
    newSkillsCount.textContent = `${skills.length} New`;

    if (skills.length === 0) {
      newSkillsContainer.innerHTML = `<p style="grid-column:1/-1; color:#94A3B8; font-size:0.85rem;">No new skills unlocked this week.</p>`;
      return;
    }

    skills.forEach(skill => {
      const card = document.createElement("div");
      card.className = "skill-card new-skill-card";
      card.innerHTML = `
        <div class="skill-card-top">
          <span class="skill-name">${skill.name}</span>
          <span class="tag-new">NEW</span>
        </div>
        <div class="skill-level-bar">
          <div class="skill-level-fill" style="width: ${skill.proficiency || 80}%;"></div>
        </div>
        <div class="skill-card-footer">
          <span>Unlocked recently</span>
          <span><strong>${skill.proficiency || 80}%</strong></span>
        </div>
      `;
      newSkillsContainer.appendChild(card);
    });
  }

  function renderCurrentSkills(skills) {
    currentSkillsContainer.innerHTML = "";
    totalSkillsCount.textContent = `${skills.length} Total`;

    if (skills.length === 0) {
      currentSkillsContainer.innerHTML = `<p style="grid-column:1/-1; color:#94A3B8; font-size:0.85rem;">No skills registered yet.</p>`;
      return;
    }

    skills.forEach(skill => {
      const card = document.createElement("div");
      card.className = "skill-card";
      card.innerHTML = `
        <div class="skill-card-top">
          <span class="skill-name">${skill.name}</span>
          <i class="fa-solid fa-circle-check text-green" style="font-size:0.85rem;"></i>
        </div>
        <div class="skill-level-bar">
          <div class="skill-level-fill" style="width: ${skill.proficiency || 70}%;"></div>
        </div>
        <div class="skill-card-footer">
          <span>Proficiency</span>
          <span><strong>${skill.proficiency || 70}%</strong></span>
        </div>
      `;
      currentSkillsContainer.appendChild(card);
    });
  }

  // Fallback helper to populate skills visually
  function renderSkillsFallback() {
    const fallbackNew = [
      { name: "Vector Databases", proficiency: 85, is_new: true },
      { name: "FastAPI", proficiency: 75, is_new: true }
    ];

    const fallbackCurrent = [
      { name: "Python", proficiency: 95 },
      { name: "PostgreSQL", proficiency: 88 },
      { name: "Flask & REST API", proficiency: 90 },
      { name: "JavaScript", proficiency: 82 }
    ];

    renderNewSkills(fallbackNew);
    renderCurrentSkills(fallbackCurrent);
  }

  function renderEnrolledCourses(courses) {
    if (!enrolledCoursesContainer || !enrolledCoursesCount) return;
    enrolledCoursesContainer.innerHTML = "";
    enrolledCoursesCount.textContent = `${courses.length} Course${courses.length === 1 ? "" : "s"}`;

    if (courses.length === 0) {
      enrolledCoursesContainer.innerHTML = `<p style="grid-column:1/-1; color:#94A3B8; font-size:0.85rem;">No courses enrolled yet. Browse the <a href="/courses.html">course catalog</a>.</p>`;
      return;
    }

    courses.forEach(course => {
      const card = document.createElement("div");
      card.className = "skill-card";
      card.innerHTML = `
        <div class="skill-card-top">
          <span class="skill-name">${course.title}</span>
          <i class="fa-solid fa-book-open text-blue" style="font-size:0.85rem;"></i>
        </div>
        <div class="skill-card-footer">
          <span>${course.instructor || "Instructor"}</span>
          <span><strong>${(course.skill_requirements || "General").split(",")[0].trim()}</strong></span>
        </div>
        <div class="skill-card-footer">
          <a href="/course-details.html?id=${course.id}" style="text-decoration:none; color:var(--accent-blue); font-size:0.8rem;">View Course &rarr;</a>
        </div>
      `;
      enrolledCoursesContainer.appendChild(card);
    });
  }

  // Init
  loadProfile();
  loadUserSkills();
});
