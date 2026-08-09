// js/anime.js
// Depends on api.js and navbar.js (loaded first)

const params = new URLSearchParams(window.location.search);
const animeId = params.get("id");

let currentUsername = null;
let currentEntry = null; // null if user has no entry for this anime

async function init() {
  if (!animeId) {
    document.body.innerHTML = "<p class='p-8 text-center'>No anime specified.</p>";
    return;
  }

  await loadAnime();

  if (isLoggedIn()) {
    try {
      const me = await api.get("/users/me", true);
      currentUsername = me.username;
      await loadUserEntry();
    } catch {
      // token invalid; navbar.js already handles redirect on 401
    }
  } else {
    // Logged out: show Add to List button, clicking it should send them to login
    document.getElementById("add-to-list-btn").classList.remove("hidden");
    document.getElementById("add-to-list-btn").onclick = () => {
      window.location.href = "login.html";
    };
  }

  wireModal();
}

async function loadAnime() {
  let anime;
  try {
    anime = await api.get(`/anime/${animeId}`);
  } catch (err) {
    document.body.innerHTML = `<p class='p-8 text-center'>Anime not found.</p>`;
    return;
  }

  document.title = `${anime.title} — Anifeed`;
  document.getElementById("anime-title").textContent = anime.title;

  const posterEl = document.getElementById("anime-poster");
  posterEl.src = resolveImageUrl(anime.picture) || "";
  posterEl.alt = anime.title;
  posterEl.onerror = () => { posterEl.style.display = "none"; };

  const statusEl = document.getElementById("anime-status");
  statusEl.textContent = anime.status;
  statusEl.className = `badge shrink-0 ${statusBadgeClass(anime.status)}`;

  const seasonYear = anime.year ? `${anime.season} ${anime.year}` : anime.season;
  document.getElementById("anime-meta").textContent =
    `${anime.type} · ${anime.episodes} episodes · ${seasonYear}`;

  const tagsEl = document.getElementById("anime-tags");
  tagsEl.innerHTML = "";

  const MAX_TAGS = 6;
  const allTags = anime.tags || [];
  const visibleTags = allTags.slice(0, MAX_TAGS);
  const remaining = allTags.length - MAX_TAGS;

  visibleTags.forEach((tag) => {
    const span = document.createElement("span");
    span.className = "badge badge-outline";
    span.textContent = tag;
    tagsEl.appendChild(span);
  });

  if (remaining > 0) {
    const more = document.createElement("span");
    more.className = "badge badge-ghost";
    more.textContent = `+${remaining} more`;
    tagsEl.appendChild(more);
  }

  window._currentAnime = anime; // stash for modal (episode max, etc.)
}

function statusBadgeClass(status) {
  if (status === "Ongoing") return "badge-info";
  if (status === "Finished") return "badge-success";
  if (status === "Upcoming") return "badge-neutral";
  return "badge-ghost";
}

async function loadUserEntry() {
  const res = await api.get(`/entries/${currentUsername}?anime_id=${animeId}`, true);
  currentEntry = res.data[0] ?? null;
  renderEntryState();
}

function renderEntryState() {
  const entryBlock = document.getElementById("user-entry-block");
  const addBtn = document.getElementById("add-to-list-btn");
  const ratingBlock = document.getElementById("user-rating-block");

  if (currentEntry) {
    entryBlock.classList.remove("hidden");
    addBtn.classList.add("hidden");

    document.getElementById("user-entry-status").textContent = currentEntry.status;
    document.getElementById("user-entry-episode").textContent =
      `${currentEntry.episode ?? 0} / ${window._currentAnime.episodes}`;

    if (currentEntry.score) {
      ratingBlock.classList.remove("hidden");
      document.getElementById("user-rating-value").textContent = `${currentEntry.score}/10`;
    } else {
      ratingBlock.classList.add("hidden");
    }
  } else {
    entryBlock.classList.add("hidden");
    addBtn.classList.remove("hidden");
  }
}

// --- Edit/Add modal ---

const modal = document.getElementById("edit_entry_modal");
const statusInput = document.getElementById("edit-status-input");
const episodeInput = document.getElementById("edit-episode-input");
const ratingInput = document.getElementById("edit-rating-input");

function wireModal() {
  document.getElementById("save-entry-btn").addEventListener("click", saveEntry);

  // Pre-fill modal with current entry values right before it opens
  document.getElementById("edit-entry-btn")?.addEventListener("click", prefillModal);
  document.getElementById("add-to-list-btn")?.addEventListener("click", () => {
    if (isLoggedIn()) prefillModal();
  });
}

function prefillModal() {
  if (currentEntry) {
    statusInput.value = currentEntry.status;
    episodeInput.value = currentEntry.episode ?? 0;
    ratingInput.value = currentEntry.score ?? "";
  } else {
    statusInput.value = "Watching";
    episodeInput.value = 0;
    ratingInput.value = "";
  }
  if (window._currentAnime) {
    episodeInput.max = window._currentAnime.episodes || "";
  }
}

async function saveEntry() {
  const saveBtn = document.getElementById("save-entry-btn");
  saveBtn.disabled = true;

  try {
    const updated = await api.post(
      "/entries/",
      {
        anime_id: parseInt(animeId, 10),
        status: statusInput.value,
        episode: parseInt(episodeInput.value, 10),
        score: ratingInput.value ? parseInt(ratingInput.value, 10) : null,
      },
      true
    );

    currentEntry = updated;
    renderEntryState();
    modal.close();
  } catch (err) {
    alert(err.message || "Could not save entry");
  } finally {
    saveBtn.disabled = false;
  }
}

init();