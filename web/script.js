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
  document.getElementById("single-spinner").classList.remove("hidden");

  window.pywebview.api.download(url, formatId).then(response => {
    document.getElementById("single-spinner").classList.add("hidden");
    const result = JSON.parse(response);
    setDownloadText("Download");

    if (result.status === "success") {
      alert("✅ Download complete: " + result.title);
    } else {
      alert("❌ Download failed: " + result.message);
    }
  });
}

function setDownloadText(text) {
  document.getElementById("single-text").textContent = text;
}

 document.getElementById("start-btn").addEventListener("click", () => {
        document.getElementById("Home").scrollIntoView({ behavior: "smooth" });
    });