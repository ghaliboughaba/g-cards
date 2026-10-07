/* ============================================================
   app.js  --  the page you see.

   It asks the server "what is happening?" every second, and
   draws the answer on the screen. When you click a button, it
   tells the server what you want to do.
   ============================================================ */

let world = null;            // the latest news from the server
let myId = localStorage.getItem("gcards_player"); // our player id
let socket = null;

/* ---------- small helpers ---------- */
const $ = (id) => document.getElementById(id);

function fmtTime(seconds) {
  seconds = Math.max(0, Math.round(seconds));
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function toast(msg, ok) {
  const t = $("toast");
  t.textContent = msg;
  t.className = "toast" + (ok ? " ok" : "");
  clearTimeout(t._timer);
  t._timer = setTimeout(() => (t.className = "toast hidden"), 2500);
}

function showScreen(name) {
  ["join", "voting", "game", "finished"].forEach((s) => {
    $("screen-" + s).classList.toggle("hidden", s !== name);
  });
}

/* ---------- talk to the server ---------- */
async function getState() {
  const r = await fetch("/api/state" + (myId ? "?player_id=" + myId : ""));
  world = await r.json();
  render();
}

async function action(payload) {
  payload.player_id = myId;
  const r = await fetch("/api/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await r.json();
  if (data.error) toast(data.error);
  return data;
}

async function join(name, country) {
  const r = await fetch("/api/join", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, country }),
  });
  const data = await r.json();
  if (data.error) { toast(data.error); return; }
  myId = data.player_id;
  localStorage.setItem("gcards_player", myId);
  toast("Welcome, " + name + "!", true);
  getState();
}

/* ---------- live updates ---------- */
function connect() {
  socket = new WebSocket((location.protocol === "https:" ? "wss" : "ws") + "://" + location.host + "/ws");
  socket.onmessage = (e) => {
    world = JSON.parse(e.data);
    render();
  };
  socket.onclose = () => setTimeout(connect, 2000);
}

/* ============================================================
   DRAW THE SCREEN
   ============================================================ */
function me() {
  return world && myId ? world.players[myId] : null;
}

function render() {
  if (!world) return;
  if (world.phase === "finished") { showScreen("finished"); renderFinished(); return; }
  if (!me() || me().is_bot) { showScreen("join"); renderJoin(); return; }
  if (world.phase === "voting") { showScreen("voting"); renderVoting(); return; }
  showScreen("game");
  renderGame();
}

/* ---------- join screen ---------- */
function renderJoin() {
  const box = $("country-list");
  box.innerHTML = "";
  world.countries.forEach((c) => {
    const owner = Object.values(world.players).find((p) => p.country === c.id);
    const taken = owner && !owner.is_bot;
    const el = document.createElement("div");
    el.className = "country-card" + (taken ? " taken" : "");
    el.innerHTML = `<div class="flag">${c.flag}</div><div class="cname">${c.name}</div>
      <div style="color:var(--muted);font-size:12px">${c.capital}</div>`;
    if (!taken) {
      el.onclick = () => {
        const name = $("name-input").value.trim();
        if (!name) { toast("Please type your name first."); return; }
        join(name, c.id);
      };
    }
    box.appendChild(el);
  });
}

/* ---------- voting screen ---------- */
function renderVoting() {
  $("vote-timer").textContent = fmtTime(world.vote_time_left);
  const mine = world.votes[myId];
  const counts = {};
  Object.values(world.votes).forEach((c) => (counts[c] = (counts[c] || 0) + 1));
  const grid = $("vote-grid");
  grid.innerHTML = "";
  world.century_choices.forEach((c) => {
    const b = document.createElement("button");
    b.className = "vote-btn" + (mine === c ? " chosen" : "");
    b.innerHTML = `${c}00<small>${counts[c] || 0} vote(s)</small>`;
    b.onclick = () => action({ action: "vote", century: c });
    grid.appendChild(b);
  });
}

