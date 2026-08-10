/**
 * PROFILE.JS - Profile Information, Membership & Password Management
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";

  // Elements
  const navUsername = document.getElementById("navUsername");
  const navAvatar = document.getElementById("navAvatar");
  const profileFullName = document.getElementById("profileFullName");
  const profileEmail = document.getElementById("profileEmail");
  const profileAvatar = document.getElementById("profileAvatar");

  const infoName = document.getElementById("infoName");
  const infoUsername = document.getElementById("infoUsername");
  const infoEmail = document.getElementById("infoEmail");

  const membershipStatus = document.getElementById("membershipStatus");
  const membershipExpiry = document.getElementById("membershipExpiry");
  const membershipMessage = document.getElementById("membershipMessage");
  const renewMembershipBtn = document.getElementById("renewMembershipBtn");
  const cancelMembershipBtn = document.getElementById("cancelMembershipBtn");

  const changePasswordForm = document.getElementById("changePasswordForm");
  const changePasswordMessage = document.getElementById("changePasswordMessage");

  const mobileMenuToggle = document.getElementById("mobileMenuToggle");
  const navRight = document.getElementById("navRight");

  // Exit / Logout Button Element
  const logoutBtn = document.getElementById("logoutBtn");

  const mobileMenuToggle = document.getElementById("mobileMenuToggle");
  const navRight = document.getElementById("navRight");

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener("click", () => {
      navRight.classList.toggle("active");
    });
  }

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener("click", () => {
      navRight.classList.toggle("active");
    });
  }

  function getAuthToken() {
    return localStorage.getItem("jwt_token");
  }

  function showMessage(element, text, isError) {
    if (!element) return;
    element.textContent = text;
    element.style.color = isError ? "#B91C1C" : "#059669";
  }

  function formatDate(isoString) {
    if (!isoString) return "-";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return "-";
    return date.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function renderMembership(membership) {
    const status = (membership && membership.status) || "active";
    membershipStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    membershipExpiry.textContent = formatDate(membership && membership.expires_at);

    if (status === "cancelled") {
      membershipStatus.className = "info-value";
      membershipStatus.style.color = "#B91C1C";
      renewMembershipBtn.disabled = false;
      cancelMembershipBtn.disabled = true;
    } else if (status === "expired") {
      membershipStatus.className = "info-value";
      membershipStatus.style.color = "#D97706";
      renewMembershipBtn.disabled = false;
      cancelMembershipBtn.disabled = true;
    } else {
      membershipStatus.className = "info-value status-active";
      renewMembershipBtn.disabled = false;
      cancelMembershipBtn.disabled = false;
    }
  }

  async function fetchJSON(url, options) {
    const token = getAuthToken();
    const res = await fetch(url, {
      ...options,
      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" }
    });
    if (res.status === 401) {
      localStorage.removeItem("jwt_token");
      window.location.href = "/login.html";
      throw new Error("Unauthorized");
    }
    const data = await res.json();
    return { res, data };
  }

  // Load User Profile Data
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

        // Header & Nav
        if (navUsername) navUsername.textContent = username;
        if (navAvatar) navAvatar.textContent = initial;
        if (profileAvatar) profileAvatar.textContent = initial;

        // Details Section
        profileFullName.textContent = fullName;
        profileEmail.textContent = user.email || "";

        infoName.textContent = fullName;
        infoUsername.textContent = username;
        infoEmail.textContent = user.email || "N/A";

        // Membership
        renderMembership(user.membership || { status: "active" });
      }
    } catch (err) {
      console.error("Profile load error:", err);
    }
  }

  // Membership actions
  if (renewMembershipBtn) {
    renewMembershipBtn.addEventListener("click", async () => {
      renewMembershipBtn.disabled = true;
      showMessage(membershipMessage, "Renewing membership...", false);
      try {
        const { res, data } = await fetchJSON(`${API_BASE}/users/membership/renew`, { method: "POST", body: "{}" });
        if (res.ok) {
          renderMembership(data.membership);
          showMessage(membershipMessage, data.message || "Membership renewed successfully!", false);
        } else {
          showMessage(membershipMessage, data.message || "Could not renew membership.", true);
        }
      } catch (err) {
        showMessage(membershipMessage, "Renewal failed. Please try again.", true);
      } finally {
        renewMembershipBtn.disabled = false;
      }
    });
  }

  if (cancelMembershipBtn) {
    cancelMembershipBtn.addEventListener("click", async () => {
      if (!window.confirm("Are you sure you want to cancel your membership? This cannot be undone.")) {
        return;
      }
      cancelMembershipBtn.disabled = true;
      showMessage(membershipMessage, "Cancelling membership...", false);
      try {
        const { res, data } = await fetchJSON(`${API_BASE}/users/membership/cancel`, { method: "POST", body: "{}" });
        if (res.ok) {
          renderMembership(data.membership);
          showMessage(membershipMessage, data.message || "Membership cancelled.", false);
        } else {
          showMessage(membershipMessage, data.message || "Could not cancel membership.", true);
        }
      } catch (err) {
        showMessage(membershipMessage, "Cancellation failed. Please try again.", true);
      } finally {
        cancelMembershipBtn.disabled = false;
      }
    });
  }

  // Change password
  if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const currentPassword = document.getElementById("currentPassword").value;
      const newPassword = document.getElementById("newPassword").value;
      const confirmNewPassword = document.getElementById("confirmNewPassword").value;

      if (!currentPassword || !newPassword || !confirmNewPassword) {
        showMessage(changePasswordMessage, "Please fill in all password fields.", true);
        return;
      }
      if (newPassword !== confirmNewPassword) {
        showMessage(changePasswordMessage, "New passwords do not match.", true);
        return;
      }
      if (newPassword.length < 6) {
        showMessage(changePasswordMessage, "New password must be at least 6 characters long.", true);
        return;
      }

      showMessage(changePasswordMessage, "Updating password...", false);
      try {
        const { res, data } = await fetchJSON(`${API_BASE}/auth/change-password`, {
          method: "POST",
          body: JSON.stringify({ old_password: currentPassword, new_password: newPassword })
        });
        if (res.ok) {
          showMessage(changePasswordMessage, data.message || "Password changed successfully!", false);
          changePasswordForm.reset();
        } else {
          showMessage(changePasswordMessage, data.message || "Could not change password.", true);
        }
      } catch (err) {
        showMessage(changePasswordMessage, "Password change failed. Please try again.", true);
      }
    });
  }

  // Init
  loadProfile();
});
