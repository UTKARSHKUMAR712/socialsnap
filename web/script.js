function fetchFormats() {
  const url = document.getElementById("single-url").value.trim();
  if (!url) return alert("⚠️ Please enter a video URL first.");

  setDownloadText("🔍 Detecting formats...");
  window.pywebview.api.get_formats(url).then(response => {
    const result = JSON.parse(response);
    const select = document.getElementById("quality-select");
    select.innerHTML = "";

    if (result.status === "success") {
      result.formats.forEach(format => {
        const option = document.createElement("option");
        option.value = format.id;
        option.textContent = format.label;
        select.appendChild(option);
      });
      if (result.thumbnail) {
        const thumb = document.getElementById("video-thumbnail");
        if (thumb) {
          thumb.src = result.thumbnail;
          thumb.style.display = "block";
        }
      }
      setDownloadText("Download");
    } else {
      alert("❌ Error loading formats: " + result.message);
      setDownloadText("Download");
    }
  });
}

function downloadSelected() {
  const url = document.getElementById("single-url").value.trim();
  const formatId = document.getElementById("quality-select").value;
  if (!url || !formatId) return alert("⚠️ URL and format selection are required.");

  setDownloadText("⏳ Downloading...");
  updateProgressBar(0);
  updateCurrentName("");

  window.pywebview.api.download(url, formatId).then(response => {
    const result = JSON.parse(response);
    setDownloadText("Download");
    if (result.status !== "success") {
      updateCurrentName("❌ Failed");
      alert("❌ Download failed: " + result.message);
    }
  });
}

function setDownloadText(text) {
  document.getElementById("single-text").textContent = text;
}
function updateProgressBar(percent) {
  document.getElementById("progress-bar").style.width = percent + "%";
  document.getElementById("progress-text").textContent = percent + "%";
}
function updateCurrentName(name) {
  document.getElementById("current-name").textContent = name;
}
