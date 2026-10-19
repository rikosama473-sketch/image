import test from "node:test";
import assert from "node:assert/strict";

globalThis.window = globalThis;
await import("../tools/character-editor/pro-editing.js");

const pro = globalThis.ImageProEditing;
assert.ok(pro, "The local editing engine should expose ImageProEditing");

function imageData(width, height, colors) {
  const data = new Uint8ClampedArray(colors.flatMap(color => [...color, 255]));
  return { width, height, data };
}
function alpha(image, index) { return image.data[index * 4 + 3]; }

test("background removal clears edge-connected matte and preserves source pixels", () => {
  const white = [255, 255, 255];
  const red = [220, 25, 30];
  const input = imageData(3, 1, [white, red, white]);
  const before = [...input.data];
  const output = pro.removeConnectedBackground(input, {
    targetColor: "#ffffff", tolerance: 0, feather: 0, protectLineArt: true
  });
  assert.equal(output.changed, true);
  assert.equal(alpha(output, 0), 0);
  assert.equal(alpha(output, 1), 255);
  assert.equal(alpha(output, 2), 0);
  assert.deepEqual([...input.data], before, "the original pixel buffer must remain untouched");
});

test("line-aware background removal protects an enclosed same-color region", () => {
  const white = [255, 255, 255], red = [220, 25, 30];
  const pixels = [
    white,white,white,white,white,
    white,red,red,red,white,
    white,red,white,red,white,
    white,red,red,red,white,
    white,white,white,white,white
  ];
  const output = pro.removeConnectedBackground(imageData(5, 5, pixels), {
    targetColor: "#ffffff", tolerance: 0, feather: 0
  });
  assert.equal(alpha(output, 0), 0);
  assert.equal(alpha(output, 12), 255, "enclosed white pixel should remain opaque");
});

test("color replacement preserves source buffer and returns a recolored buffer", () => {
  const input = imageData(2, 1, [[128, 96, 80], [40, 80, 120]]);
  const before = [...input.data];
  const output = pro.replaceColorRange(input, {
    sourceColor: "#806050", targetColor: "#c76cf2",
    tolerance: 0, softness: 0, preserveShading: true
  });
  assert.notDeepEqual([...output.data.slice(0, 3)], [128, 96, 80]);
  assert.deepEqual([...input.data], before, "color replacement is non-mutating by default");
  assert.deepEqual([...output.data.slice(4, 7)], [40, 80, 120], "unmatched pixels should stay untouched");
});

test("adjustment presets map to reversible canvas filters", () => {
  assert.equal(pro.layerAdjustmentsToCanvasFilter({}), "none");
  assert.match(pro.layerAdjustmentsToCanvasFilter({ brightness: 105, contrast: 114, saturation: 142 }), /brightness\(105%\)/);
  const normalized = pro.normalizeLayerAdjustments({ brightness: 900, contrast: -20, hue: 181 });
  assert.equal(normalized.brightness, 200);
  assert.equal(normalized.contrast, 0);
  assert.equal(normalized.hue, 180);
});

test("invalid raster dimensions and colors are rejected safely", () => {
  assert.throws(() => pro.removeConnectedBackground({ width: 2, height: 2, data: new Uint8ClampedArray(3) }), /valid image pixels/i);
  assert.throws(() => pro.replaceColorRange(imageData(1, 1, [[1, 2, 3]]), { sourceColor: "red" }), /six-digit/i);
});
