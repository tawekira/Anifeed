// js/mylist.js
// Depends on api.js and navbar.js (loaded first)

let currentUsername = null;
let currentStatus = "";
let currentPage = 1;
const PAGE_SIZE = 20;
let allEntries = []; // accumulated across "load more" clicks
let animeCache = {}; // anime_id -> Anime object, to avoid refetching

const entriesList = document.getElementById("entries-list");
const entriesEmpty = document.getElementById("entries-empty");
const loadMoreBtn = document.getElementById("load-more-btn");

async function init() {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
    return;
  }

  const me = await api.get("/users/me", true);
  currentUsername = me.username;

  wireStatusTabs();
  wireModal();
  await loadEntries(true);
}

function wireStatusTabs() {
  document.querySelectorAll(".status-option").forEach((option) => {
    option.addEventListener("click", async () => {
      currentStatus = option.dataset.status;
      document.getElementById("status-filter-label").textContent =
        option.dataset.status || "All";

      // Close the dropdown by removing focus
      document.activeElement.blur();

      currentPage = 1;
      allEntries = [];
      await loadEntries(true);
    });
  });

  loadMoreBtn.addEventListener("click", async () => {
    currentPage += 1;
    await loadEntries(false);
  });
}

async function loadEntries(reset) {
  const params = new URLSearchParams({
    page: currentPage,
    page_size: PAGE_SIZE,
  });
  if (currentStatus) params.append("status", currentStatus);

  const res = await api.get(`/entries/${currentUsername}?${params}`, true);

  if (reset) allEntries = res.data;
  else allEntries = [...allEntries, ...res.data];

  await hydrateAnimeData(res.data);
  renderEntries();

  const loadedSoFar = currentPage * PAGE_SIZE;
  loadMoreBtn.classList.toggle("hidden", loadedSoFar >= res.total);
}

// Fetch anime details for any entries whose anime we haven't cached yet
async function hydrateAnimeData(entries) {
  const missingIds = [...new Set(entries.map((e) => e.anime_id))].filter(
    (id) => !animeCache[id]
  );
  await Promise.all(
    missingIds.map(async (id) => {
      try {
        animeCache[id] = await api.get(`/anime/${id}`);
      } catch {
        animeCache[id] = null;
      }
    })
  );
}

function renderEntries() {
  entriesList.innerHTML = "";
  entriesEmpty.classList.toggle("hidden", allEntries.length > 0);

  allEntries.forEach((entry) => {
    const anime = animeCache[entry.anime_id];
    const title = anime ? anime.title : `Anime #${entry.anime_id}`;
    const poster = anime ? resolveImageUrl(anime.picture) : "";
    const totalEpisodes = anime ? anime.episodes : "?";

    const row = document.createElement("div");
    row.className = "flex items-center gap-3 p-3 rounded-lg bg-base-100 shadow-sm";
    row.innerHTML = `
      <a href="anime.html?id=${entry.anime_id}" class="shrink-0">
        <figure class="w-12 h-16 rounded overflow-hidden bg-base-300">
          <img src="${poster}" alt="${title}" class="w-full h-full object-cover" onerror="this.style.display='none'" />
        </figure>
      </a>
      <div class="flex-1 min-w-0">
        <a href="anime.html?id=${entry.anime_id}" class="font-medium hover:link line-clamp-1">${title}</a>
        <div class="flex items-center gap-2 mt-1 flex-wrap">
          <span class="badge badge-sm badge-info">${entry.status}</span>
          <span class="text-xs text-base-content/60">Ep ${entry.episode ?? 0} / ${totalEpisodes}</span>
          ${entry.score ? `<span class="badge badge-sm badge-warning">${entry.score}/10</span>` : ""}
        </div>
      </div>
      <div class="flex gap-2 shrink-0">
        <button class="btn btn-xs btn-outline edit-btn">Edit</button>
        <button class="btn btn-xs btn-outline btn-error delete-btn">Delete</button>
      </div>
    `;

    row.querySelector(".edit-btn").addEventListener("click", () => openEditModal(entry));
    row.querySelector(".delete-btn").addEventListener("click", () => deleteEntry(entry));

    entriesList.appendChild(row);
  });
}

// --- Edit modal ---

let editingEntry = null;
const modal = document.getElementById("edit_entry_modal");
const statusInput = document.getElementById("edit-status-input");
const episodeInput = document.getElementById("edit-episode-input");
const ratingInput = document.getElementById("edit-rating-input");
const editError = document.getElementById("edit-error-message");

function wireModal() {
  document.getElementById("cancel-entry-btn").addEventListener("click", () => modal.close());
  document.getElementById("save-entry-btn").addEventListener("click", saveEntry);
}

function openEditModal(entry) {
  editingEntry = entry;
  statusInput.value = entry.status;
  episodeInput.value = entry.episode ?? 0;
  ratingInput.value = entry.score ?? "";
  editError.classList.add("hidden");
  modal.showModal();
}

async function saveEntry() {
  editError.classList.add("hidden");
  const saveBtn = document.getElementById("save-entry-btn");
  saveBtn.disabled = true;

  try {
    await api.post(
      "/entries/",
      {
        anime_id: editingEntry.anime_id,
        status: statusInput.value,
        episode: parseInt(episodeInput.value, 10),
        score: ratingInput.value ? parseInt(ratingInput.value, 10) : null,
      },
      true
    );

    modal.close();
    currentPage = 1;
    allEntries = [];
    await loadEntries(true);
  } catch (err) {
    editError.textContent = err.message || "Could not update entry";
    editError.classList.remove("hidden");
  } finally {
    saveBtn.disabled = false;
  }
}

async function deleteEntry(entry) {
  if (!confirm("Remove this from your list?")) return;
  try {
    await api.del(`/entries/${entry.id}`, true);
    allEntries = allEntries.filter((e) => e.id !== entry.id);
    renderEntries();
  } catch (err) {
    alert(err.message || "Could not delete entry");
  }
}

init();