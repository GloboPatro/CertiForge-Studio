/* ============================================================
   GLOBAL STATE
============================================================ */

let templates = [];
let selectedTemplate = null;

/* DOM ELEMENTS */
const grid = document.getElementById("grid");
const searchInput = document.getElementById("searchInput");
const detailsPanel = document.getElementById("detailsPanel");

const detailsName = document.getElementById("detailsName");
const detailsPreview = document.getElementById("detailsPreview");
const metaId = document.getElementById("metaId");
const metaSize = document.getElementById("metaSize");
const metaFields = document.getElementById("metaFields");
const metaCreated = document.getElementById("metaCreated");

/* ============================================================
   INITIAL LOAD
============================================================ */

window.onload = () => {
    loadTemplates();
    searchInput.addEventListener("input", filterTemplates);
};

/* ============================================================
   LOAD TEMPLATES FROM BACKEND
============================================================ */

async function loadTemplates() {
    const res = await fetch("/templates");
    const data = await res.json();
    templates = data.templates;

    renderGrid(templates);
}

/* ============================================================
   RENDER GRID
============================================================ */

function renderGrid(list) {
    grid.innerHTML = "";

    list.forEach(tpl => {
        const card = document.createElement("div");
        card.className = "templateCard";
        card.onclick = () => openDetails(tpl);

        const thumb = document.createElement("div");
        thumb.className = "templateThumb";
        thumb.style.backgroundImage = `url(/templates/${tpl.id}/thumb?ts=${Date.now()})`;

        const info = document.createElement("div");
        info.className = "templateInfo";

        const name = document.createElement("div");
        name.className = "templateName";
        name.innerText = tpl.name;

        const meta = document.createElement("div");
        meta.className = "templateMeta";
        meta.innerText = `${tpl.width}×${tpl.height} px`;

        info.appendChild(name);
        info.appendChild(meta);

        card.appendChild(thumb);
        card.appendChild(info);

        grid.appendChild(card);
    });
}

/* ============================================================
   SEARCH FILTER
============================================================ */

function filterTemplates() {
    const q = searchInput.value.toLowerCase();

    const filtered = templates.filter(t =>
        t.name.toLowerCase().includes(q) ||
        t.id.toLowerCase().includes(q)
    );

    renderGrid(filtered);
}

/* ============================================================
   OPEN DETAILS PANEL
============================================================ */

function openDetails(tpl) {
    selectedTemplate = tpl;

    detailsName.innerText = tpl.name;
    detailsPreview.src = `/templates/${tpl.id}/preview?ts=${Date.now()}`;

    metaId.innerText = tpl.id;
    metaSize.innerText = `${tpl.width} × ${tpl.height}`;
    metaFields.innerText = tpl.fields || "Unknown";
    metaCreated.innerText = tpl.created || "Unknown";

    detailsPanel.classList.remove("hidden");
}

/* ============================================================
   CLOSE DETAILS PANEL
============================================================ */

function closeDetails() {
    detailsPanel.classList.add("hidden");
    selectedTemplate = null;
}

/* ============================================================
   ACTIONS
============================================================ */

function openEditor() {
    if (!selectedTemplate) return;
    window.location.href = `layout_editor.html?template=${selectedTemplate.id}`;
}

function openGenerator() {
    if (!selectedTemplate) return;
    window.location.href = `generator.html?template=${selectedTemplate.id}`;
}

async function duplicateTemplate() {
    if (!selectedTemplate) return;

    const res = await fetch(`/templates/${selectedTemplate.id}/duplicate`, {
        method: "POST"
    });

    if (res.ok) {
        alert("Template duplicated");
        loadTemplates();
    }
}

async function deleteTemplate() {
    if (!selectedTemplate) return;

    if (!confirm("Delete this template?")) return;

    const res = await fetch(`/templates/${selectedTemplate.id}`, {
        method: "DELETE"
    });

    if (res.ok) {
        alert("Template deleted");
        closeDetails();
        loadTemplates();
    }
}

/* ============================================================
   IMPORT TEMPLATE
============================================================ */

function openImporter() {
    window.location.href = "importer.html";
}
