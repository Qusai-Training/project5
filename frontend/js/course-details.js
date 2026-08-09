/**
 * COURSE-DETAILS.JS - Dynamic Single Course Endpoint Fetcher
 */

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("jwt_token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get("id");
  const container = document.getElementById("courseDetailsContainer");

  if (!courseId) {
    container.innerHTML = `<p>Invalid Course ID provided.</p>`;
    return;
  }

  try {
    const response = await fetch(`/api/courses/${courseId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) throw new Error("Course not found");

    const course = await response.json();

    container.innerHTML = `
      <div style="border-bottom: 1px solid #E2E8F0; padding-bottom: 16px; margin-bottom: 20px;">
        <h1 style="font-size: 1.8rem; color: var(--text-dark); margin-bottom: 8px;">${course.title}</h1>
        <p style="color: var(--text-muted); font-weight:600;">Instructor: ${course.instructor || "Expert Staff"}</p>
      </div>

      <div style="margin-bottom: 24px;">
        <h3>Course Overview</h3>
        <p style="color: #334155; line-height: 1.6; margin-top: 8px;">${course.description}</p>
      </div>

      <div style="margin-bottom: 24px;">
        <h3>Target Skills & Prerequisites</h3>
        <div class="skill-badges" style="margin-top: 10px;">
          ${(course.skill_requirements || "General")
            .split(",")
            .map(skill => `<span class="skill-tag">${skill.trim()}</span>`)
            .join("")}
        </div>
      </div>

      <button id="enrollBtn" style="background: ${course.enrolled ? "#059669" : "var(--accent-blue)"}; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 700; cursor: pointer;" ${course.enrolled ? "disabled" : ""}>
        ${course.enrolled ? "Enrolled ✓" : "Enroll in Course"}
      </button>
    `;

    const enrollBtn = document.getElementById("enrollBtn");
    if (enrollBtn) {
      enrollBtn.addEventListener("click", async () => {
        enrollBtn.disabled = true;
        enrollBtn.textContent = "Enrolling...";
        try {
          const res = await fetch(`/api/courses/${courseId}/enroll`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
          });
          if (res.status === 401) {
            localStorage.removeItem("jwt_token");
            window.location.href = "login.html";
            return;
          }
          const data = await res.json();
          if (res.ok) {
            enrollBtn.textContent = "Enrolled ✓";
            enrollBtn.style.background = "#059669";
          } else {
            enrollBtn.disabled = false;
            enrollBtn.textContent = data.message || "Enrollment failed";
          }
        } catch (err) {
          enrollBtn.disabled = false;
          enrollBtn.textContent = "Retry";
        }
      });
    }

  } catch (err) {
    container.innerHTML = `<p class="error-msg">Failed to load course details.</p>`;
  }
});