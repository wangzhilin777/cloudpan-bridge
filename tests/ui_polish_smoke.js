const { chromium } = require("../.tmp-playwright/node_modules/playwright-core");

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  });
  const page = await browser.newPage();
  const report = {};

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
    report.langBefore = await page.locator("#ui_language").inputValue();
    await page.selectOption("#ui_language", "mix");
    await page.waitForTimeout(600);
    report.modeChipMix = await page.locator("#openlist-mode-chip").textContent();

    await page.selectOption("#openlist_mode", "managed_binary");
    await page.waitForTimeout(500);
    report.visibleManaged = await page.locator("[data-openlist-section]").evaluateAll((nodes) =>
      nodes.filter((n) => getComputedStyle(n).display !== "none").map((n) => n.getAttribute("data-openlist-section"))
    );
    report.runtimeNoticeManaged = await page.locator("#runtime-action-notice").textContent();

    await page.selectOption("#openlist_mode", "external_remote");
    await page.waitForTimeout(500);
    report.visibleRemote = await page.locator("[data-openlist-section]").evaluateAll((nodes) =>
      nodes.filter((n) => getComputedStyle(n).display !== "none").map((n) => n.getAttribute("data-openlist-section"))
    );

    await page.click('[data-tab="config"]');
    await page.waitForTimeout(300);
    const targets = ["guangya", "openlist", "localfs", "webdav", "s3"];
    report.targets = {};
    for (const key of targets) {
      await page.click(`#target-quick-picks [data-target-quick="${key}"]`);
      await page.waitForTimeout(900);
      report.targets[key] = await page.evaluate(() => ({
        visible: Array.from(document.querySelectorAll("[data-target-section]"))
          .filter((n) => getComputedStyle(n).display !== "none")
          .map((n) => n.getAttribute("data-target-section")),
        chip: document.getElementById("target-mode-chip")?.textContent?.trim() || "",
        preflight: document.getElementById("target-preflight-notice")?.textContent?.trim() || "",
      }));
    }

    await page.click('#target-quick-picks [data-target-quick="openlist"]');
    await page.waitForTimeout(900);
    report.openlistTargetMounts = await page.evaluate(() => ({
      targetTabCount: document.querySelectorAll("#openlist_target_mount_select option").length,
      targetTabFirst: document.querySelector("#openlist_target_mount_select option")?.value || "",
    }));

    await page.click('[data-tab="task"]');
    await page.waitForTimeout(400);
    report.openlistTaskMounts = await page.evaluate(() => ({
      visible: !!document.getElementById("openlist_target_mount_select_task")
        && getComputedStyle(document.getElementById("openlist_target_mount_select_task")).display !== "none",
      taskTabCount: document.querySelectorAll("#openlist_target_mount_select_task option").length,
      taskTabFirst: document.querySelector("#openlist_target_mount_select_task option")?.value || "",
    }));

    await page.click('[data-tab="mounts"]');
    await page.waitForTimeout(300);
    report.providerQuicks = await page.locator("#provider-quick-picks .quick-pick strong").evaluateAll((nodes) =>
      nodes.map((n) => n.textContent.trim())
    );
    report.helpTips = await page.locator(".help-tip").count();

    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error?.stack || String(error));
  process.exit(1);
});
