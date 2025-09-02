let tabs = JSON.parse(localStorage.getItem('notepadTabs')) || [
    { name: 'Tab 1', content: '' },
    { name: 'Tab 2', content: '' },
    { name: 'Tab 3', content: '' }
];
let currentTab = 0;

function saveTabsToStorage() {
    localStorage.setItem('notepadTabs', JSON.stringify(tabs));
}

function renderTabs() {
    const container = document.getElementById('tabContainer');
    container.innerHTML = '';
    tabs.forEach((tab, index) => {
        const tabElement = document.createElement('div');
        tabElement.className = 'tab' + (index === currentTab ? ' active' : '');
        tabElement.innerHTML = `${tab.name} <button onclick="deleteTab(${index}); event.stopPropagation();">&times;</button>`;
        tabElement.onclick = () => switchTab(index);
        container.appendChild(tabElement);
    });
    document.getElementById('noteArea').value = tabs[currentTab]?.content || '';
}

function switchTab(index) {
    saveCurrentContent();
    currentTab = index;
    renderTabs();
}

function saveCurrentContent() {
    if (tabs[currentTab]) {
        tabs[currentTab].content = document.getElementById('noteArea').value;
        saveTabsToStorage();
    }
}

function newTab() {
    saveCurrentContent();
    const name = prompt("Enter new tab name:", `Tab ${tabs.length + 1}`);
    if (name) {
        tabs.push({ name, content: '' });
        currentTab = tabs.length - 1;
        saveTabsToStorage();
        renderTabs();
    }
}

function renameTab() {
    const name = prompt("Enter new tab name:", tabs[currentTab].name);
    if (name) {
        tabs[currentTab].name = name;
        saveTabsToStorage();
        renderTabs();
    }
}

function deleteTab(index) {
    if (confirm(`Delete \"${tabs[index].name}\"?`)) {
        tabs.splice(index, 1);
        if (currentTab >= tabs.length) currentTab = tabs.length - 1;
        saveTabsToStorage();
        renderTabs();
    }
}

function saveToFile() {
    saveCurrentContent();
    let content = tabs.map(tab => `--- ${tab.name} ---\n${tab.content}`).join("\n\n");
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'notepad_tabs.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function copySelectedText() {
    const textarea = document.getElementById('noteArea');
    const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);

    if (!selectedText) {
        alert("Please select some text first.");
        return;
    }

    navigator.clipboard.writeText(selectedText).then(() => {
        alert("Selected text copied to clipboard!");
    }).catch(err => {
        console.error("Could not copy text: ", err);
    });
}

function shareSelectedText() {
    const textarea = document.getElementById('noteArea');
    const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);

    if (!selectedText) {
        alert("Please select some text first.");
        return;
    }

    if (navigator.share) {
        navigator.share({
            title: 'Shared from Multi-Tab Notepad',
            text: selectedText
        }).catch(err => {
            console.error("Error sharing: ", err);
        });
    } else {
        alert("Sharing not supported in this browser. Please copy instead.");
    }
}

function openInputTools() {
    window.open("https://www.google.com/intl/bn/inputtools/try/", "_blank");
}

// 🔹 Emoji Pickers
const popularEmojis = ["😀","😁","😂","🤣","😊","😍","😎","😢","😭","😡","👍","🙏","🔥","🌹","🎉","❤️","💔","⭐","💡","✅"];
function toggleEmojiPicker() {
    const picker = document.getElementById("emojiPicker");
    if (picker.style.display === "none" || picker.style.display === "") {
        picker.innerHTML = "";
        popularEmojis.forEach(emoji => {
            const span = document.createElement("span");
            span.textContent = emoji;
            span.onclick = () => insertEmoji(emoji);
            picker.appendChild(span);
        });
        picker.style.display = "block";
    } else {
        picker.style.display = "none";
    }
}

function insertEmoji(emoji) {
    const textarea = document.getElementById("noteArea");
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    textarea.value = textarea.value.substring(0, start) + emoji + textarea.value.substring(end);
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
    textarea.focus();
    saveCurrentContent();
}

window.addEventListener('beforeunload', saveCurrentContent);
document.getElementById('noteArea').addEventListener('input', saveCurrentContent);

renderTabs();
