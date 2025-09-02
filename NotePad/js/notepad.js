// ---------------- Tab Management ----------------
let currentTab = null;
let notesData = JSON.parse(localStorage.getItem("notesData")) || {};
let tabCounter = Object.keys(notesData).length || 1;

function renderTabs() {
  const tabContainer = document.getElementById("tabContainer");
  tabContainer.innerHTML = "";

  Object.keys(notesData).forEach(tabId => {
    const tab = document.createElement("div");
    tab.className = "tab" + (tabId === currentTab ? " active" : "");
    tab.innerHTML = `${notesData[tabId].title} 
      <button onclick="closeTab('${tabId}')">x</button>`;
    tab.onclick = () => switchTab(tabId);
    tabContainer.appendChild(tab);
  });
}

function switchTab(tabId) {
  currentTab = tabId;
  document.getElementById("noteArea").value = notesData[tabId].content;
  renderTabs();
  saveNotes();
}

function newTab() {
  const tabId = "tab" + tabCounter++;
  notesData[tabId] = { title: "Untitled", content: "" };
  switchTab(tabId);
}

function renameTab() {
  if (!currentTab) return;
  const newName = prompt("Enter new tab name:", notesData[currentTab].title);
  if (newName) {
    notesData[currentTab].title = newName;
    renderTabs();
    saveNotes();
  }
}

function closeTab(tabId) {
  delete notesData[tabId];
  if (currentTab === tabId) {
    const remainingTabs = Object.keys(notesData);
    currentTab = remainingTabs.length ? remainingTabs[0] : null;
    document.getElementById("noteArea").value = currentTab ? notesData[currentTab].content : "";
  }
  renderTabs();
  saveNotes();
}

// ---------------- Save & Load ----------------
function saveNotes() {
  localStorage.setItem("notesData", JSON.stringify(notesData));
}

document.getElementById("noteArea").addEventListener("input", () => {
  if (currentTab) {
    notesData[currentTab].content = document.getElementById("noteArea").value;
    saveNotes();
  }
});

function saveToFile() {
  if (!currentTab) return alert("No tab selected.");
  const blob = new Blob([notesData[currentTab].content], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = notesData[currentTab].title + ".txt";
  link.click();
}

// ---------------- Share ----------------
function shareSelectedText() {
  const textarea = document.getElementById("noteArea");
  const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
  if (!selectedText) return alert("Please select some text to share!");

  if (navigator.share) {
    navigator.share({ text: selectedText })
      .catch(err => console.log("Share failed:", err));
  } else {
    alert("Sharing not supported in this browser.");
  }
}

// ---------------- Emoji Picker ----------------
function toggleEmojiPicker() {
  const picker = document.getElementById("emojiPicker");
  picker.style.display = picker.style.display === "none" || picker.style.display === "" ? "block" : "none";

  if (picker.innerHTML === "") {
    const emojis = ["😀","😂","😍","🙏","🎉","😢","😡","👍","👎","❤️","🔥","🌟","✨","🎶","📚","✍️","🚀"];
    emojis.forEach(e => {
      const span = document.createElement("span");
      span.textContent = e;
      span.onclick = () => insertEmoji(e);
      picker.appendChild(span);
    });
  }
}

function insertEmoji(emoji) {
  const textarea = document.getElementById("noteArea");
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  textarea.value = textarea.value.slice(0, start) + emoji + textarea.value.slice(end);
  textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
  textarea.focus();

  if (currentTab) {
    notesData[currentTab].content = textarea.value;
    saveNotes();
  }
}

// ---------------- Initialization ----------------
window.onload = function () {
  if (Object.keys(notesData).length === 0) {
    newTab();
  } else {
    currentTab = Object.keys(notesData)[0];
    document.getElementById("noteArea").value = notesData[currentTab].content;
    renderTabs();
  }
};
