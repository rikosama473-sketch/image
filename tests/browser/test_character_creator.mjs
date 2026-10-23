import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { mkdtemp, readFile, stat, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import { chromium } from "playwright";

const root = process.cwd();
const tempDir = await mkdtemp(path.join(os.tmpdir(), "image-browser-e2e-"));
const serverPort = await new Promise((resolve, reject) => {
  const probe = createServer();
  probe.once("error", reject);
  probe.listen(0, "127.0.0.1", () => {
    const address = probe.address();
    probe.close((error) => error ? reject(error) : resolve(address.port));
  });
});

const env = { ...process.env };
delete env.OPENAI_API_KEY;
const server = spawn(
  process.env.PYTHON || "python",
  ["tools/avatar-maker/ai_edit_server.py", "--host", "127.0.0.1", "--port", String(serverPort)],
  { cwd: root, env, stdio: ["ignore", "pipe", "pipe"] }
);
let serverOutput = "";
server.stdout.on("data", (chunk) => { serverOutput += chunk.toString(); });
server.stderr.on("data", (chunk) => { serverOutput += chunk.toString(); });
let browser;
const pageErrors = [];

async function waitForHttp(url) {
  let lastError;
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1200) });
      if (response.ok) return response;
    } catch (error) {
      lastError = error;
    }
    if (server.exitCode !== null) {
      throw new Error("IMAGE HTTP server exited early. " + serverOutput);
    }
    await delay(250);
  }
  throw new Error("IMAGE server did not start. " + String(lastError || "") + "\n" + serverOutput);
}

