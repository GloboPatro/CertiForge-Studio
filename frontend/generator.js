/* ============================================================
   GLOBAL STATE
============================================================ */

let templateId = null;
let templateMeta = null;
let fieldNames = [];
let csvData = [];
let csvHeaders = [];

/* DOM ELEMENTS */
const singleFields = document.getElementById("singleFields");
const previewImage = document.getElementById("previewImage");
const mappingFields = document.getElementById("mappingFields");
const bulkProgress = document.getElementById("bulkProgress");

/* ============================================================
   INITIAL LOAD
============================================================ */

window.onload = () => {
    const params = new URLSearchParams(window.location.search);
    templateId = params.get("template");

    if (!templateId) {
        alert("No template selected");
        return;
    }

    loadTemplateInfo();
};

/* ============================================================
   LOAD TEMPLATE METADATA + FIELDS
============================================================ */

async function loadTemplateInfo() {
    const res = await fetch(`/templates/${templateId}/info`);
    templateMeta = await res.json();

    document.getElementById("templateName").innerText = templateMeta.name;
    document.getElementById("templateSize").innerText =
        `${templateMeta.width} × ${templateMeta.height}`;

    previewImage.src = `/templates/${templateId}/preview?ts=${Date.now()}`;

    // Load layout fields
    const layoutRes = await fetch(`/templates/${templateId}/layout`);
    const layoutData = await layoutRes.json();

    fieldNames = Object.keys(layoutData.layout.fields);

    buildSingleForm();
}

/* ============================================================
   BUILD SINGLE GENERATION FORM
============================================================ */

function buildSingleForm() {
    singleFields.innerHTML = "";

    fieldNames.forEach(name => {
        const label = document.createElement("label");
        label.innerText = name;

        const input = document.createElement("input");
        input.type = "text";
        input.id = "single_" + name;

        singleFields.appendChild(label);
        singleFields.appendChild(input);
    });
}

/* ============================================================
   GENERATE SINGLE CERTIFICATE
============================================================ */

async function generateSingle() {
    const data = {};

    fieldNames.forEach(name => {
        data[name] = document.getElementById("single_" + name).value || "";
    });

    const res = await fetch("/generate/single", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            template_id: templateId,
            data
        })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    window.open(url, "_blank");
}

/* ============================================================
   TAB SWITCHING
============================================================ */

function switchTab(tab) {
    document.getElementById("tabSingle").classList.remove("active");
    document.getElementById("tabBulk").classList.remove("active");
    document.getElementById("singlePanel").classList.remove("active");
    document.getElementById("bulkPanel").classList.remove("active");

    if (tab === "single") {
        document.getElementById("tabSingle").classList.add("active");
        document.getElementById("singlePanel").classList.add("active");
    } else {
        document.getElementById("tabBulk").classList.add("active");
        document.getElementById("bulkPanel").classList.add("active");
    }
}

/* ============================================================
   CSV UPLOAD + PARSE
============================================================ */

document.getElementById("csvFile").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const text = await file.text();
    parseCSV(text);
    buildMappingUI();
});

function parseCSV(text) {
    const rows = text.split("\n").map(r => r.trim()).filter(r => r.length);

    csvHeaders = rows[0].split(",");
    csvData = rows.slice(1).map(row => {
        const values = row.split(",");
        const obj = {};
        csvHeaders.forEach((h, i) => obj[h] = values[i] || "");
        return obj;
    });
}

/* ============================================================
   BUILD FIELD MAPPING UI
============================================================ */

function buildMappingUI() {
    mappingFields.innerHTML = "";

    fieldNames.forEach(name => {
        const label = document.createElement("label");
        label.innerText = name;

        const select = document.createElement("select");
        select.id = "map_" + name;

        const empty = document.createElement("option");
        empty.value = "";
        empty.innerText = "-- ignore --";
        select.appendChild(empty);

        csvHeaders.forEach(h => {
            const opt = document.createElement("option");
            opt.value = h;
            opt.innerText = h;
            select.appendChild(opt);
        });

        mappingFields.appendChild(label);
        mappingFields.appendChild(select);
    });
}

/* ============================================================
   BULK GENERATION
============================================================ */

async function generateBulk() {
    if (csvData.length === 0) {
        alert("Upload a CSV first");
        return;
    }

    bulkProgress.innerText = "Generating...";

    const mapping = {};
    fieldNames.forEach(name => {
        mapping[name] = document.getElementById("map_" + name).value;
    });

    const res = await fetch("/generate/bulk", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            template_id: templateId,
            mapping,
            rows: csvData
        })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    bulkProgress.innerText = "Done! Downloading ZIP...";

    const a = document.createElement("a");
    a.href = url;
    a.download = "certificates.zip";
    a.click();

    bulkProgress.innerText = "Completed.";
}

/* ============================================================
   NAVIGATION
============================================================ */

function goBack() {
    window.location.href = "template_browser.html";
}
