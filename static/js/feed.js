// js/feed.js
// Depends on api.js and navbar.js (loaded first)

const strip = document.getElementById("currently-watching-strip");
const stripEmpty = document.getElementById("currently-watching-empty");

const activityFeed = document.getElementById("activity-feed");
const feedEmptyNoFollows = document.getElementById("feed-empty-no-follows");
const feedEmptyNoActivity = document.getElementById("feed-empty-no-activity");
const loadMoreBtn = document.getElementById("load-more-feed-btn");

let nextCursor = null;
let animeCache = {};

async function init() {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
    return;
  }

  const me = await api.get("/users/me", true);
  await loadCurrentlyWatching(me.username);
  await loadFeed();

  loadMoreBtn.addEventListener("click", () => loadFeed(nextCursor));
}

async function loadCurrentlyWatching(username) {
  const res = await api.get(`/entries/${username}?status=Watching&page_size=15`, true);

  if (res.data.length === 0) {
    stripEmpty.classList.remove("hidden");
    return;
  }

  await Promise.all(
    res.data.map(async (entry) => {
      if (!animeCache[entry.anime_id]) {
        try {
          animeCache[entry.anime_id] = await api.get(`/anime/${entry.anime_id}`);
        } catch {
          animeCache[entry.anime_id] = null;
        }
      }
    })
  );

  strip.innerHTML = "";
  res.data.forEach((entry) => {
    const anime = animeCache[entry.anime_id];
    const title = anime ? anime.title : `Anime #${entry.anime_id}`;
    const poster = anime ? resolveImageUrl(anime.picture) : "";
    const total = anime ? anime.episodes : "?";

    const item = document.createElement("a");
    item.href = `anime.html?id=${entry.anime_id}`;
    item.className = "shrink-0 w-24";
    item.innerHTML = `
      <figure class="aspect-[2/3] rounded-lg overflow-hidden bg-base-300">
        <img src="${poster}" alt="${title}" class="w-full h-full object-cover" onerror="this.style.display='none'" />
      </figure>
      <p class="text-xs mt-1 text-base-content/60">Ep ${entry.episode ?? 0}/${total}</p>
    `;
    strip.appendChild(item);
  });
}

function describeEvent(event) {
  const meta = event.event_metadata || {};
  const from = meta.from_episode;
  const to = meta.to_episode;

  switch (event.event_type) {
    case "Watched":
    case "Rewatched": {
      const verb = event.event_type === "Rewatched" ? "rewatched" : "watched";

      // No episode movement recorded — fall back to generic phrasing
      if (from == null || to == null || to <= from) {
        return event.event_type === "Rewatched" ? "is rewatching" : "started watching";
      }

      // Went from 0 -> N: first time watching up to episode N
      if (from === 0) {
        return to === 1
          ? `${verb} episode 1 of`
          : `${verb} episodes 1-${to} of`;
      }

      // Incremented by exactly one episode
      if (to === from + 1) {
        return `${verb} episode ${to} of`;
      }

      // Jumped multiple episodes at once
      return `${verb} episodes ${from + 1}-${to} of`;
    }
    case "Completed":
      return "completed";
    case "Rated":
      return "rated";
    default:
      return event.event_type.toLowerCase();
  }
}

async function loadFeed(cursor = null) {
  const params = new URLSearchParams({ limit: 20 });
  if (cursor) params.append("cursor", cursor);

  const res = await api.get(`/feed/?${params}`, true);

  if (!cursor) activityFeed.innerHTML = "";

  const hasEvents = res.data && res.data.length > 0;

  if (!cursor && !hasEvents) {
    // No prior events at all — show a generic empty state
    // (the API doesn't currently distinguish "follows nobody" vs "no activity",
    // so this uses one combined message; see follows count via /users/me if you
    // want to split this further later)
    feedEmptyNoActivity.classList.remove("hidden");
    loadMoreBtn.classList.add("hidden");
    return;
  }

  res.data.forEach((event) => {
    if (!event) return;
    const meta = event.event_metadata || {};
    const card = document.createElement("div");
    card.className = "flex items-start gap-3 p-3 rounded-lg bg-base-100 shadow-sm";
    card.innerHTML = `
      <div class="avatar avatar-placeholder">
        <div class="bg-neutral text-neutral-content rounded-full w-10 flex items-center justify-center">
          <span>${event.username.charAt(0).toUpperCase()}</span>
        </div>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm">
          <span class="font-semibold">${event.username}</span>
          ${describeEvent(event)}
          <a href="anime.html?id=${event.anime_id}" class="font-semibold link link-hover">${event.anime_name}</a>
          ${event.event_type === "Rated" && meta.score ? `<span class="badge badge-warning badge-sm ml-1">${meta.score}/10</span>` : ""}
        </p>
        <p class="text-xs text-base-content/50 mt-0.5">${timeAgo(event.created_at)}</p>
      </div>
    `;
    activityFeed.appendChild(card);
  });

  nextCursor = res.next;
  loadMoreBtn.classList.toggle("hidden", !res.next);
}

function timeAgo(isoString) {
  // Backend sends UTC timestamps. If the string is missing an explicit UTC
  // marker (no trailing "Z" or "+00:00" offset), the browser would otherwise
  // parse it as local time instead of UTC — throwing every timestamp off by
  // however many hours the user's timezone is offset from UTC.
  const hasTimezoneMarker = /Z$|[+-]\d{2}:?\d{2}$/.test(isoString);
  const normalized = hasTimezoneMarker ? isoString : `${isoString}Z`;

  const seconds = Math.floor((Date.now() - new Date(normalized)) / 1000);

  if (seconds < 0) return "just now"; // guard against tiny clock-skew putting this slightly in the future
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

init();