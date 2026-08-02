const header = document.querySelector("[data-header]");
const menuButton = document.querySelector(".menu-toggle");
const navigation = document.querySelector(".site-nav");
const junctions = [...document.querySelectorAll("[data-junction]")];
const factionButtons = [...document.querySelectorAll("[data-faction]")];
const factionStage = document.querySelector("[data-faction-stage]");

const factions = {
  helix: { label: "Helix Dominion", title: "Own the infrastructure.<br>Own the outcome.", copy: "Build an immaculate machine of taxes, durable constructs, and inevitable control.", color: "#e5a138" },
  neon: { label: "Neon Saints", title: "Move faster than<br>the city can watch.", copy: "Chain shifts, rescue operatives, and turn impossible angles into sudden control.", color: "#ed4ad9" },
  ashen: { label: "Ashen Court", title: "Every contract<br>has a cost.", copy: "Sacrifice the material, recover what was lost, and manifest dangerous bargains in the Veil.", color: "#e8e5df" },
  null: { label: "Null Assembly", title: "Divide. Reconfigure.<br>Become more.", copy: "Build distributed machine minds that adapt their role across both realities.", color: "#63d7f2" },
};

window.addEventListener("scroll", () => header.classList.toggle("fixed", window.scrollY > 100), { passive: true });

menuButton.addEventListener("click", () => {
  const open = navigation.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(open));
});

navigation.addEventListener("click", () => {
  navigation.classList.remove("open");
  menuButton.setAttribute("aria-expanded", "false");
});

junctions.forEach((junction) => {
  junction.querySelector("button").addEventListener("click", () => {
    junctions.forEach((item) => {
      const active = item === junction;
      item.classList.toggle("active", active);
      item.querySelector("button").setAttribute("aria-expanded", String(active));
    });
  });
});

factionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.faction;
    const faction = factions[key];
    factionButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    factionStage.dataset.active = key;
    factionStage.querySelector("[data-faction-label]").textContent = faction.label;
    factionStage.querySelector("[data-faction-title]").innerHTML = faction.title;
    factionStage.querySelector("[data-faction-copy]").textContent = faction.copy;
    factionStage.querySelector("[data-faction-label]").style.color = faction.color;
  });
});
