const API_URL = window.EKC_API_URL ||
     (location.hostname.endsWith(".app.github.dev")
       ? location.origin.replace(/-\d+\./, "-8000.")
       : "http://127.0.0.1:8000");   // change when deployed
const THINK_DELAY_MS = 300;            // short pause before typing starts
const TYPING_SOUND_URL = "";           // optional LOCAL file, e.g. "typing.mp3" ("" = no sound)
const MAX_LEN = 500;                   // must match the backend limit

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const typingAudio = TYPING_SOUND_URL ? new Audio(TYPING_SOUND_URL) : null;
if (typingAudio) typingAudio.volume = 0.15;
chatBox.setAttribute("aria-live", "polite");   // screen readers announce new replies
let busy = false;

/* ---------- messages ---------- */
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = type === "user" ? "user-message" : "bot-message";
  div.innerText = text;                         // innerText (not innerHTML) = XSS-safe
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

function addCursor(element) {
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  cursor.innerText = "▋";
  element.appendChild(cursor);
  return cursor;
}

/* ---------- typewriter (total typing time capped at ~3 s) ---------- */
function typeWriterEffect(text, element, onDone) {
  element.innerText = "";
  const speed = Math.max(2, Math.min(15, 3000 / text.length));
  let i = 0;
  const cursor = addCursor(element);

  function type() {
    if (i < text.length) {
      element.insertBefore(document.createTextNode(text.charAt(i)), cursor);
      if (typingAudio) { typingAudio.currentTime = 0; typingAudio.play().catch(() => {}); }
      i++;
      chatBox.scrollTop = chatBox.scrollHeight;
      setTimeout(type, speed);
    } else {
      cursor.remove();
      if (onDone) onDone();
    }
  }
  setTimeout(type, THINK_DELAY_MS);
}

/* ---------- feedback buttons ---------- */
function addFeedback(botDiv, logId) {
  if (!logId) return;
  const box = document.createElement("div");
  box.className = "feedback";

  function send(helpful) {
    fetch(`${API_URL}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ log_id: logId, helpful })
    }).catch(() => {});
    box.innerText = "Thanks for your feedback!";
  }

  [["👍", true, "Helpful"], ["👎", false, "Not helpful"]].forEach(([icon, value, label]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.innerText = icon;
    b.setAttribute("aria-label", label);
    b.onclick = () => send(value);
    box.appendChild(b);
  });
  botDiv.appendChild(box);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* ---------- send ---------- */
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg || busy) return;
  if (msg.length > MAX_LEN) {
    addMessage(`Please keep your question under ${MAX_LEN} characters.`, "bot");
    return;
  }

  busy = true;
  addMessage(msg, "user");
  input.value = "";
  const typingDiv = addMessage("EKC Bot is typing...", "bot");

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();

    typingDiv.remove();
    const botDiv = document.createElement("div");
    botDiv.className = "bot-message";
    chatBox.appendChild(botDiv);
    typeWriterEffect(data.response, botDiv, () => {
      addFeedback(botDiv, data.log_id);
      busy = false;
    });
  } catch (err) {
    typingDiv.remove();
    addMessage("Sorry, I can't reach the server right now. Please try again in a moment.", "bot");
    busy = false;
  }
}

function quickAsk(text) {
  input.value = text;
  sendMessage();
}

input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

/* ---------- speech recognition ---------- */
function startSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    addMessage("Speech recognition is not supported in this browser.", "bot");
    return;
  }
  const mic = document.getElementById("mic-btn");
  const rec = new SR();
  rec.lang = "en-IN";
  rec.onstart = () => { mic.style.background = "#c62828"; };
  rec.onend = () => { mic.style.background = "#2e7d32"; };
  rec.onerror = () => addMessage("Sorry, I couldn't hear that. Please try again.", "bot");
  rec.onresult = e => {
    input.value = e.results[0][0].transcript;
    sendMessage();
  };
  rec.start();
}

/* ---------- theme (remembered; follows system setting the first time) ---------- */
function applyTheme(dark) {
  document.body.classList.toggle("dark-mode", dark);
  const btn = document.getElementById("theme-toggle");
  if (btn) btn.innerText = dark ? "☀️" : "🌙";
}

function toggleTheme() {
  const dark = !document.body.classList.contains("dark-mode");
  applyTheme(dark);
  try { localStorage.setItem("ekc-theme", dark ? "dark" : "light"); } catch (e) {}
}

(function initTheme() {
  let saved = null;
  try { saved = localStorage.getItem("ekc-theme"); } catch (e) {}
  const dark = saved ? saved === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(dark);
})();
