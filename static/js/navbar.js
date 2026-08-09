// js/navbar.js
// Injects the shared navbar component and wires it up with real data.
// Depends on api.js being loaded first.

async function loadNavbar() {
  const container = document.getElementById("navbar-container");
  if (!container) return;

  const res = await fetch("components/navbar.html", { cache: "no-store" });
  container.innerHTML = await res.text();

  await populateNavbar();
  wireNavbarEvents();

  if (isLoggedIn()) {
    await loadNotifications();
  }
}

async function populateNavbar() {
  const usernameEl = document.getElementById("navbar-username");

  if (!isLoggedIn()) {
    // Logged-out state: hide avatar/profile stuff, could show a Login link instead
    const navbarEnd = document.querySelector(".navbar-end");
    if (navbarEnd) {
      navbarEnd.innerHTML = `<a href="login.html" class="btn btn-primary btn-sm">Log in</a>`;
    }
    return;
  }

  try {
    const me = await api.get("/users/me", true);
    if (usernameEl) usernameEl.textContent = me.username;
    const initialEl = document.getElementById("navbar-avatar-initial");
    if (initialEl) initialEl.textContent = me.username.charAt(0).toUpperCase();
  } catch (err) {
    // Token invalid/expired — clear it and treat as logged out
    if (err.status === 401) {
      clearToken();
      window.location.href = "login.html";
    }
  }
}

function wireNavbarEvents() {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      clearToken();
      window.location.href = "login.html";
    });
  }

  const notificationsToggle = document.getElementById("notifications-toggle");
  if (notificationsToggle) {
    // Attach to the wrapper too (parentElement), not just the button itself —
    // a sizing/padding mismatch between the wrapper and the button can mean
    // clicks land on the wrapper without actually hitting the button's own box.
    notificationsToggle.addEventListener("click", onNotificationsOpened);
    if (notificationsToggle.parentElement) {
      notificationsToggle.parentElement.addEventListener("click", onNotificationsOpened);
    }
  }
}

async function loadNotifications() {
  try {
    const notifications = await api.get("/notifications/", true);
    renderNotifications(notifications);
  } catch {
    // fail silently — notifications aren't critical to the rest of the page working
  }
}

function renderNotifications(notifications) {
  const badge = document.getElementById("notifications-badge");
  const list = document.getElementById("notifications-list");

  if (notifications.length > 0) {
    badge.textContent = notifications.length > 9 ? "9+" : String(notifications.length);
    badge.classList.remove("hidden");
  } else {
    badge.classList.add("hidden");
  }

  list.innerHTML = "";

  if (notifications.length === 0) {
    list.innerHTML = `<p class="text-sm text-base-content/50 text-center py-4">No new notifications</p>`;
    return;
  }

  notifications.forEach((n) => {
    const item = document.createElement("div");
    item.className = "p-2 rounded-lg hover:bg-base-200 text-sm";
    item.innerHTML = describeNotification(n);
    list.appendChild(item);
  });
}

function describeNotification(n) {
  switch (n.notification_type) {
    case "New Follower":
      return `<span class="font-semibold">${n.actor_username}</span> started following you`;
    default:
      return `${n.actor_username}: ${n.notification_type}`;
  }
}

let notificationsMarkedThisSession = false;

async function onNotificationsOpened() {
  if (notificationsMarkedThisSession) return;
  notificationsMarkedThisSession = true;

  // Optimistically clear the badge right away, then mark as read in the background
  const badge = document.getElementById("notifications-badge");
  if (badge) badge.classList.add("hidden");

  try {
    await api.post("/notifications/read-all", {}, true);
  } catch {
    // if this fails, badge will just reappear on next page load — acceptable
  }
}

loadNavbar();