const zipSection = document.getElementById("zipSection");
const imageSection = document.getElementById("imageSection");
const statusEl = document.getElementById("status");

function setStatus(msg, isError = false) {
    statusEl.textContent = msg;
    statusEl.style.color = isError ? "#e55353" : "#777";
}

function selectZip() {
    zipSection.classList.remove("hidden");
    imageSection.classList.add("hidden");
    setStatus("");
}

function selectImage() {
    imageSection.classList.remove("hidden");
    zipSection.classList.add("hidden");
    setStatus("");
}

async function uploadZip() {
    const file = document.getElementById("zipFile").files[0];
    if (!file) return setStatus("Please select a ZIP file.", true);

    setStatus("Uploading ZIP...");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/import/zip", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) return setStatus(data.error || "Import failed.", true);

    setStatus("Import successful. Redirecting...");
    window.location.href = `layout_editor.html?template=${data.template_id}`;
}

async function uploadImage() {
    const file = document.getElementById("imageFile").files[0];
    if (!file) return setStatus("Please select an image.", true);

    setStatus("Uploading image...");

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/import/image", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) return setStatus(data.error || "Import failed.", true);

    setStatus("Import successful. Redirecting...");
    window.location.href = `layout_editor.html?template=${data.template_id}`;
}

function goBack() {
    window.location.href = "template_browser.html";
}
