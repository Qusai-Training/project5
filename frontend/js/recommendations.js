/**
 * RECOMMENDATIONS.JS - Vector Match Recommendation Fetcher
 */

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("jwt_token");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  const recommendationsGrid = document.getElementById("recommendationsGrid");

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ limit: 6 })
    });

    if (!response.ok) throw new Error("Failed to fetch recommendations");

    const recommendations = await response.json();
    renderRecommendations(recommendations);

  } catch (err) {
    recommendationsGrid.innerHTML = `<p class="error-msg">Could not load recommendations at this time.</p>`;
  }

  function renderRecommendations(items) {
    recommendationsGrid.innerHTML = "";

    if (!items || items.length === 0) {
      recommendationsGrid.innerHTML = `<p>No matching courses found for your skill set.</p>`;
      return;
    }

    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "course-card";

      const matchPercent = Math.round((item.match_score || 0.85) * 100);

      card.innerHTML = `
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="background:#E0F2FE; color:#0369A1; font-weight:700; font-size:0.75rem; padding:4px 8px; border-radius:12px;">
              ${matchPercent}% Skill Match
            </span>
          </div>
          <h3 class="course-title">${item.title}</h3>
          <p class="instructor-tag"><i class="fa-solid fa-user-tie"></i> ${item.instructor || "Instructor"}</p>
          <p class="course-description">${item.description}</p>
          <p style="font-size:0.8rem; color:#059669; background:#ECFDF5; padding:6px 10px; border-radius:6px; margin-bottom:12px;">
            <i class="fa-solid fa-circle-info"></i> ${item.explanation || "Recommended based on your target skills."}
          </p>
        </div>
        <div class="course-card-footer">
          <a href="course-details.html?id=${item.id}" class="view-details-btn">View Details</a>
        </div>
      `;

      recommendationsGrid.appendChild(card);
    });
  }
});