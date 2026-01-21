console.log("Editor booting...");

// ===============================
// STATE
// ===============================
let currentTemplate = null;
let layout = {}; 
let selectedField = null;

const canvasWrapper = document.getElementById("canvasWrapper");
const canvasInner = document.getElementById("canvasInner");
const canvas = document.getElementById("canvas");
const fieldList = document.getElementById("fieldList");

let zoomLevel = 1;
let snapEnabled = false;

// ===============================
// UI WIRING
// ===============================
document.getElementById("btnAddField").onclick = addNewField;
document.getElementById("btnDuplicateField").onclick = duplicateField;
document.getElementById("btnDeleteField").onclick = deleteField;
document.getElementById("btnZoomIn").onclick = () => setZoom(zoomLevel + 0.1);
document.getElementById("btnZoomOut").onclick = () => setZoom(Math.max(0.2, zoomLevel - 0.1));
document.getElementById("btnZoomReset").onclick = () => setZoom(1);
document.getElementById("btnSnap").onclick = () => { snapEnabled = !snapEnabled; updateSnapUI(); };
document.getElementById("btnGenerate").onclick = generatePreview;
document.getElementById("btnApplyProps").onclick = applyFieldProps;
document.querySelectorAll(".closeModal").forEach(b => b.onclick = () => b.closest(".modal").classList.add("hidden"));
document.getElementById("themeToggle").onclick = toggleTheme;

document.getElementById("btnLoadTemplate").onclick = () => {
  const id = prompt("Enter template ID:");
  if (id) loadTemplateFromServer(id.trim());
};

// ===============================
// THEME
// ===============================
function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute("data-theme") === "light";
  html.setAttribute("data-theme", isLight ? "dark" : "light");
}

// ===============================
// ZOOM
// ===============================
function setZoom(level) {
  zoomLevel = Math.round(level * 100) / 100;
  canvasInner.style.transform = `scale(${zoomLevel})`;
  document.getElementById("btnZoomReset").innerText = Math.round(zoomLevel * 100) + "%";
}

// ===============================
// COORDINATE CONVERSION
// ===============================
function screenToCanvas(clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (clientX - rect.left) / zoomLevel,
    y: (clientY - rect.top) / zoomLevel
  };
}

// ===============================
// LOAD TEMPLATE (SERVER)
// ===============================
async function loadTemplateFromServer(id) {
  currentTemplate = id;
  layout = {};
  selectedField = null;
  canvas.innerHTML = "";

  const img = new Image();
  img.src = `/templates/${encodeURIComponent(id)}/preview?ts=${Date.now()}`;

  try {
    await img.decode();
  } catch (e) {
    alert("Failed to load template image");
    return;
  }

  canvas.style.width = img.width + "px";
  canvas.style.height = img.height + "px";
  canvas.style.backgroundImage = `url(${img.src})`;

  canvasInner.style.width = canvas.style.width;
  canvasInner.style.height = canvas.style.height;

  try {
    const res = await fetch(`/templates/${encodeURIComponent(id)}/layout?ts=${Date.now()}`);
    const data = await res.json();
    layout = data.layout?.fields || {};
  } catch (e) {
    layout = {};
  }

  canvas.innerHTML = "";
  for (const name in layout) {
    createFieldBox(name, layout[name]);
  }

  refreshFieldList();
}

// ===============================
// LOCAL BLANK TEMPLATE (INIT)
// ===============================
async function loadTemplate(id, imageUrl) {
  currentTemplate = id || "local";
  layout = {};
  selectedField = null;
  canvas.innerHTML = "";

  if (!imageUrl) {
    canvas.style.width = "1200px";
    canvas.style.height = "850px";
    canvas.style.backgroundImage = "";
    canvas.style.backgroundColor = "#fff";
  } else {
    const img = new Image();
    img.src = imageUrl + "?ts=" + Date.now();
    try { await img.decode(); } catch(e){ console.warn("image decode failed", e); }
    canvas.style.width = img.width + "px";
    canvas.style.height = img.height + "px";
    canvas.style.backgroundImage = `url(${img.src})`;
    canvas.style.backgroundColor = "";
  }

  canvasInner.style.width = canvas.style.width;
  canvasInner.style.height = canvas.style.height;

  refreshFieldList();
}

// ===============================
// ADD FIELD
// ===============================
function addNewField() {
  const name = prompt("Field name:");
  if (!name) return;

  const rect = canvasWrapper.getBoundingClientRect();
  const cx = rect.left + canvasWrapper.clientWidth / 2;
  const cy = rect.top + canvasWrapper.clientHeight / 2;

  const pos = screenToCanvas(cx, cy);

  layout[name] = {
    x: pos.x - 100,
    y: pos.y - 30,
    w: 200,
    h: 60,
    size: 32,
    color: "#000000"
  };

  createFieldBox(name, layout[name]);
  refreshFieldList();
  selectField(name);
}

