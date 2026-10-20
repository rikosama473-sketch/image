from pathlib import Path
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_character_layers as layers


def test_normalize_and_find_hair_label():
    assert layers.normalize_label("Upper-clothes") == "upper-clothes"
    assert layers.labels_for_group({0: "Background", 2: "Hair", 11: "Face"}, "hair") == {2}


def test_mask_from_labels_keeps_only_requested_class():
    labels = Image.new("L", (3, 1))
    labels.putdata([0, 2, 11])
    mask = layers.mask_from_labels(labels, {2})
    assert list(mask.getdata()) == [0, 255, 0]


def test_mask_combination_and_subtraction():
    left = Image.new("L", (3, 1))
    left.putdata([255, 255, 0])
    right = Image.new("L", (3, 1))
    right.putdata([0, 255, 255])
    assert list(layers.combine_masks(left, right).getdata()) == [255, 255, 255]
    assert list(layers.subtract_mask(left, right).getdata()) == [255, 0, 0]


def test_edit_delta_is_limited_to_upper_region():
    source = Image.new("RGB", (100, 200), (0, 0, 0))
    variant = source.copy()
    draw = ImageDraw.Draw(variant)
    draw.rectangle((20, 10, 30, 20), fill=(255, 255, 255))
    draw.rectangle((20, 170, 30, 180), fill=(255, 255, 255))
    mask = layers.edit_delta_mask(source, variant)
    assert mask.getpixel((25, 15)) > 0
    assert mask.getpixel((25, 175)) == 0


def test_apply_alpha_mask_preserves_canvas_and_suppresses_pixels():
    image = Image.new("RGBA", (4, 4), (240, 10, 10, 255))
    mask = Image.new("L", (4, 4), 0)
    mask.putpixel((1, 1), 255)
    output = layers.apply_alpha_mask(image, mask)
    assert output.size == (4, 4)
    assert output.getpixel((1, 1))[3] == 255
    assert output.getpixel((0, 0))[3] == 0
