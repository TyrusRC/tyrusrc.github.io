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

// Terminal intro: type each "$ cmd" prompt in turn, fading in its output once typed.
const prompts = [...document.querySelectorAll("main > .prompt")];
const outputs = prompts.map((p) => {
  const els = [];
  for (let n = p.nextElementSibling; n && !n.classList.contains("prompt"); n = n.nextElementSibling) els.push(n);
  return els;
});
const cursor = () => {
  if (!prompts.length) return;
  const p = document.createElement("p");
  p.className = "prompt";
  const c = document.createElement("span");
  c.className = "cursor";
  c.setAttribute("aria-hidden", "true");
  p.append("$ ", c);
  document.querySelector("main").append(p);
};
const reveal = (els) => els.forEach((el) => el.classList.replace("pending", "revealed"));

if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
  cursor();
} else {
  prompts.forEach((p, i) => {
    const cmd = p.textContent.replace(/^\$\s*/, "");
    const span = document.createElement("span");
    span.textContent = cmd;
    span.style.setProperty("--n", cmd.length);
    p.replaceChildren("$ ", span);
    if (i) p.classList.add("pending");
    outputs[i].forEach((el) => el.classList.add("pending"));
  });
  // Timers, not animationend: if the CSS animation never runs, content must still appear.
  const run = (i) => {
    if (i === prompts.length) return cursor();
    const span = prompts[i].lastChild;
    reveal([prompts[i]]);
    span.classList.add("typing");
    setTimeout(() => {
      reveal(outputs[i]);
      setTimeout(() => run(i + 1), 300);
    }, span.textContent.length * 55 + 50);
  };
  setTimeout(() => run(0), 300);
}

document.addEventListener("keydown", (ev) => {
  if (ev.key === "/" && document.activeElement !== search) {
    ev.preventDefault();
    if (!side.classList.contains("open") && getComputedStyle(side).display === "none") menu.click();
    search.focus();
  }
});
