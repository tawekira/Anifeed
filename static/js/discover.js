// js/discover.js
// Depends on api.js and navbar.js (loaded first)

const animeSearchInput = document.getElementById("anime-search-input");
const animeResults = document.getElementById("anime-results");
const animeEmpty = document.getElementById("anime-empty");
const animeResultsLabel = document.getElementById("anime-results-label");

const userSearchInput = document.getElementById("user-search-input");
const userResults = document.getElementById("user-results");
const userEmpty = document.getElementById("user-empty");

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// --- Anime tab ---

async function loadCurrentlyAiring() {
  animeResultsLabel.textContent = "Currently airing";
  const results = await api.get("/anime/?status=Ongoing&limit=15");
  renderAnimeResults(results);
}

async function searchAnime(query) {
  if (!query) {
    await loadCurrentlyAiring();
    return;
  }
  animeResultsLabel.textContent = `Results for "${query}"`;
  const results = await api.get(`/anime/?q=${encodeURIComponent(query)}&limit=15`);
  renderAnimeResults(results);
}

function renderAnimeResults(results) {
  animeResults.innerHTML = "";
  animeEmpty.classList.toggle("hidden", results.length > 0);

  results.forEach((anime) => {
    const card = document.createElement("a");
    card.href = `anime.html?id=${anime.id}`;
    card.className = "group";
    card.innerHTML = `
      <figure class="aspect-[2/3] rounded-lg overflow-hidden bg-base-300">
        <img src="${resolveImageUrl(anime.picture)}" alt="${anime.title}"
             onerror="this.style.display='none'"
             class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" />
      </figure>
      <p class="mt-2 text-sm font-medium line-clamp-2">${anime.title}</p>
      <p class="text-xs text-base-content/60">${anime.type} · ${anime.status}</p>
    `;
    animeResults.appendChild(card);
  });
}

animeSearchInput.addEventListener(
  "input",
  debounce((e) => searchAnime(e.target.value.trim()), 350)
);

// --- Users tab ---

async function searchUsers(query) {
  userResults.innerHTML = "";
  if (!query) {
    userEmpty.classList.add("hidden");
    return;
  }

  const results = await api.get(`/users/?q=${encodeURIComponent(query)}&limit=10`, isLoggedIn());
  userEmpty.classList.toggle("hidden", results.length > 0);

  results.forEach((user) => {
    const row = document.createElement("div");
    row.className = "flex items-center justify-between p-3 rounded-lg bg-base-100 shadow-sm";
    const followLabel = user.is_following ? "Following" : "Follow";
    const followClasses = user.is_following ? "btn btn-sm btn-neutral" : "btn btn-sm btn-outline";

    row.innerHTML = `
      <div class="flex items-center gap-3">
        <div class="avatar avatar-placeholder">
          <div class="bg-neutral text-neutral-content rounded-full w-10 flex items-center justify-center">
            <span>${user.username.charAt(0).toUpperCase()}</span>
          </div>
        </div>
        <div>
          <p class="font-medium">${user.username}</p>
          <p class="text-xs text-base-content/60">${user.entries_count} anime tracked · ${user.follower_count} followers</p>
        </div>
      </div>
      <button class="${followClasses} follow-btn">${followLabel}</button>
    `;

    const followBtn = row.querySelector(".follow-btn");
    followBtn.addEventListener("click", () => toggleFollow(user.username, followBtn));

    userResults.appendChild(row);
  });
}

async function toggleFollow(username, btn) {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
    return;
  }

  const currentlyFollowing = btn.textContent.trim() === "Following";
  btn.disabled = true;

  try {
    if (currentlyFollowing) {
      await api.del(`/users/${username}/follow`, true);
      btn.textContent = "Follow";
      btn.classList.remove("btn-neutral");
      btn.classList.add("btn-outline");
    } else {
      await api.post(`/users/${username}/follow`, {}, true);
      btn.textContent = "Following";
      btn.classList.remove("btn-outline");
      btn.classList.add("btn-neutral");
    }
  } catch (err) {
    alert(err.message || "Could not update follow status");
  } finally {
    btn.disabled = false;
  }
}

userSearchInput.addEventListener(
  "input",
  debounce((e) => searchUsers(e.target.value.trim()), 350)
);

// --- Init ---
loadCurrentlyAiring();