/* ---------- game screen ---------- */
function renderGame() {
  const p = me();

  // top bar
  const paused = world.paused;
  $("phase-title").textContent = paused
    ? "⏸️ PAUSED"
    : (world.sub_phase === "war" ? "⚔️ WAR!" : "🔨 Build time");
  $("timer").textContent = fmtTime(world.time_left);
  $("century-label").textContent =
    `Century ${world.century}00 — ${world.century_index + 1} of ${world.total_centuries}`;

  // pause button: only shown when you are the only human player
  const pauseBtn = $("pause-btn");
  if (world.can_pause) {
    pauseBtn.classList.remove("hidden");
    pauseBtn.textContent = paused ? "▶️ Resume" : "⏸️ Pause";
  } else {
    pauseBtn.classList.add("hidden");
  }

  const mats = world.materials
    .map((m) => `<span class="chip">${matEmoji(m)} ${m} <b>${p.materials[m] || 0}</b></span>`)
    .join("");
  $("resources").innerHTML =
    `<span class="chip">💰 money <b>${p.money}</b></span>
     <span class="chip">🏗️ building pts <b>${p.building_points}</b></span>
     <span class="chip">🔬 knowledge <b>${p.knowledge_points}</b></span>
     <span class="chip">⚔️ war pts <b>${p.war_points}</b></span>
     <span class="chip">🛡️ security <b>${p.security_points}</b></span>
     ${mats}`;

  renderMyCities(p);
  renderMap(p);
  renderWarPanel(p);
  renderPlayers();
  renderEvents();
  renderTechs(p);
  renderTroops(p);
  renderMaterials(p);
  renderChat();
}

function matEmoji(m) {
  return { iron: "⛓️", stone: "🪨", gold: "🪙", diamond: "💎" }[m] || "•";
}

function renderMyCities(p) {
  const box = $("my-cities");
  if (!p.cities.length) { box.innerHTML = "<i>You have no cities! 😢</i>"; return; }
  box.innerHTML = "";
  p.cities.forEach((cid) => {
    const city = world.cities[cid];
    const div = document.createElement("div");
    div.className = "city";
    const built = Object.entries(city.buildings)
      .map(([b, n]) => `${world.buildings[b].emoji}${n}`).join(" ") || "nothing yet";
    div.innerHTML = `
      <div class="city-head"><span class="city-name">${city.is_capital ? "⭐ " : ""}${city.name}</span>
        <span style="color:var(--muted);font-size:12px">🛡️ ${city.defense}</span></div>
      <div class="city-stats">👥 ${city.population} people · 😊 ${city.satisfaction}% · built: ${built}</div>
      <div class="build-row"></div>`;
    const row = div.querySelector(".build-row");
    Object.entries(world.buildings).forEach(([bid, b]) => {
      const btn = document.createElement("button");
      btn.className = "mini";
      btn.title = b.info;
      const matCost = Object.entries(b.materials || {})
        .map(([m, n]) => `${matEmoji(m)}${n}`).join(" ");
      btn.innerHTML = `${b.emoji} ${b.name}<br><small>💰${b.cost_money} 🏗️${b.cost_bp} ${matCost}</small>`;
      btn.onclick = () => action({ action: "build", city: cid, building: bid });
      row.appendChild(btn);
    });
    box.appendChild(div);
  });
}

function ownerColor(city) {
  if (!city.owner) return "#5a6a86";
  const o = world.players[city.owner];
  return o ? o.color : "#5a6a86";
}

function renderMap(p) {
  const map = $("map");
  map.innerHTML = "";
  world.countries.forEach((c) => {
    const cities = Object.values(world.cities).filter((ci) => ci.country === c.id);
    const div = document.createElement("div");
    div.className = "map-country";
    div.style.borderColor = c.color;
    div.innerHTML = `<div class="mc-title">${c.flag} ${c.name}</div>`;
    cities.forEach((ci) => {
      const token = document.createElement("div");
      token.className = "city-token" + (ci.owner === myId ? " mine" : "");
      if (world.sub_phase === "war" && ci.owner !== myId) token.classList.add("attackable");
      token.style.background = ownerColor(ci);
      token.textContent = `${ci.name} (👥${ci.population})`;
      if (world.sub_phase === "war" && ci.owner !== myId) {
        token.onclick = () => attack(ci.id);
      }
      div.appendChild(token);
    });
    map.appendChild(div);
  });
}

function attack(cityId) {
  action({ action: "target", city: cityId }).then(() => {
    if (world.sub_phase === "war") toast("Target chosen! The battle is automatic. ⚔️", true);
  });
}

function renderWarPanel(p) {
  const box = $("war-panel");
  if (world.sub_phase !== "war") {
    box.innerHTML = `<p style="color:var(--muted);font-size:13px">War comes at the end of the century. Get ready! ⚔️</p>`;
    return;
  }
  if (!p.alive) { box.innerHTML = "<i>You are out of the game.</i>"; return; }
  const target = p.target ? world.cities[p.target] : null;
  box.innerHTML = target
    ? `<p style="color:var(--good)">🎯 Attacking <b>${target.name}</b> automatically at the end of the war.</p>`
    : `<p style="color:var(--bad)">Click an enemy city on the map to attack it!</p>`;
}

