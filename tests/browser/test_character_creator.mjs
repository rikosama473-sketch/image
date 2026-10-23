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
const generatorPort = await new Promise((resolve, reject) => {
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

const generatorServer = spawn(
  process.env.PYTHON || "python",
  ["ml/local_server.py", "--host", "127.0.0.1", "--port", String(generatorPort)],
  { cwd: root, env, stdio: ["ignore", "pipe", "pipe"] }
);
let generatorOutput = "";
generatorServer.stdout.on("data", (chunk) => { generatorOutput += chunk.toString(); });
generatorServer.stderr.on("data", (chunk) => { generatorOutput += chunk.toString(); });
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

async function waitForGeneratorHttp(url) {
  let lastError;
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1200) });
      if (response.ok) return response;
    } catch (error) {
      lastError = error;
    }
    if (generatorServer.exitCode !== null) {
      throw new Error("IMAGE local generator exited early. " + generatorOutput);
    }
    await delay(250);
  }
  throw new Error("IMAGE local generator did not start. " + String(lastError || "") + "\n" + generatorOutput);
}

try {
  const baseUrl = `http://127.0.0.1:${serverPort}`;
  const response = await waitForHttp(baseUrl + "/api/status");
  const status = await response.json();
  assert.equal(status.service, "IMAGE local AI edit bridge");
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
  assert.ok(Array.isArray(project.layers) && project.layers.length >= 2, "Constructor JSON stores independent layers; the base illustration is described separately");
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

  // The hair workbench must compose real repository parts, keep variants distinct, and export a valid project/PNG.
  const hairstylePage = await context.newPage();
  hairstylePage.on("pageerror", (error) => pageErrors.push("hairstyle workbench: " + error.message));
  await hairstylePage.goto(baseUrl + "/tools/hairstyle-workbench/index.html", { waitUntil: "domcontentloaded" });
  await hairstylePage.locator("#demoBtn").waitFor();
  await hairstylePage.locator("#demoBtn").click();
  await hairstylePage.waitForFunction(() => window.HairWorkbenchAPI &&
    window.HairWorkbenchAPI.getLayers().length >= 7 &&
    window.HairWorkbenchAPI.getCatalogHairCount() >= 5 &&
    document.querySelectorAll("#styleList [data-style]").length >= 5);
  const workbenchLayers = await hairstylePage.evaluate(() => window.HairWorkbenchAPI.getLayers());
  assert.ok(workbenchLayers.some((layer) => layer.category === "face"), "The workbench should use a face from the repository catalog");
  assert.ok(workbenchLayers.some((layer) => layer.category === "body"), "The workbench should use a body/base layer");
  assert.ok(workbenchLayers.filter((layer) => layer.category === "haircut").length >= 5, "The five candidate cuts must remain separate");
  assert.match(await hairstylePage.locator("#layerCount").innerText(), /capas/);
  const originalVariantCount = await hairstylePage.locator("#styleList [data-style]").count();
  assert.ok(originalVariantCount >= 5, "The initial looks should be distinct variants; found " + originalVariantCount);
  await hairstylePage.locator("#styleName").fill("E2E · variante independiente");
  await hairstylePage.locator("#duplicateStyleBtn").click();
  await hairstylePage.waitForFunction((count) => document.querySelectorAll("#styleList [data-style]").length === count + 1, originalVariantCount);
  const workbenchSavePromise = hairstylePage.waitForEvent("download");
  await hairstylePage.locator("#saveProjectBtn").click();
  const workbenchProjectDownload = await workbenchSavePromise;
  const workbenchProjectPath = await workbenchProjectDownload.path();
  assert.ok(workbenchProjectPath, "The hairstyle workbench should export a project JSON");
  const workbenchProject = JSON.parse(await readFile(workbenchProjectPath, "utf8"));
  assert.equal(workbenchProject.app, "IMAGE Hairstyle Workbench");
  assert.ok(workbenchProject.layers.length >= 7);
  assert.ok(workbenchProject.styles.length >= originalVariantCount + 1);
  await hairstylePage.locator("#projectFile").setInputFiles(workbenchProjectPath);
  await hairstylePage.waitForFunction(() => /Proyecto abierto/.test(document.querySelector("#notice")?.textContent || ""));
  assert.ok(await hairstylePage.locator("#layerCount").innerText().then(text => /capas/.test(text)));
  const workbenchPngPromise = hairstylePage.waitForEvent("download");
  await hairstylePage.locator("#exportBtn").click();
  const workbenchPngDownload = await workbenchPngPromise;
  const workbenchPngPath = await workbenchPngDownload.path();
  assert.ok(workbenchPngPath);
  const workbenchPng = await readFile(workbenchPngPath);
  assert.deepEqual([...workbenchPng.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10]);

  // The visual library must save a new reference, annotate it, build a recipe, and export its data.
  const visualPage = await context.newPage();
  visualPage.on("pageerror", (error) => pageErrors.push("visual reference library: " + error.message));
  await visualPage.goto(baseUrl + "/tools/visual-reference-library/index.html", { waitUntil: "domcontentloaded" });
  await visualPage.waitForFunction(() => /\d+/.test(document.querySelector("#resultCount")?.textContent || "") &&
    Number(document.querySelector("#statAssets")?.textContent || 0) > 0);
  await visualPage.waitForFunction(() => document.querySelectorAll("#grid [data-card]").length > 0);
  const refsBefore = Number(await visualPage.locator("#statRefs").innerText());
  await visualPage.locator("#newTitle").fill("E2E referencia ocular");
  await visualPage.locator("#newCategory").selectOption("eyes");
  await visualPage.locator("#newCreator").fill("Prueba automatizada");
  await visualPage.locator("#newSource").fill("https://www.pinterest.com/pin/123456789012345678/");
  await visualPage.locator("#newTags").fill("anime, iris radial, prueba e2e");
  await visualPage.locator("#addReferenceForm button[type=submit]").click();
  await visualPage.waitForFunction((before) => Number(document.querySelector("#statRefs")?.textContent || 0) === before + 1, refsBefore);
  await visualPage.locator("#search").fill("E2E referencia ocular");
  await visualPage.waitForFunction(() => document.querySelector('#grid [data-card*="user-ref-"]')?.textContent?.includes("E2E referencia ocular"));
  const e2eReference = visualPage.locator('#grid [data-card*="user-ref-"]').first();
  const e2eReferenceId = await e2eReference.getAttribute("data-card");
  await e2eReference.locator("[data-edit]").click();
  await visualPage.locator("#editName").fill("E2E referencia ocular anotada");
  await visualPage.locator("#editStatus").selectOption("reviewed_reference");
  await visualPage.locator("#editLicense").selectOption("reference_only_unverified");
  await visualPage.locator("#editNotes").fill("La prueba valida el flujo; los derechos siguen sin verificarse.");
  await visualPage.locator('#editForm button[type=submit]').click();
  await visualPage.waitForFunction(() => !document.querySelector("#editDialog")?.open);
  await visualPage.waitForFunction(() => document.querySelector('#grid [data-card*="user-ref-"] h3')?.textContent === "E2E referencia ocular anotada");
  const savedCard = visualPage.locator('#grid [data-card*="user-ref-"]').first();
  await savedCard.locator('input[data-select]').check();
  await visualPage.locator("#styleFamily").selectOption("eyes");
  await visualPage.locator("#styleName").fill("E2E receta de ojos");
  await visualPage.locator("#styleMood").selectOption("sharp");
  const stylesBefore = Number(await visualPage.locator("#statStyles").innerText());
  await visualPage.locator("#makeVariationBtn").click();
  await visualPage.waitForFunction((before) => Number(document.querySelector("#statStyles")?.textContent || 0) === before + 1, stylesBefore);
  const visualExportPromise = visualPage.waitForEvent("download");
  await visualPage.locator("#exportBtn").click();
  const visualExport = await visualExportPromise;
  const visualExportPath = await visualExport.path();
  assert.ok(visualExportPath, "The visual reference library should export a JSON bundle");
  const visualBundle = JSON.parse(await readFile(visualExportPath, "utf8"));
  assert.equal(visualBundle.project, "IMAGE visual reference library");
  assert.ok(visualBundle.references_added_by_user.some((reference) => reference.id === e2eReferenceId));
  assert.ok(visualBundle.annotations[e2eReferenceId], "The user annotation should be in the export");
  assert.ok(visualBundle.style_recipes.some((recipe) => recipe.name === "E2E receta de ojos"));
  assert.ok(visualBundle.selected_ids.includes(e2eReferenceId));

  // The switch must actually prevent remote navigation, not simply recolor links.
  await page.locator('#nav [data-cat="anatomy"]').click();
  const remoteLink = page.locator('#content a[href^="https://github.com"]').first();
  await remoteLink.waitFor();
  const constructorUrl = page.url();
  assert.equal(await remoteLink.getAttribute("aria-disabled"), "true");
  await remoteLink.dispatchEvent("click");
  await page.waitForFunction(() => /Modo Internet está apagado/.test(document.querySelector("#toast")?.textContent || ""));
  assert.equal(page.url(), constructorUrl, "A blocked Internet link must not navigate away");
  await page.evaluate(() => {
    Object.defineProperty(navigator, "onLine", { configurable: true, get: () => false });
    window.dispatchEvent(new Event("offline"));
  });
  await page.waitForFunction(() => document.querySelector("#internetModeToggle")?.dataset.state === "unavailable");

  // The local generation tool must guide model discovery and preflight without starting inference.
  const generatorUrl = "http://127.0.0.1:" + generatorPort;
  await waitForGeneratorHttp(generatorUrl + "/api/models");
  const generatorPage = await context.newPage();
  generatorPage.on("pageerror", (error) => pageErrors.push("local generator: " + error.message));
  await generatorPage.goto(generatorUrl + "/", { waitUntil: "domcontentloaded" });
  await generatorPage.waitForSelector("#scan-models-button");
  await generatorPage.locator("#scan-models-button").click();
  await generatorPage.waitForFunction(() => {
    const button = document.querySelector("#scan-models-button");
    return button && !button.disabled && document.querySelector("#model-scan-status")?.textContent?.trim().length > 0;
  });
  const scanStatus = await generatorPage.locator("#model-scan-status").innerText();
  assert.match(scanStatus, /No encontré|Detectados/);
  const picker = generatorPage.locator("#local-model-picker");
  if (await picker.isEnabled()) {
    assert.ok((await picker.locator("option").count()) >= 2, "Detected models should be selectable");
  } else {
    assert.match(scanStatus, /No encontré/, "An empty model search must explain that no weights were downloaded");
  }
  await generatorPage.locator("#diagnose-button").click();
  await generatorPage.waitForFunction(() => (document.querySelectorAll("#diagnostics-list .diagnostic-row").length >= 6) &&
    /REQUISITOS BÁSICOS DETECTADOS|REVISAR ANTES DE GENERAR/.test(document.querySelector("#diagnostics-summary")?.textContent || ""));
  assert.match(await generatorPage.locator("#diagnostics-summary").innerText(), /REQUISITOS BÁSICOS DETECTADOS|REVISAR ANTES DE GENERAR/);
  assert.match(await generatorPage.locator(".diagnostics-note").innerText(), /No genera imágenes/);
  assert.deepEqual(pageErrors, [], "Unexpected browser runtime errors: " + pageErrors.join("; "));
  console.log("PASS: Chromium E2E — constructor, reusable pieces, manual editor handoff, hairstyle variants and export, visual-reference annotations/recipes/export, Internet guard, local model discovery/preflight, zero JS errors.");
  await context.close();
} catch (error) {
  console.error("FAIL: IMAGE Character Creator browser E2E");
  console.error(error && error.stack ? error.stack : String(error));
  if (serverOutput) console.error("Server output:\n" + serverOutput);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close().catch(() => {});
  server.kill("SIGTERM");
  generatorServer.kill("SIGTERM");
  await Promise.all([server, generatorServer].map((child) => new Promise((resolve) => {
    if (child.exitCode !== null) return resolve();
    child.once("exit", resolve);
    setTimeout(resolve, 1500).unref();
  })));
  await rm(tempDir, { recursive: true, force: true });
}
