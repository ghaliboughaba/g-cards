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
    const botOnly = !!c.bot_only;
    const taken = botOnly || (owner && !owner.is_bot);
    const el = document.createElement("div");
    el.className = "country-card" + (taken ? " taken" : "");
    el.innerHTML = `<div class="flag">${c.flag}</div><div class="cname">${c.name}</div>
      <div style="color:var(--muted);font-size:12px">${botOnly ? "🤖 computer" : c.capital}</div>`;
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

  // difficulty picker
  const dgrid = $("difficulty-grid");
  dgrid.innerHTML = "";
  Object.entries(world.difficulties).forEach(([key, d]) => {
    const b = document.createElement("button");
    b.className = "vote-btn" + (world.difficulty === key ? " chosen" : "");
    b.innerHTML = `${d.emoji} ${d.name}<small>${d.info}</small>`;
    b.onclick = () => action({ action: "difficulty", level: key });
    dgrid.appendChild(b);
  });
}

/* ---------- game screen ---------- */
function renderGame() {
  const p = me();

  // top bar
  const paused = world.paused;
  $("phase-title").textContent = paused
    ? "⏸️ PAUSED"
    : world.sub_phase === "war" ? "⚔️ WAR!"
    : world.sub_phase === "result" ? "💥 Results"
    : "🔨 Build time";
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
  const diff = world.difficulties[world.difficulty];
  $("resources").innerHTML =
    `<span class="chip">💰 money <b>${p.money}</b></span>
     <span class="chip">🏗️ building pts <b>${p.building_points}</b></span>
     <span class="chip">🔬 knowledge <b>${p.knowledge_points}</b></span>
     <span class="chip">⚔️ war pts <b>${p.war_points}</b></span>
     <span class="chip">🛡️ security <b>${p.security_points}</b></span>
     ${mats}
     <span class="chip">${diff.emoji} ${diff.name}</span>`;

  renderMyCities(p);
  renderMap(p);
  renderWarPanel(p);
  renderPlayers();
  renderEvents();
  renderTechs(p);
  renderTroops(p);
  renderMaterials(p);
  renderChat();
  renderWarOverlay(p);
}

/* ---------- the war screen ---------- */
function renderWarOverlay(p) {
  const ov = $("war-overlay");
  const active = world.sub_phase === "war" || world.sub_phase === "result";
  ov.classList.toggle("hidden", !active);
  if (!active) return;

  $("war-century").textContent = world.century;
  $("war-timer").textContent = fmtTime(world.time_left);

  if (world.sub_phase === "war") {
    $("war-subtitle").textContent = p.alive
      ? "Pick a city to attack — the battle happens automatically when the timer ends!"
      : "You were defeated. Watch the battles!";
    renderWarTargets(p);
    renderBattles(world.war_preview, false);
  } else {
    $("war-subtitle").textContent = "💥 The battles are over!";
    $("war-targets").innerHTML = "<p class='muted'>Look at the results on the right ➡️</p>";
    renderBattles(world.war_results, true);
  }
}

function renderWarTargets(p) {
  const box = $("war-targets");
  box.innerHTML = "";
  if (!p.alive) { box.innerHTML = "<p class='muted'>You are out of the game.</p>"; return; }
  const enemies = Object.values(world.cities).filter((c) => c.owner !== myId);
  enemies.sort((a, b) => a.defense - b.defense);
  enemies.forEach((c) => {
    const owner = c.owner ? world.players[c.owner] : null;
    const color = owner ? owner.color : "#5a6a86";
    const b = document.createElement("button");
    b.className = "war-target" + (p.target === c.id ? " chosen" : "");
    b.style.borderColor = color;
    b.innerHTML = `<span class="wt-name"><span class="dot" style="background:${color}"></span>${c.name}</span>
      <small>${owner ? owner.flag + " " + owner.name : "Neutral"} · 🛡️${c.defense} · 👥${c.population}</small>`;
    b.onclick = () => action({ action: "target", city: c.id });
    box.appendChild(b);
  });
}

