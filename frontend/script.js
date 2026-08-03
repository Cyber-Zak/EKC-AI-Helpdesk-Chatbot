const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");

/* ================================
   ADD MESSAGE FUNCTION
================================ */
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = type === "user" ? "user-message" : "bot-message";
  div.innerText = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* ================================
   TYPING SOUND
================================ */
const typingAudio = new Audio("https://www.soundjay.com/mechanical/keyboard-1.mp3");
typingAudio.volume = 0.15;

/* ================================
   BLINKING CURSOR
================================ */
function addCursor(element) {
  const cursor = document.createElement("span");
  cursor.className = "cursor";
  cursor.innerText = "▋";
  element.appendChild(cursor);
  return cursor;
}

/* ================================
   PREMIUM TYPEWRITER EFFECT
================================ */
function typeWriterEffect(text, element) {

  element.innerText = "";

  // Dynamic typing speed
  let speed = text.length < 60 ? 8 : 15;

  let i = 0;

  const cursor = addCursor(element);

  function type() {
    if (i < text.length) {

      element.insertBefore(
        document.createTextNode(text.charAt(i)),
        cursor
      );

      // Play typing sound
      typingAudio.currentTime = 0;
      typingAudio.play().catch(() => {});

      i++;
      setTimeout(type, speed);

    } else {
      cursor.remove(); // Remove cursor when done
    }
  }

  // Slight thinking pause
  setTimeout(type, 600);
}

/* ================================
   SEND MESSAGE FUNCTION
================================ */
function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  input.value = "";

  // Show typing indicator
  const typingDiv = document.createElement("div");
  typingDiv.className = "bot-message";
  typingDiv.innerText = "EKC Bot is typing...";
  chatBox.appendChild(typingDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  })
  .then(res => res.json())
  .then(data => {

    // Realistic delay (800–1200ms)
    const delay = Math.floor(Math.random() * 400) + 800;

    setTimeout(() => {

      // Remove typing indicator
      chatBox.removeChild(typingDiv);

      // Create empty bot message
      const botDiv = document.createElement("div");
      botDiv.className = "bot-message";
      chatBox.appendChild(botDiv);

      // Animate response
      typeWriterEffect(data.response, botDiv);

      chatBox.scrollTop = chatBox.scrollHeight;

    }, delay);
  });
}

/* ================================
   QUICK CHIP FUNCTION
================================ */
function quickAsk(text) {
  input.value = text;
  sendMessage();
}

/* ================================
   ENTER KEY SUPPORT
================================ */
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

/* ================================
   SPEECH RECOGNITION
================================ */
function startSpeech() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Speech recognition not supported in this browser.");
    return;
  }

  const rec = new SpeechRecognition();
  rec.lang = "en-IN";

  rec.onstart = () => {
    document.getElementById("mic-btn").style.background = "#c62828";
  };

  rec.onend = () => {
    document.getElementById("mic-btn").style.background = "#2e7d32";
  };

  rec.onresult = e => {
    input.value = e.results[0][0].transcript;
    sendMessage();
  };

  rec.start();
}
function toggleTheme() {
  document.body.classList.toggle("dark-mode");

  const btn = document.getElementById("theme-toggle");

  if (document.body.classList.contains("dark-mode")) {
    btn.innerText = "☀️";
  } else {
    btn.innerText = "🌙";
  }
}