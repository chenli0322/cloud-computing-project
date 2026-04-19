// Dashboard client — connects to /ws and renders live data.

const hrEl = document.getElementById("hr");
const tempEl = document.getElementById("temp");
const spo2El = document.getElementById("spo2");
const anomCountEl = document.getElementById("anomCount");
const bcCountEl = document.getElementById("bcCount");
const anomBody = document.getElementById("anomBody");
const bcBody = document.getElementById("bcBody");
const peersEl = document.getElementById("peers");
const selfEl = document.getElementById("self");
const masterEl = document.getElementById("master");
const wsstatusEl = document.getElementById("wsstatus");

const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const MAX_POINTS = 60;
const hrSeries = [];

function fitCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  canvas.width = Math.floor(w * dpr);
  canvas.height = Math.floor(h * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
fitCanvas();
window.addEventListener("resize", () => { fitCanvas(); drawChart(); });

function drawChart() {
  const W = canvas.clientWidth;
  const H = canvas.clientHeight;
  ctx.clearRect(0, 0, W, H);

  ctx.strokeStyle = "#2a3448";
  ctx.lineWidth = 1;
  for (let y = 0; y <= 4; y++) {
    const yy = (H / 4) * y;
    ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(W, yy); ctx.stroke();
  }

  if (hrSeries.length < 2) return;
  const min = 40, max = 180;
  ctx.strokeStyle = "#6aa6ff";
  ctx.lineWidth = 2;
  ctx.beginPath();
  hrSeries.forEach((v, i) => {
    const x = (i / (MAX_POINTS - 1)) * W;
    const y = H - ((v - min) / (max - min)) * H;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();

  hrSeries.forEach((v, i) => {
    const x = (i / (MAX_POINTS - 1)) * W;
    const y = H - ((v - min) / (max - min)) * H;
    ctx.fillStyle = v >= 120 || v <= 50 ? "#e85c57" : "#6aa6ff";
    ctx.beginPath(); ctx.arc(x, y, 2, 0, 2 * Math.PI); ctx.fill();
  });
}

function fmtTime(ts) {
  return new Date(ts * 1000).toLocaleTimeString();
}

function shortAddr(h, n = 10) {
  if (!h) return "";
  return h.length > n * 2 ? h.slice(0, n) + "…" + h.slice(-6) : h;
}

let anomCount = 0;
let bcCount = 0;

function handleSensor(msg) {
  const r = msg.payload;
  hrEl.textContent = r.heart_rate.toFixed(1);
  tempEl.textContent = r.body_temp.toFixed(2);
  spo2El.textContent = r.spo2.toFixed(1);
  hrSeries.push(r.heart_rate);
  while (hrSeries.length > MAX_POINTS) hrSeries.shift();
  drawChart();
}

function handleAnomaly(msg) {
  anomCount += 1;
  anomCountEl.textContent = anomCount;
  const r = msg.payload;
  const tr = document.createElement("tr");
  tr.className = "anomaly";
  tr.innerHTML = `
    <td class="mono">${fmtTime(r.ts)}</td>
    <td>${r.device_id}</td>
    <td>${r.heart_rate.toFixed(1)}</td>
    <td>${r.body_temp.toFixed(2)}</td>
    <td>${r.spo2.toFixed(1)}</td>
    <td>${(r.score ?? 0).toFixed(3)}</td>
  `;
  anomBody.prepend(tr);
  while (anomBody.children.length > 25) anomBody.lastChild.remove();
}

function handleBC(msg) {
  bcCount += 1;
  bcCountEl.textContent = bcCount;
  const r = msg.payload;
  const tr = document.createElement("tr");
  const etherscan = `https://sepolia.etherscan.io/tx/${r.tx_hash}`;
  tr.innerHTML = `
    <td class="mono">${fmtTime(r.ts_submitted)}</td>
    <td>${r.anomaly_kind}</td>
    <td>${r.device_id}</td>
    <td>${r.block_number}</td>
    <td><a href="${etherscan}" target="_blank" rel="noreferrer">${shortAddr(r.tx_hash)}</a></td>
  `;
  bcBody.prepend(tr);
  while (bcBody.children.length > 25) bcBody.lastChild.remove();
}

function handlePeers(msg) {
  selfEl.textContent = msg.self;
  masterEl.textContent = msg.master || "(none yet)";
  peersEl.innerHTML = "";
  for (const p of msg.peers) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="role">${p.id}</span><span>${p.host}:${p.port}</span>`;
    peersEl.appendChild(li);
  }
}

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen = () => { wsstatusEl.textContent = "connected"; };
  ws.onclose = () => {
    wsstatusEl.textContent = "disconnected — retrying in 2s";
    setTimeout(connect, 2000);
  };
  ws.onerror = () => { wsstatusEl.textContent = "error"; };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.kind === "sensor") handleSensor(msg);
    else if (msg.kind === "anomaly") handleAnomaly(msg);
    else if (msg.kind === "bc") handleBC(msg);
    else if (msg.kind === "peers") handlePeers(msg);
  };
}
connect();