try {
  const baseUrl = `http://127.0.0.1:${serverPort}`;
  const response = await waitForHttp(baseUrl + "/api/status");
  const status = await response.json();
  assert.equal(status.service, "IMAGE local AI image editing bridge");
  assert.equal(status.api_key_configured, false, "E2E must run without a provider key");

  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("https://api.github.com/**", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify({ ok: true })
  }));

  await page.goto(baseUrl + "/tools/avatar-maker/index.html", { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#nav [data-cat]");
  await page.waitForFunction(() => document.querySelector("#catTitle")?.textContent?.trim());

  // Confirm the constructor really opens its internal asset bank and can add a real PNG layer.
  await page.locator('#nav [data-cat="starter"]').click();
  await page.waitForSelector("#starterGrid [data-starter-overlay]");
  await page.locator("#starterGrid [data-starter-overlay]").first().click();
  await page.waitForFunction(() => document.querySelectorAll("#layerList [data-layer]").length >= 2);
  assert.match(await page.locator("#toast").innerText(), /Superposición de prueba añadida/);

  // A cutout must be classified before it enters the reusable local library.
  await page.locator('#nav [data-cat="anatomy"]').click();
  await page.waitForSelector("#anatomyPieceType");
  await page.locator("#anatomySavePiece").click();
  await page.waitForFunction(() => /Elegí el tipo de pieza/.test(document.querySelector("#toast")?.textContent || ""));
  await page.locator("#anatomyPieceType").selectOption("hair");
  await page.locator("#anatomySavePiece").click();
  await page.waitForFunction(() => document.querySelectorAll("#localPartsGrid [data-local-part-add]").length === 1);
  const libraryCard = page.locator("#localPartsGrid article").first();
  assert.match(await libraryCard.innerText(), /Cabello/);
  assert.match(await libraryCard.innerText(), /origen: test/);
  assert.match(await libraryCard.innerText(), /needs_visual_review|needs visual review|revisión visual/i);

  // Reuse the saved piece as a separate layer, then verify reversible project I/O.
  await libraryCard.locator("[data-local-part-add]").click();
  await page.waitForFunction(() => [...document.querySelectorAll("#layerList [data-layer]")].some((el) => /Prueba completa/.test(el.innerText)) &&
    [...document.querySelectorAll("#layerList [data-layer]")].length >= 3);

  const saveProjectPromise = page.waitForEvent("download");
  await page.locator("#saveBtn").click();
  const projectDownload = await saveProjectPromise;
  const projectPath = await projectDownload.path();
  assert.ok(projectPath, "The project JSON should be downloadable");
  const projectStat = await stat(projectPath);
  assert.ok(projectStat.size > 50, "The project JSON should not be empty");
  const project = JSON.parse(await readFile(projectPath, "utf8"));
  assert.equal(project.app, "IMAGE Character Creator");
  assert.ok(Array.isArray(project.layers) && project.layers.length >= 3);
  assert.ok(project.layers.some((layer) => layer.category === "hair" && layer.sourceCategory === "test"));

  const beforeReload = await page.locator("#layerList [data-layer]").count();
  await page.locator("#jsonFile").setInputFiles(projectPath);
  await page.waitForFunction(() => /Diseño cargado/.test(document.querySelector("#toast")?.textContent || ""));
  await page.waitForFunction((expected) => document.querySelectorAll("#layerList [data-layer]").length >= expected, beforeReload);

  // Export must be a real, non-empty PNG, not only a button or an alert.
  const pngPromise = page.waitForEvent("download");
  await page.locator("#exportBtn").click();
  const pngDownload = await pngPromise;
  const pngPath = await pngDownload.path();
  assert.ok(pngPath, "PNG export should create a download");
  const pngStat = await stat(pngPath);
  assert.ok(pngStat.size > 1000, "PNG export should have image data");
  const pngHeader = await readFile(pngPath);
  assert.deepEqual([...pngHeader.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10]);

  // Handoff into the manual editor must preserve the full image and independent layers.
  const manualPage = await context.newPage();
  manualPage.on("pageerror", (error) => pageErrors.push("manual editor: " + error.message));
  await manualPage.goto(baseUrl + "/tools/manual-character-editor/index.html", { waitUntil: "domcontentloaded" });
  await manualPage.locator("#projectFile").setInputFiles(projectPath);
  await manualPage.waitForFunction(() => /Proyecto del Constructor importado/.test(document.querySelector("#status")?.textContent || ""));
  await manualPage.waitForFunction(() => document.querySelectorAll("#layers .layer-item").length >= 3);
  const importedLayerNames = await manualPage.locator("#layers .layer-name").allTextContents();
  assert.ok(importedLayerNames.some((name) => /Prueba completa/.test(name)), "The original independent layer should survive constructor handoff");
  assert.ok(importedLayerNames.some((name) => /Ilustración base/.test(name)), "The base illustration should remain explicitly identified");

  // The manual editor also needs to save, reopen and export its own project.
  const manualSavePromise = manualPage.waitForEvent("download");
  await manualPage.locator("#saveProjectBtn").click();
  const manualProjectDownload = await manualSavePromise;
  const manualProjectPath = await manualProjectDownload.path();
  assert.ok(manualProjectPath, "The manual project JSON should be downloadable");
  const manualProject = JSON.parse(await readFile(manualProjectPath, "utf8"));
  assert.equal(manualProject.app, "IMAGE Manual Character Editor");
  assert.ok(manualProject.layers.length >= 3);
  await manualPage.locator("#projectFile").setInputFiles(manualProjectPath);
  await manualPage.waitForFunction(() => /Proyecto .* recuperaron|Proyecto abierto|Proyecto cargado|proyecto .*restaur/i.test(document.querySelector("#status")?.textContent || ""));
  assert.ok(await manualPage.locator("#layers .layer-item").count() >= 3, "Manual editor project reopen must restore editable layers");
  const compositePromise = manualPage.waitForEvent("download");
  await manualPage.locator("#exportCompositeBtn").click();
  const compositeDownload = await compositePromise;
  const compositePath = await compositeDownload.path();
  assert.ok(compositePath, "The manual editor composite should export a PNG");
  const compositeStat = await stat(compositePath);
  assert.ok(compositeStat.size > 1000);
  const compositeHeader = await readFile(compositePath);
  assert.deepEqual([...compositeHeader.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10]);

  // The Internet toggle is a functional state switch, not only color decoration.
  const internetToggle = page.locator("#internetModeToggle");
  await page.waitForFunction(() => document.querySelector("#internetModeToggle")?.dataset.state === "on");
  await internetToggle.click();
  await page.waitForFunction(() => document.querySelector("#internetModeToggle")?.dataset.state === "off");
  assert.equal(await internetToggle.getAttribute("aria-pressed"), "false");

  assert.deepEqual(pageErrors, [], "Unexpected browser runtime errors: " + pageErrors.join("; "));
  console.log("PASS: real Chromium E2E — internal asset layer, required category, IndexedDB save/reuse, project JSON save/reopen, PNG signature/size, Internet toggle, zero page errors.");
  await context.close();
} catch (error) {
  console.error("FAIL: IMAGE Character Creator browser E2E");
  console.error(error && error.stack ? error.stack : String(error));
  if (serverOutput) console.error("Server output:\n" + serverOutput);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close().catch(() => {});
  server.kill("SIGTERM");
  await new Promise((resolve) => {
    if (server.exitCode !== null) return resolve();
    server.once("exit", resolve);
    setTimeout(resolve, 1500).unref();
  });
  await rm(tempDir, { recursive: true, force: true });
}