function renderPlayers() {
  const box = $("players");
  box.innerHTML = "";
  const list = Object.values(world.players).sort((a, b) => b.cities.length - a.cities.length);
  list.forEach((p) => {
    const row = document.createElement("div");
    row.className = "player-row" + (p.alive ? "" : " dead");
    row.innerHTML = `<span><span class="dot" style="background:${p.color}"></span>${p.flag} ${p.name}</span>
      <span style="color:var(--muted);font-size:12px">🏙️ ${p.cities.length} · 🪖 ${Object.values(p.troops || {}).reduce((a, b) => a + b, 0)}
      ${p.id === myId ? "" : `<button class="mini" data-ally="${p.id}">🤝</button>`}</span>`;
    box.appendChild(row);
  });
  box.querySelectorAll("[data-ally]").forEach((b) => {
    b.onclick = () => action({ action: "ally", other: b.dataset.ally });
  });
}

function renderEvents() {
  const box = $("events");
  box.innerHTML = world.events.map((e) => `<div>${e.text}</div>`).join("");
  box.scrollTop = box.scrollHeight;
}

function renderTechs(p) {
  const box = $("techs");
  box.innerHTML = "";
  Object.entries(world.techs).forEach(([tid, t]) => {
    const known = p.techs.includes(tid);
    const btn = document.createElement("button");
    btn.className = "mini";
    btn.style.margin = "3px";
    btn.title = t.info;
    btn.innerHTML = `${t.emoji} ${t.name} ${known ? "✅" : `<small>🔬${t.cost_kp}</small>`}`;
    if (!known) btn.onclick = () => action({ action: "research", tech: tid });
    box.appendChild(btn);
  });
}

function renderTroops(p) {
  const box = $("troops");
  box.innerHTML = "";
  Object.entries(world.troops).forEach(([tid, t]) => {
    const count = (p.troops || {})[tid] || 0;
    const btn = document.createElement("button");
    btn.className = "mini";
    btn.style.margin = "3px";
    btn.title = t.info || `attack ${t.attack} · defense ${t.defense}`;
    const mat = Object.entries(t.materials || {}).map(([m, n]) => `${matEmoji(m)}${n}`).join(" ");
    btn.innerHTML = `${t.emoji} ${t.name} ×${count}<br><small>💰${t.money} 🏗️${t.cost_bp} ${mat}</small>`;
    btn.onclick = () => action({ action: "train", troop: tid, amount: 1 });
    box.appendChild(btn);
  });
}

function renderMaterials(p) {
  const box = $("materials");
  box.innerHTML = "";
  world.materials.forEach((m) => {
    const btn = document.createElement("button");
    btn.className = "mini";
    btn.style.margin = "3px";
    btn.innerHTML = `${matEmoji(m)} buy ${m} <small>💰${world.material_price[m]}</small>`;
    btn.onclick = () => buyMaterial(m);
    box.appendChild(btn);
  });
}

function buyMaterial(material) {
  const price = world.material_price[material];
  const answer = prompt(
    `How much ${material} do you want to buy?\n(1 ${material} = ${price} money)`,
    "1"
  );
  if (answer === null) return; // cancelled
  const amount = parseInt(answer, 10);
  if (!Number.isFinite(amount) || amount < 1) {
    toast("Please type a whole number of 1 or more.");
    return;
  }
  action({ action: "buy", material, amount });
}

function renderChat() {
  const log = $("chat-log");
  log.innerHTML = world.chat
    .map((c) => `<div><span class="who" style="color:${c.color}">${c.name}:</span> ${escapeHtml(c.text)}</div>`)
    .join("");
  log.scrollTop = log.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

/* ---------- finished screen ---------- */
function renderFinished() {
  const box = $("final-scores");
  box.innerHTML = world.scores.map((s, i) => `
    <div class="player-row" style="font-size:16px">
      <span>${["🥇", "🥈", "🥉"][i] || "•"} ${s.flag} ${s.name}</span>
      <span>👥 ${s.citizens} · 🏗️ ${s.buildings} · 📦 ${s.resources} · <b>${s.score} pts</b></span>
    </div>`).join("");
}

/* ============================================================
   BUTTONS
   ============================================================ */
$("pause-btn").onclick = () => action({ action: "pause" });
$("chat-send").onclick = () => {
  const input = $("chat-text");
  if (input.value.trim()) { action({ action: "chat", text: input.value }); input.value = ""; }
};
$("chat-text").addEventListener("keydown", (e) => {
  if (e.key === "Enter") $("chat-send").click();
});
$("play-again").onclick = async () => {
  await action({ action: "reset" });
  localStorage.removeItem("gcards_player");
  myId = null;
  getState();
};

/* ---------- start ---------- */
getState();
connect();
