// Progressive enhancement only: the site works without JS (sidebar just stays open).
document.documentElement.classList.add("js");

const side = document.getElementById("side");
const menu = document.getElementById("menu");
menu.hidden = false;
menu.addEventListener("click", () => {
  const open = side.classList.toggle("open");
  menu.setAttribute("aria-expanded", String(open));
});

const search = document.getElementById("search");
search.hidden = false;
search.addEventListener("input", () => {
  const q = search.value.trim().toLowerCase();
  side.querySelectorAll("li").forEach((li) => {
    li.hidden = q !== "" && !li.textContent.toLowerCase().includes(q);
  });
  side.querySelectorAll("details").forEach((d) => {
    if (q) d.open = true;
  });
});

document.addEventListener("keydown", (ev) => {
  if (ev.key === "/" && document.activeElement !== search) {
    ev.preventDefault();
    if (!side.classList.contains("open") && getComputedStyle(side).display === "none") menu.click();
    search.focus();
  }
});
