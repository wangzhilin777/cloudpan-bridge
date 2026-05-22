const { chromium } = require("../.tmp-playwright/node_modules/playwright-core");

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  });
  const page = await browser.newPage();
  const bad = [];
  const logs = [];
  const hits = [];
  page.on("response", (res) => {
    if (res.status() >= 400) bad.push({ status: res.status(), url: res.url() });
  });
  page.on("console", (msg) => logs.push({ type: msg.type(), text: msg.text() }));
  page.on("request", (req) => {
    if (req.url().includes("/api/openlist/login")) hits.push({ method: req.method(), url: req.url() });
  });

  try {
    await page.goto("http://127.0.0.1:18888", { waitUntil: "domcontentloaded", timeout: 15000 });
    const locked = await page.locator("body.auth-locked").count();
    if (locked) {
      await page.evaluate(async () => {
        await fetch("/api/auth/login", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: "admin", password: "Na6177980." }),
        });
      });
      await page.reload({ waitUntil: "domcontentloaded", timeout: 15000 });
    }
    await page.waitForSelector("#ui_language", { timeout: 15000 });
    await page.click('[data-tab="mounts"]');
    await page.waitForTimeout(300);

    await page.selectOption("#openlist_mode", "external_remote");
    await page.waitForTimeout(300);
    const remoteSection = page.locator('[data-openlist-section="external_remote"]');
    await remoteSection.locator('[data-openlist-mirror="openlist_url"]').fill("http://192.168.31.2:5244");
    await remoteSection.locator('[data-openlist-mirror="openlist_username"]').fill("admin");
    await remoteSection.locator('[data-openlist-mirror="openlist_password"]').fill("Na6177980.");
    await page.click("#login-openlist-remote");
    await page.waitForTimeout(5000);
    await page.click('[data-tab="config"]');
    await page.waitForTimeout(300);
    await page.click('#target-quick-picks [data-target-quick="s3"]');
    await page.waitForTimeout(1200);

    const result = await page.evaluate(() => ({
      visibleOpenListSections: Array.from(document.querySelectorAll("[data-openlist-section]"))
        .filter((node) => getComputedStyle(node).display !== "none")
        .map((node) => node.getAttribute("data-openlist-section")),
      runtimeNotice: document.getElementById("runtime-action-notice")?.textContent?.trim() || "",
      targetQuickCount: document.querySelectorAll("#target-quick-picks .quick-pick").length,
      providerQuickCount: document.querySelectorAll("#provider-quick-picks .quick-pick").length,
      activeModeChip: document.getElementById("openlist-mode-chip")?.textContent?.trim() || "",
      visibleTargetSections: Array.from(document.querySelectorAll("[data-target-section]"))
        .filter((node) => getComputedStyle(node).display !== "none")
        .map((node) => node.getAttribute("data-target-section")),
      activeTargetChip: document.getElementById("target-mode-chip")?.textContent?.trim() || "",
      targetPreflight: document.getElementById("target-preflight-notice")?.textContent?.trim() || "",
    }));

    console.log(JSON.stringify({ ok: true, result, hits, bad, logs }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error?.stack || String(error));
  process.exit(1);
});