function renderBattles(rows, showResult) {
  const box = $("war-battles");
  box.innerHTML = "";
  if (!rows || !rows.length) {
    box.innerHTML = "<p class='muted'>No battles chosen yet. Pick a target! 🎯</p>";
    return;
  }
  const maxPow = Math.max(1, ...rows.map((r) => Math.max(r.attack, r.defense)));
  rows.forEach((r) => {
    const mine = r.attacker === myId;
    const captured = showResult && r.captured;
    const card = document.createElement("div");
    card.className = "battle-card" + (mine ? " mine" : "") + (captured ? " captured" : "");
    const aPct = Math.max(4, Math.round((r.attack / maxPow) * 100));
    const dPct = Math.max(4, Math.round((r.defense / maxPow) * 100));
    let outcome = "";
    if (showResult) {
      outcome = r.captured
        ? `<div class="battle-result win">🔥 ${r.attacker_name} CAPTURED ${r.city_name}!</div>`
        : `<div class="battle-result lose">🛡️ ${r.city_name} held! Attack repelled.</div>`;
    }
    card.innerHTML = `
      <div class="battle-title">${r.attacker_name} <span class="arrow">➜</span> ${r.city_name}
        <small>vs ${r.defender_name}</small></div>
      <div class="bar-row"><span>⚔️ ${r.attack}</span><div class="bar"><i class="atk" style="width:${aPct}%"></i></div></div>
      <div class="bar-row"><span>🛡️ ${r.defense}</span><div class="bar"><i class="def" style="width:${dPct}%"></i></div></div>
      ${outcome}`;
    box.appendChild(card);
  });
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

// real positions of each country on the Earth map (percentages of the map image).
// x/y = where the country is, lx/ly = where its label is placed (fanned out).
const COUNTRY_MAP = {
  croatia: { x: 52.1, y: 32.5, lx: 61,   ly: 31 },
  morocco: { x: 45.0, y: 41.0, lx: 41,   ly: 48 },
  italy:   { x: 51.2, y: 33.6, lx: 58,   ly: 42 },
  japan:   { x: 85.9, y: 32.1, lx: 85.9, ly: 39 },
  denmark: { x: 50.1, y: 25.4, lx: 53,   ly: 15 },
  usa:     { x: 21.7, y: 33.6, lx: 21.7, ly: 41 },
  france:  { x: 48.2, y: 31.1, lx: 36,   ly: 27 },
  england: { x: 47.1, y: 26.7, lx: 35,   ly: 18 },
};

function renderMap(p) {
  const map = $("map");
  map.innerHTML = "";
  const canvas = document.createElement("div");
  canvas.className = "map-canvas";

  // connector lines (svg uses 0..100 coordinates = percentages)
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("class", "map-lines");
  svg.setAttribute("viewBox", "0 0 100 100");
  svg.setAttribute("preserveAspectRatio", "none");
  canvas.appendChild(svg);

  world.countries.forEach((c) => {
    const pos = COUNTRY_MAP[c.id];
    if (!pos) return;
    const owner = Object.values(world.players).find((pl) => pl.country === c.id);
    const color = owner ? owner.color : "#5a6a86";

    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", pos.x); line.setAttribute("y1", pos.y);
    line.setAttribute("x2", pos.lx); line.setAttribute("y2", pos.ly);
    line.setAttribute("stroke", color);
    line.setAttribute("stroke-width", "0.25");
    line.setAttribute("stroke-dasharray", "1.2 0.9");
    svg.appendChild(line);

    const dot = document.createElement("div");
    dot.className = "pin-dot";
    dot.style.left = pos.x + "%";
    dot.style.top = pos.y + "%";
    dot.style.background = color;
    dot.title = c.name;
    canvas.appendChild(dot);

    const cities = Object.values(world.cities).filter((ci) => ci.country === c.id);
    const label = document.createElement("div");
    label.className = "pin-label";
    label.style.left = pos.lx + "%";
    label.style.top = pos.ly + "%";
    label.style.borderColor = color;
    label.innerHTML =
      `<div class="pl-title"><span class="dot" style="background:${color}"></span>${c.flag} ${c.name}</div>
       <div class="pl-cities">${cities
         .map((ci) => {
           const oc = ci.owner ? world.players[ci.owner] : null;
           const cc = oc ? oc.color : "#5a6a86";
           const mine = ci.owner === myId ? " mine" : "";
           return `<span class="ci${mine}" style="border-left-color:${cc}">${ci.name} <small>👥${ci.population}</small></span>`;
         })
         .join("")}</div>`;
    canvas.appendChild(label);
  });

  map.appendChild(canvas);
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