// ===============================
// CREATE FIELD BOX
// ===============================
function createFieldBox(name, props) {
  const box = document.createElement("div");
  box.className = "fieldBox";
  box.dataset.name = name;

  const label = document.createElement("div");
  label.className = "fieldLabel";
  label.innerText = name;
  box.appendChild(label);

  const handle = document.createElement("div");
  handle.className = "resize-handle";
  box.appendChild(handle);

  enableDrag(box);
  enableResize(box);

  canvas.appendChild(box);
  updateFieldBox(name);
}

// ===============================
// UPDATE FIELD BOX
// ===============================
function updateFieldBox(name) {
  const props = layout[name];
  const box = canvas.querySelector(`.fieldBox[data-name="${name}"]`);
  if (!box) return;

  box.style.left = props.x + "px";
  box.style.top = props.y + "px";
  box.style.width = props.w + "px";
  box.style.height = props.h + "px";

  const label = box.querySelector(".fieldLabel");
  if (label) {
    label.style.fontSize = props.size + "px";
    label.style.color = props.color;
  }
}

// ===============================
// FIELD LIST
// ===============================
function refreshFieldList() {
  fieldList.innerHTML = "";
  for (const name in layout) {
    const item = document.createElement("div");
    item.className = "fieldListItem";
    item.innerText = name;
    item.onclick = () => selectField(name);
    if (name === selectedField) item.style.background = "rgba(0,0,0,0.1)";
    fieldList.appendChild(item);
  }
}

function selectField(name) {
  selectedField = name;
  refreshFieldList();

  const p = layout[name];
  if (!p) return;

  document.getElementById("propName").value = name;
  document.getElementById("propX").value = Math.round(p.x);
  document.getElementById("propY").value = Math.round(p.y);
  document.getElementById("propW").value = Math.round(p.w);
  document.getElementById("propH").value = Math.round(p.h);
  document.getElementById("propSize").value = Math.round(p.size);
  document.getElementById("propColor").value = p.color;
}

// ===============================
// APPLY PROPERTIES (RENAMING FIXED)
// ===============================
function applyFieldProps() {
  if (!selectedField) return;

  const old = selectedField;
  const newName = document.getElementById("propName").value.trim() || old;
  const p = layout[old];

  p.x = parseInt(document.getElementById("propX").value) || 0;
  p.y = parseInt(document.getElementById("propY").value) || 0;
  p.w = parseInt(document.getElementById("propW").value) || 0;
  p.h = parseInt(document.getElementById("propH").value) || 0;
  p.size = parseInt(document.getElementById("propSize").value) || 12;
  p.color = document.getElementById("propColor").value || "#000000";

  if (newName !== old) {
    layout[newName] = p;
    delete layout[old];

    const box = canvas.querySelector(`.fieldBox[data-name="${old}"]`);
    if (box) {
      box.dataset.name = newName;
      const label = box.querySelector(".fieldLabel");
      if (label) label.innerText = newName;
    }

    selectedField = newName;
  }

  updateFieldBox(selectedField);
  refreshFieldList();
}

// ===============================
// LIVE PROPERTY UPDATES (FIXED MAPPING)
// ===============================
const propMap = {
  propX: "x",
  propY: "y",
  propW: "w",
  propH: "h",
  propSize: "size",
  propColor: "color"
};

for (const id in propMap) {
  const el = document.getElementById(id);
  const key = propMap[id];

  el.addEventListener("input", () => {
    if (!selectedField) return;
    const p = layout[selectedField];

    if (key === "color") {
      p.color = el.value;
    } else {
      p[key] = parseInt(el.value) || 0;
    }

    updateFieldBox(selectedField);
  });
}

// ===============================
// DUPLICATE / DELETE
// ===============================
function duplicateField() {
  if (!selectedField) return;

  const original = layout[selectedField];
  let base = selectedField + "_copy";
  let i = 1;
  while (layout[base]) {
    base = selectedField + "_copy" + i;
    i++;
  }

  layout[base] = { ...original, x: original.x + 20, y: original.y + 20 };
  createFieldBox(base, layout[base]);
  refreshFieldList();
  selectField(base);
}

function deleteField() {
  if (!selectedField) return;

  delete layout[selectedField];
  const box = canvas.querySelector(`.fieldBox[data-name="${selectedField}"]`);
  if (box) box.remove();

  selectedField = null;
  refreshFieldList();
}

