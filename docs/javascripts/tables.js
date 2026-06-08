/* Embedded data tables for TCSW research docs.
   Uses PapaParse (CSV) + Grid.js (search/sort/pagination).
   Re-runs on Material instant navigation via document$. */

function tcswParse(url) {
  return new Promise((resolve, reject) => {
    Papa.parse(url, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (res) => resolve(res.data),
      error: reject,
    });
  });
}

function linkCell(text, href) {
  if (!text) return "";
  if (href) return gridjs.html(`<a href="${href}" target="_blank" rel="noopener">${text}</a>`);
  return text;
}

function renderGrid(el, columns, data, limit) {
  el.innerHTML = "";
  new gridjs.Grid({
    columns: columns,
    data: data,
    search: true,
    sort: true,
    resizable: true,
    pagination: { limit: limit || 25, summary: true },
    className: { table: "tcsw-grid-table" },
    language: { search: { placeholder: "Filter…" } },
  }).render(el);
}

async function initSessions(el) {
  const rows = await tcswParse("/data/sessions.csv");
  const data = rows.map((r) => [
    r.year || "",
    r.title || "",
    r.url || "",
    r.track || "",
    (r.speakers || "").replace(/;/g, ", "),
  ]);
  renderGrid(
    el,
    [
      { id: "year", name: "Year", width: "70px" },
      {
        id: "title",
        name: "Session",
        formatter: (cell, row) => linkCell(cell, row.cells[2].data),
      },
      { id: "url", name: "url", hidden: true },
      { id: "track", name: "Track", width: "150px" },
      { id: "speakers", name: "Speakers" },
    ],
    data,
    25
  );
}

async function initDirectory(el) {
  const rows = await tcswParse("/data/organizations.csv");
  const data = rows.map((r) => [
    r.name || "",
    r.website || "",
    r.type || "",
    r.years || "",
    r.notes || "",
  ]);
  renderGrid(
    el,
    [
      {
        id: "name",
        name: "Organization",
        formatter: (cell, row) => linkCell(cell, row.cells[1].data),
      },
      { id: "website", name: "website", hidden: true },
      { id: "type", name: "Role", width: "160px" },
      { id: "years", name: "Years", width: "110px" },
      { id: "notes", name: "Notes" },
    ],
    data,
    20
  );
}

async function initVenues(el) {
  const rows = await tcswParse("/data/organizations.csv");
  const data = rows
    .filter((r) => (r.type || "").toLowerCase().includes("venue"))
    .map((r) => [r.name || "", r.website || "", r.years || "", r.notes || ""]);
  renderGrid(
    el,
    [
      {
        id: "name",
        name: "Venue",
        formatter: (cell, row) => linkCell(cell, row.cells[1].data),
      },
      { id: "website", name: "website", hidden: true },
      { id: "years", name: "Years", width: "120px" },
      { id: "notes", name: "Notes" },
    ],
    data,
    20
  );
}

function tcswInitTables() {
  if (typeof gridjs === "undefined" || typeof Papa === "undefined") return;
  const s = document.getElementById("grid-sessions");
  const d = document.getElementById("grid-directory");
  const v = document.getElementById("grid-venues");
  if (s) initSessions(s);
  if (d) initDirectory(d);
  if (v) initVenues(v);
}

if (typeof document$ !== "undefined") {
  document$.subscribe(tcswInitTables);
} else {
  document.addEventListener("DOMContentLoaded", tcswInitTables);
}