// ===============================
// DRAGGING
// ===============================
function enableDrag(el) {
  let dragging = false;
  let start = null;
  let name = null;

  el.addEventListener("pointerdown", e => {
    if (e.target.classList.contains("resize-handle")) return;
    e.preventDefault();
    el.setPointerCapture(e.pointerId);

    dragging = true;
    name = el.dataset.name;
    selectField(name);

    const p = layout[name];
    start = { x: p.x, y: p.y, cx: e.clientX, cy: e.clientY };
  });

  el.addEventListener("pointermove", e => {
    if (!dragging || !start) return;

    const dx = (e.clientX - start.cx) / zoomLevel;
    const dy = (e.clientY - start.cy) / zoomLevel;

    let nx = start.x + dx;
    let ny = start.y + dy;

    if (snapEnabled) {
      nx = Math.round(nx / 10) * 10;
      ny = Math.round(ny / 10) * 10;
    }

    layout[name].x = nx;
    layout[name].y = ny;

    updateFieldBox(name);
  });

  el.addEventListener("pointerup", e => {
    dragging = false;
    el.releasePointerCapture(e.pointerId);
  });
}

// ===============================
// RESIZING
// ===============================
function enableResize(el) {
  const handle = el.querySelector(".resize-handle");
  if (!handle) return;

  let resizing = false;
  let start = null;
  let name = null;

  handle.addEventListener("pointerdown", e => {
    e.stopPropagation();
    e.preventDefault();
    handle.setPointerCapture(e.pointerId);

    resizing = true;
    name = el.dataset.name;

    const p = layout[name];
    start = { w: p.w, h: p.h, cx: e.clientX, cy: e.clientY };
  });

  handle.addEventListener("pointermove", e => {
    if (!resizing || !start) return;

    const dx = (e.clientX - start.cx) / zoomLevel;
    const dy = (e.clientY - start.cy) / zoomLevel;

    let nw = Math.max(20, start.w + dx);
    let nh = Math.max(20, start.h + dy);

    if (snapEnabled) {
      nw = Math.round(nw / 10) * 10;
      nh = Math.round(nh / 10) * 10;
    }

    layout[name].w = nw;
    layout[name].h = nh;

    updateFieldBox(name);
  });

  handle.addEventListener("pointerup", e => {
    resizing = false;
    handle.releasePointerCapture(e.pointerId);
  });
}

// ===============================
// SNAP UI
// ===============================
function updateSnapUI() {
  const btn = document.getElementById("btnSnap");
  btn.style.background = snapEnabled ? "#e6f0ff" : "";
  canvas.classList.toggle("snap-grid", snapEnabled);
}

// ===============================
// Generate Preview UI
// ===============================
function generatePreview() {
  const modal = document.getElementById("previewModal");
  const imgEl = document.getElementById("previewImage");

  // Hide editor UI
  setEditorVisuals(false);

  const clone = canvasInner.cloneNode(true);
  clone.style.transform = "scale(1)";
  clone.style.position = "absolute";
  clone.style.left = "0";
  clone.style.top = "0";

  const temp = document.createElement("div");
  temp.style.position = "fixed";
  temp.style.left = "-9999px";
  temp.style.top = "0";
  temp.appendChild(clone);
  document.body.appendChild(temp);

  html2canvas(clone, { backgroundColor: null }).then(canvasOutput => {
    imgEl.src = canvasOutput.toDataURL("image/png");
    modal.classList.remove("hidden");

    // Restore editor UI
    setEditorVisuals(true);

    document.body.removeChild(temp);
  });

  document.getElementById("btnDownload").onclick = () => {
    const img = document.getElementById("previewImage").src;

    const a = document.createElement("a");
    a.href = img;
    a.download = "certificate.png";
    a.click();
};

  document.getElementById("btnDownloadPDF").onclick = () => {
    const img = document.getElementById("previewImage").src;

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({
        orientation: "landscape",
        unit: "px",
        format: "a4"
    });

    const width = pdf.internal.pageSize.getWidth();
    const height = pdf.internal.pageSize.getHeight();

    pdf.addImage(img, "PNG", 0, 0, width, height);
    pdf.save("certificate.pdf");
};

  document.getElementById("btnSaveLayout").onclick = () => {
    const data = {
        template: currentTemplate,
        fields: layout
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "layout.json";
    a.click();
};


}

  // Shows final resutls in preview
function setEditorVisuals(enabled) {
  const boxes = document.querySelectorAll(".fieldBox");
  boxes.forEach(b => {
    b.style.border = enabled ? "1px dashed var(--accent)" : "none";
    b.style.background = enabled ? "rgba(0,0,0,0.04)" : "transparent";
  });

  const handles = document.querySelectorAll(".resize-handle");
  handles.forEach(h => h.style.display = enabled ? "block" : "none");

  if (!enabled) {
    canvas.classList.remove("snap-grid");
  } else if (snapEnabled) {
    canvas.classList.add("snap-grid");
  }
}


// ===============================
// INIT
// ===============================
loadTemplate("blank");
console.log("Editor ready");
