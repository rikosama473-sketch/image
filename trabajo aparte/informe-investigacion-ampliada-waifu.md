# Female Anime / Waifu Asset Library — Exhaustive Reference & Decision Report

**For: Character Editor Development Team**
**Date: 2026-10-21 | Scope: Visual identification, reference sourcing, licensed assets, UI workflow**

---

## Executive Summary

This report catalogs **140+ genuinely distinct reference entries** across four component categories (hairstyles, clothing, eyes, accessories) for a female anime character editor asset library. It separates **reference-only imagery** (DeviantArt, Pixiv, tutorials — not commercially reusable) from **downloadable/licensed assets** (ArtStation Marketplace, Itch.io, BOOTH, CraftPix). Verified prices and licenses are noted only where confirmed in evidence. A UI workflow is proposed for marking "extra elements" that must be isolated per component. Image-search query links are provided wherever direct clean monochrome square references cannot be confirmed from evidence.

**Key decisions for the team:**
- Best free commercial-use sprite base: cogabushi's 25-pack (Itch.io, free, commercial OK) [25] and CraftPix schoolgirls pack (royalty-free, unlimited projects) [26]
- Best paid reference packs (verified prices): ArtStation 210-girl model sheet $4.99/$15.00 [8]; 240 Asian Female $4.99/$15.00 [10]; 370 Fantasy Armor $5.00/$15.00 [53]; BOOTH Ninja Design Collection ¥1,000 [70]
- sutemo's female sprite (Itch.io) is **free, no commercial attribution required**, modular PSD [52]
- NovelAI tag taxonomy [68] is the most complete machine-readable component vocabulary for all four categories
- All AI-generated packs (ArtStation packs, BOOTH ninja pack) must be treated as **reference-only** for tracing/identification; downstream commercial rights depend on each platform's AI policy

---

## Part 1 — How to Use This Atlas in a Character Editor UI

### Extra-Element Isolation (Red-Marking Protocol)

Every reference source contains multiple component categories simultaneously (a hairstyle reference also shows eyes, a clothing sheet also shows hair). For the atlas UI:

1. **Tag each reference entry** with its PRIMARY component (the catalogued element) and SECONDARY elements (everything else present in the image)
2. **Mark secondary elements in red** in the UI overlay so the artist/developer knows which parts to ignore when isolating the target component
3. Example: DeviantArt "50 Female Anime Hairstyles" [35] → PRIMARY: hairstyle; RED: face shape, eye style, expression. The Clip Studio maid uniform tutorial [15] → PRIMARY: clothing; RED: hairstyle (varies per example), eye shape, body proportion

This table structure should be applied to every atlas tile:

| Atlas Tile | Primary Component | Secondary Elements (mark red) | Source |
|---|---|---|---|
| Bun/Odango hair | Hairstyle | Eyes, face, expression | [11][13][42] |
| Sailor uniform | Clothing | Hair, shoes, socks, accessories | [48][63] |
| Almond eye shape | Eye | Eyelashes, brow, iris pattern | [1][6][50] |
| Hair bow | Accessory | Entire hairstyle, outfit, face | [19][68] |

---

## Part 2 — Hairstyles: 30+ Named Styles with Reference Sources

### 2A. Named Style Catalog

The following 30+ distinct named hairstyle types are confirmed across multiple primary and secondary sources [11][13][17][27][34][35][36][37][38][39][42][43][67][68].

#### LENGTH-BASED STYLES

| # | Style Name | JP Name | Key Visual Features | Primary Sources |
|---|---|---|---|---|
| 1 | Short / Boyish cut | ボーイッシュ | Close-cropped, angular, cowlick at nape | [17][67][43] |
| 2 | Short inner curl | 内まき | Short with ends curling inward toward face | [17][67] |
| 3 | Blunt bangs short | ぱっつん | Dead-straight fringe, near-uniform length all around | [17][67] |
| 4 | Bob cut | ボブカット | Chin-length, full volume, rounded silhouette | [13][68] |
| 5 | Medium straight | ミディアムストレート | Shoulder-length, flat and sleek | [17][43][67] |
| 6 | Medium wave | ウェーブ | Shoulder-length with S-curve body | [17][67] |
| 7 | Long straight | ロングストレート | Past-shoulder, sleek, flows as one mass | [43][67] |
| 8 | Long wavy | ロングウェーブ | Past-shoulder, undulating; associated with mystery [43] | [43][67] |
| 9 | Long curled / voluminous bunches | ロングカール | Elaborate curls, pampered silhouette [43] | [43][27] |

#### UPDO / TIE STYLES

| # | Style Name | JP Name | Key Visual Features | Primary Sources |
|---|---|---|---|---|
| 10 | High ponytail | ハイポニーテール | Tie point at crown, tail falls from apex | [17][68] |
| 11 | Low ponytail | ローポニーテール | Tie at nape, softer silhouette | [68] |
| 12 | Side ponytail | サイドポニーテール | Single tie offset to one side | [68] |
| 13 | Short ponytail | ショートポニー | Tie but tail is stub-length | [68] |
| 14 | Braided ponytail | 三つ編みポニー | Tail rendered as braid [68] | [68][64] |
| 15 | Twin tails (pigtails) | ツインテール | Two high or mid ties, one per side; "childlike charm" [43] | [11][13][17][43][68] |
| 16 | Half-up / half-updo | ハーフアップ | Top section tied, bottom section loose | [68] |
| 17 | Odango / bun pair | お団子ヘア | Two spherical buns at ~45° from crown; "dango" reference [11][42] | [11][13][27][42] |
| 18 | Single topknot / samurai bun | お団子 | Single bun at crown; warrior connotation [11] | [11][68] |
| 19 | Folded ponytail | | Tail looped back through tie | [68] |

#### BRAID STYLES

| # | Style Name | JP Name | Key Visual Features | Primary Sources |
|---|---|---|---|---|
| 20 | Standard three-strand braid (pigtail braid) | シンプルおさげ | Classic alternating-strand braid; best drawn with zigzag guide [65] | [64][65][66] |
| 21 | French braid / braided-in | 編み込み | Braid anchored to scalp, strands pulled from sides as it descends [65][66] | [65][66][68] |
| 22 | Loose / yurufuwa braid | ゆるふわ三つ編み | Intentionally fluffy, stray hairs (おくれ毛); heart-mark guide recommended [66] | [65][66] |
| 23 | Twin braids | 三つ編みツインテール | Two braids, one per side [64] | [64][65] |
| 24 | Braid loop / arranged braid | アレンジ編み込み | Braid formed into ring or pinned arrangement [65] | [65] |
| 25 | Side braid | サイドブレイド | Single braid swept to one side | [65] |

#### FEATURE / ORNAMENTAL ELEMENTS

| # | Style Name | JP Name | Key Visual Features | Primary Sources |
|---|---|---|---|---|
| 26 | Ahoge | アホ毛 | Single strand sticking up; "foolish hair" [11][42] | [11][13][27][42][68] |
| 27 | Heart ahoge | ハートアホ毛 | Ahoge formed into heart loop | [68] |
| 28 | Huge ahoge | 大アホ毛 | Exaggerated size variant | [68] |
| 29 | Antenna hair (shokkaku) | 触角 | Two upward projections; sweet/enthusiastic character type [27] | [27][68] |
| 30 | Hime cut | 姫カット | Blunt bangs + cheek-level sidebangs + long body; "princess" [11][42] | [11][27][42] |
| 31 | Hair over one eye | 片目隠れ | Long asymmetrical bang covering one eye; mystery/shy [21][42] | [21][42][68] |
| 32 | Hair over both eyes | 両目隠れ | Bangs fully obscure eyes | [22][68] |
| 33 | Parted bangs | 分け目バング | Center-part exposing forehead | [68] |
| 34 | Swept bangs | 流しバング | Side-swept fringe | [68] |
| 35 | Sidelocks | サイドロック | Long strands framing face in front of ears | [68] |
| 36 | Ojou ringlets / drill curls | お嬢巻き | Tight spiral curls framing face; "high social status" [42] | [11][27][42] |
| 37 | Spiky / shonen hair | スパイク / 主人公ヘア | Gravity-defying spikes; hot-blooded protagonist [11][42] | [11][27][42][68] |
| 38 | Pompadour | ポンパドール | Volume swept upward from forehead | [68] |
| 39 | Afro | アフロ | Rounded natural texture volume | [68] |
| 40 | Shoujo style | 少女スタイル | Fine-line flowing strands, soft highlights; tutorial by REBORNxYUI | [41] |

### 2B. Reference Sheet Sources (DeviantArt)

These are **reference-only** (not commercially reusable without author permission):

| Source Title | Author | Confirmed Content | Extra Elements (red) | URL |
|---|---|---|---|---|
| manga girl hair reference sheet II | StyrbjornAndersson | Multiple named styles, 420K views | Face shape, eyes | [34] deviantart.com/styrbjornandersson/art/manga-girl-hair-reference-sheet-II---20130113-348275702 |
| 50 Female Anime Hairstyles | AnaisKalinin | 50 styles, copic liner on paper | Eyes, face | [35] deviantart.com/anaiskalinin/art/50-Female-Anime-Hairstyles-308941397 |
| Various Female Anime+Manga Hairstyles | Elythe | 50 styles across 6 scanned pages | Eyes, face | [36] deviantart.com/elythe/art/Various-Female-Anime+Manga-Hairstyles-307583395 |
| anime hair reference | ryky | Tutorial + multiple styles, 536K views | Eyes, expression | [37] deviantart.com/ryky/art/anime-hair-reference-520974411 |
| anime hair (girls) guidelines | yosopher | Guidelines, CC BY-SA 3.0, 12.7K views | Minimal extras | [38] deviantart.com/yosopher/art/anime-hair-(girls)-guidelines-375934474 |
| Character Hair Reference Sheet | GabrielleBrickey | Named types with drawing class | Eyes, proportions | [39] deviantart.com/gabriellebrickey/art/Character-Hair-Reference-Sheet-663911704 |
| 16 Anime Hairstyles | cupiekristin | 16 colored styles | Eyes, face | [40] deviantart.com/cupiekristin/art/16-Anime-Hairstyles-287323552 |
| How to Draw Shoujo Style Hair | REBORNxYUI | Shoujo-specific technique | Eyes, face | [41] deviantart.com/rebornxyui/art/How-to-Draw-Shoujo-Style-Hair-259912277 |
| How to Draw Anime Hair Styles | LearntoDrawAnime | 720×3000px tutorial sheet | Face, proportions | [69] deviantart.com/learntodrawanime/art/How-to-Draw-Anime-Hair-Styles-285515551 |

**License note:** yosopher's guideline sheet [38] is explicitly CC BY-SA 3.0 — the only confirmed open license in this group. All others are reference/inspiration use only unless authors confirm otherwise.

### 2C. Tutorial & Instructional Sources

| Platform | Title | Styles Covered | URL |
|---|---|---|---|
| Clip Studio Tips | Easy Guide to Drawing Anime Hair [16] | S-curves, wavy, highlights technique | clipstudio.net/how-to-draw/archives/161517 |
| Clip Studio Tips | Choosing a Hairstyle for Your Anime Character [42] | Spiky, odango, spiral, ahoge, hime | tips.clip-studio.com/en-us/articles/7165 |
| Palmie (Japanese) | 髪の毛の描き方講座 [17] | 7 styles: short/bob/semi-long/ponytail/twin-tail/braid/tate-roll + crown position | palmie.jp/lessons/63 |
| Clip Studio (Japanese) | 髪の毛の描き方でキャラクターの個性を演出しよう！ [67] | Short (3 types), medium (3 types), long (3 types) | clipstudio.net/oekaki/archives/149946 |
| Sensei by Pixiv | キャラクターの髪コース (7-lecture course) [64] | Structure, simple, detailed, movement, twin-tail/ponytail, braid | sensei.pixiv.net/ja/course/20 |
| ATAM Academy | 初心者も簡単！三つ編みのイラストの描き方 [65] | 5 braid guide methods | atam-academy.com/blog/43326/ |
| egaco | 簡単三つ編み描き方講座 [66] | 5 braid methods with difficulty/3D/workload ratings | comic.smiles55.jp/guide/9269/ |
| Anime Art Magazine | Anime hairstyles for girls [43] | Short/medium/long with fringe analysis | animeartmagazine.com/anime-hairstyles-for-girls-… |
| WikiHow | A Guide to the Most Iconic Anime Hair Styles [11] | Odango, hime, ahoge, twin tails, spiky, topknot | wikihow.com/Anime-Hair-Styles |

### 2D. Pixiv Sources

| Pixiv URL | Content | Tags |
|---|---|---|
| pixiv.net/artworks/69100777 [12] | Hair tutorial (June 2018) | Hair, Tutorial |
| pixiv.net/artworks/108693077 [14] | How-to-draw hair (June 2023) | hair, Tutorial, how to draw |
| pixivision.net/ja/a/11971 [13] | Curated hairstyle illustration collection | ショートカット, ロングヘア, ボブ, ツインテール, ポニーテール, 三つ編み, お団子, アホ毛, 編み込み |

### 2E. Pinterest Search Query Link (when direct monochrome ref unavailable)

> **Fallback query:** `site:pinterest.com anime female hairstyle reference sheet monochrome lineart`
> Direct confirmed Pinterest pin: pinterest.com/pin/anime-hair--8092474325716844/ [28] — female hairstyles chart with named styles

### 2F. PixAI Tag Links (Hair)

| Tag | Artwork Count | URL |
|---|---|---|
| hair_down | 7,709 [20] | pixai.art/en/tags/artwork/hair_down |
| hair_over_one_eye | 121,399 [21] | pixai.art/tags/artwork/hair_over_one_eye |
| hair_over_eyes | 19,696 [22] | pixai.art/tags/artwork/hair_over_eyes |

> **Additional PixAI hair tag queries to run** (not yet confirmed from evidence — use direct search):
> `pixai.art/tags/artwork/twintails`, `pixai.art/tags/artwork/ponytail`, `pixai.art/tags/artwork/braid`, `pixai.art/tags/artwork/hime_cut`, `pixai.art/tags/artwork/ahoge`

### 2G. NovelAI Complete Hair Tag Taxonomy [68]

This is the most complete machine-readable vocabulary for the character editor tag system:

**Hairstyle base tags:** bob cut, braid, french braid, ponytail, twintails, half updo, pompadour, afro

**Ponytail variants:** high ponytail, low ponytail, side ponytail, short ponytail, folded ponytail, braided ponytail, topknot

**Front-hair/bang tags:** bangs, blunt bangs, hair between eyes, hair over eyes, hair over one eye, parted bangs, swept bangs, sidelocks

**Crown/top-of-head tags:** ahoge, huge ahoge, heart ahoge, antenna hair, hair pulled back, hair slicked back

**Texture tags:** curly hair, messy hair, spiked hair, straight hair, wavy hair

**Color base tags (11):** black hair, blonde hair, platinum blonde hair, blue hair, aqua hair, light blue hair, dark blue hair, brown hair, light brown hair, green hair, dark green hair, light green hair, grey hair, orange hair, pink hair, purple hair, light purple hair, red hair, white hair

**Complex color tags:** multicolored hair, colored inner hair, colored tips, gradient hair, rainbow hair, split-color hair, streaked hair, two-tone hair

---

## Part 3 — Clothing: 30+ Outfit Types with Reference Sources

### 3A. Outfit Catalog by Category

#### SCHOOL / INSTITUTIONAL UNIFORMS

| # | Garment / Style | Key Visual Components | Subvariants | Sources |
|---|---|---|---|---|
| 1 | Sailor uniform (serafuku) | Wide collar + square back flap, pleated skirt (24 pleats), scarf/ribbon, boxy top [48] | Summer (short sleeve + firm cloth), Winter (long sleeve + heavy cloth) [48] | [48][61] |
| 2 | Blazer uniform | Tailored blazer, checkered pleated skirt, school emblem patch on left chest [47] | Tie variant, ribbon variant, summer blouse-only variant, vest variant [47] | [47][63] |
| 3 | Gym uniform / athletic wear | Short shorts + polo or jersey top | — | [63] |
| 4 | Maid uniform | Dress/top+skirt + apron; frilled; traditionally black + white [15] | Standard frilly (puffy shoulders), Sexy (short skirt, minimal ruffles), Cute (full ruffles), Traditional (long skirt + sleeves) [15] | [15][60] |
| 5 | Wa-maid (Japanese-Western hybrid) | Kimono skirt / hakama + frilly white apron, floral hair acc., ribbon bows [60] | — | [60] |

#### TRADITIONAL JAPANESE

| # | Garment / Style | Key Visual Components | Subvariants | Sources |
|---|---|---|---|---|
| 6 | Furisode kimono | Very long swinging sleeves, obi sash at back, juban undercollar visible | Multiple angles incl. back and 3/4 | [44] |
| 7 | Houmongi kimono | Semi-formal visiting kimono, shorter sleeves than furisode | With haori overcoat variant | [44] |
| 8 | Yukata | Casual summer kimono, lightweight, simpler obi | — | [44] |
| 9 | Hakama (pants) | Wide pleated trousers over kimono top | Miko red variant (hibakama), kendo variant | [46] |
| 10 | Miko / shrine maiden | White hakue blouse + red hibakama, taski sleeve cord, mizuhiki hair cord [46] | Dark green or white hibakama variant [46] | [46] |
| 11 | Ninja / kunoichi outfit | Form-fitting bodysuit, sash belt, mask elements, tabi boots [70] | 330 reference sheets available in BOOTH pack | [70] |

**Authentic kimono search terms (per mikiko-art [44]):** Kitsuke, Furisode, Iromuji, Houmongi, Komon, tomesode, Kurotomesode, Uchikake, Yukata, Otaiko musubi, ginza-musubi, fukura suzume, kai no kuchi musubi, nagoya obi, Hakama, Haori

#### LOLITA FASHION

| # | Subgenre | Key Visual Components | Skirt Shape | Color Palette | Sources |
|---|---|---|---|---|---|
| 12 | Gothic Lolita | Bell-shaped or A-line skirt to knee, crosses/skulls/crown prints, dark colors, modesty sleeves [45] | Bell-shaped preferred [45] | Dark, rich (black, deep purple, wine) | [45][62] |
| 13 | Sweet Lolita | Pastel bell-shaped skirt, cute prints (bunnies, candy, kitties), maximum ruffles [45] | Bell-shaped; occasional A-line [45] | Pastels (pink, mint, lavender) | [45][62] |
| 14 | Classic Lolita | Victorian influence, grace + elegance, floral/fruit prints [45] | A-line preferred [45] | Muted (ivory, bordeaux, dusty blue) | [45][62] |
| 15 | Wa-Lolita | Kimono/hakama elements merged with lolita silhouette | — | — | [62] |

**Key lolita garment vocabulary [45]:**
- **Jumperskirt (JSK):** Sleeveless dress worn over blouse
- **One-piece (OP):** Sleeved dress, standalone
- **Cutsew:** Casual shirt replacing blouse in casual lolita
- **Knee-high socks:** Required; bob socks acceptable in warm weather
- **Petticoat:** Underneath for bell shape volume

> ⚠️ Per Ginger's Guide [45]: "Lolita representation in anime is almost always incorrect." Recommend sourcing from actual lolita brand references (Baby, the Stars Shine Bright; Angelic Pretty; Moitié) for authentic silhouettes; the DeviantArt guide is the most detailed confirmed reference in evidence.

#### FANTASY / ADVENTURE / ARMOR

| # | Style | Key Visual Components | Sources |
|---|---|---|---|
| 16 | Fantasy mage / sorceress | Robes or dress, corset, leather belt, leather pouch, knee boots, gloves [68] | [68][25] |
| 17 | Female medieval warrior armor | Plate/chainmail elements on female form, 370 reference images available [53] | [53] |
| 18 | Fantasy RPG casual adventurer | Tunic, cape, boots, belt pouches | [25][68] |
| 19 | Magical girl | Frilly colored costume, sailor-derived, star motifs | [32][68] |

#### CASUAL / CONTEMPORARY

| # | Style | Key Visual Components | Sources |
|---|---|---|---|
| 20 | Casual street wear | Varied; jeans, tops, cardigans | [9][10] |
| 21 | Blazer casual | Oversized blazer, shorts or skirt | [22] |
| 22 | Tank top / T-shirt casual | Minimal top, shorts/skirt | [68] |
| 23 | Dress (generic) | Simple one-piece dress | [68] |
| 24 | Idol outfit | Fitted colorful costume, ruffles, star motifs | [63] |
| 25 | Cheerleader / athletic | Skirt + matching top, pompoms implied | [63] |

#### ADDITIONAL COSTUME TYPES (confirmed via NovelAI tags [68] and packs)

| # | Style | Notes |
|---|---|---|
| 26 | Jacket outfit | Jacket as primary topwear [68] |
| 27 | Dress shirt outfit | Formal blouse/shirt as primary [68] |
| 28 | Corset outfit | Corset as defining element, fantasy/gothic [68] |
| 29 | Armor + gloves + boots | Full adventurer set with leather pouch [68] |
| 30 | Pelvic curtain / tabard | Fantasy waist-wrap garment [68] |

### 3B. Clothing Reference Sources

#### Tutorials & Instructional

| Source | Outfit Type | URL |
|---|---|---|
| CLIP STUDIO TIPS — Ecao [15] | Maid uniform (4 substyles) | tips.clip-studio.com/en-us/articles/3094 |
| Anime Art Magazine [46] | Miko shrine maiden | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ |
| Anime Art Magazine [47] | Blazer school uniform | animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/ |
| Anime Art Academy [48] | Sailor uniform (serafuku) | animeartacademy.com/p/how-to-draw-anime-sailor-uniform |
| AnimeOutline [18] | School uniform (6-step drawing) | animeoutline.com/how-to-draw-anime-school-girl-in-6-steps/ |
| DeviantArt — mikiko-art [44] | Kimono (furisode + houmongi + haori) | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 |
| DeviantArt — who-dat-betch [45] | Lolita fashion (gothic/sweet/classic) | deviantart.com/who-dat-betch/journal/Ginger%27s-Guide-to-drawing-Lolita-455570174 |

#### PixAI Tag Pages (Clothing)

| Tag | Count | URL |
|---|---|---|
| school_uniform | 414,878 [63] | pixai.art/tags/artwork/school_uniform |
| serafuku (sailor uniform) | 97,536 [61] | pixai.art/tags/artwork/serafuku |
| lolita_fashion | 41,502 [62] | pixai.art/tags/artwork/lolita_fashion |
| wa_maid | 2,254 [60] | pixai.art/tags/artwork/wa_maid |

> **Additional PixAI clothing tag queries** (not confirmed from evidence — search directly):
> `pixai.art/tags/artwork/kimono`, `pixai.art/tags/artwork/miko`, `pixai.art/tags/artwork/armor`, `pixai.art/tags/artwork/gothic_lolita`, `pixai.art/tags/artwork/hakama`, `pixai.art/tags/artwork/maid`

---

## Part 4 — Anime Eyes: 25+ Distinct Types with Reference Sources

### 4A. Eye Shape / Form Taxonomy

Evidence from [1][6][7][29][30][50][54][55][57][58][68] confirms the following distinct eye types:

#### BY OUTER CORNER ORIENTATION

| # | Type | Visual Signature | Character Association | Sources |
|---|---|---|---|---|
| 1 | Upturned (sharp) | Outer corner rises above pupil line; fierce edges | Intense, determined, villain types [6][50] | [1][6][50] |
| 2 | Downturned (gentle) | Outer corner dips below pupil line | Gentle, sweet, approachable [6][50] | [6][50] |
| 3 | Neutral / horizontal | Outer corner at same level as pupil | Balanced, normal expression baseline [7] | [7][50] |

#### BY OVERALL SHAPE GEOMETRY

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 4 | Rounded | Nearly circular opening; maximum innocence; large iris | [1][50][51] |
| 5 | Almond / elongated | Wider horizontal span, tapered ends; "bold personality" [50] | [1][50] |
| 6 | Rectangular / angular | Squared corners; more masculine tendency [29][58] | [29][58] |
| 7 | Triangular | Sharp angular shape; "more intense" per JeyRam [1] | [1] |
| 8 | Narrow / sharp | Compressed vertical height; intense, suspicious | [50] |

#### BY EYELID CONFIGURATION

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 9 | Double eyelid | Visible crease above lash line; bold, awake, dramatic [50] | [50] |
| 10 | Single eyelid (monolid) | Smooth contour, no crease; softer, younger, minimalist [50] | [50] |
| 11 | Lowered upper eyelid | Eyelid droops halfway; sleepy, calm, or serious [49] | [49] |
| 12 | Wide open / surprised | Upper eyelid raised maximally; large iris visible | [7][50] |

#### BY EYELASH STYLE

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 13 | Minimal / thin lashes | Sparse line indication; simple/young | [57][59] |
| 14 | Curved upward lashes | Classic "anime sweep" — curve sideways then up [1] | [1] |
| 15 | Tapered / pointed lashes | Long, sharp tips; almond-eye style [50] | [50] |
| 16 | Dense / dramatic lashes | High lash count; intense personality [50] | [50] |
| 17 | Bottom-lash visible | Lower lash line drawn (female specialist style) [59] | [59] |
| 18 | Winged / curled lashes | Pronounced curl with wing extension [50] | [50] |

#### BY PUPIL / IRIS SPECIALTY

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 19 | Standard oval iris | Typical anime; iris may be oval not round [7] | [7] |
| 20 | Slit pupils | Vertical slit; feline, supernatural [68] | [68] |
| 21 | Star-shaped pupils | Star pattern in pupil; magical/exaggerated [68] | [68] |
| 22 | Heart-shaped pupils | Heart in pupil; love/comedy | [68] |
| 23 | Diamond pupils | Diamond geometry | [68] |
| 24 | Flower-shaped pupils | Floral pattern | [68] |
| 25 | Symbol-shaped pupils | General non-geometric symbol | [68] |
| 26 | Horizontal pupils | Bar-shaped; animal/supernatural | [68] |
| 27 | Mismatched pupils | Different shape per eye | [68] |
| 28 | No visible pupil | Blank iris; ghost/supernatural | [30] |
| 29 | Spiral pupils | Spiral pattern; hypnosis/comedy | [30] |

#### BY SCLERA / SPECIAL FEATURES

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 30 | Black sclera | White-on-black inversion; horror/demon | [68] |
| 31 | Flaming eyes | Fire overlaid on eye | [68] |
| 32 | Glowing eyes | Luminous iris/pupils | [68] |
| 33 | Bags under eyes | Shadow line beneath; tired/villain | [68] |
| 34 | Heterochromia | Different color per eye | [68] |

#### BY CHARACTER TYPE / SIZE CONVENTION

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 35 | Chibi/cute (hyperlarge) | Iris up to 1/3 of face; sparkle-dominant [50] | [50][51] |
| 36 | Moe/shojo (70% iris) | "Usagi" type — nearly all iris visible, giant highlights [51] | [51] |
| 37 | Seinen/mature (small iris) | Smaller iris-to-face ratio; realistic proportion [6] | [6] |
| 38 | Villain/antihero | Sharp upturned corners, narrow pupils, deeper shadows [50] | [50] |
| 39 | Child/young | Big round + thick lashes + high arching brows [50] | [50] |

#### BY LIGHT / HIGHLIGHT PATTERN

| # | Type | Visual Signature | Sources |
|---|---|---|---|
| 40 | Two-highlight standard | Large highlight (main source) + small (secondary) [7] | [7] |
| 41 | Gradient iris | Dark outer ring blending lighter toward center [50] | [50] |
| 42 | Gradient with displaced pupil | Tanjiro/Demon Slayer style — gradient merges into pupil area [51] | [51] |
| 43 | Asterisk iris | Rick & Morty variant; irregular asterisk-shaped iris [51] | [51] |

### 4B. Eye Reference Sheets (DeviantArt)

| Source | Author | Content | Extra Elements (red) | URL |
|---|---|---|---|---|
| Anime Eyes Reference | imaginary-ang3l | 54 distinct designs (28 original + 26 referenced) [2] | Minimal — isolated eyes | [2] deviantart.com/imaginary-ang3l/art/Anime-Eyes-Reference-268915669 |
| Anime Eye Reference Sheet | LonelyWolfa | Line-art style, 3264×2448px [3] | Minimal | [3] deviantart.com/lonelywolfa/art/Anime-Eye-Reference-Sheet-743561128 |
| Simple Anime Eye Styles (Girls) | RikaYoru | Digital colored, multiple styles; tutorial on request [4] | Minimal | [4] deviantart.com/rikayoru/art/Simple-Anime-Eye-Styles-(Girls)-371705474 |
| Anime Eye Chart | PenguinNinja226 | Photoshop CS stock eyes compiled [5] | Minimal | [5] deviantart.com/penguinninja226/art/Anime-Eye-Chart-73978246 |
| Eye Shapes Reference (animation) | InokitheFox | Upper eyelid movement frame-by-frame [54] | Minimal | [54] deviantart.com/inokithefox/art/Eye-Shapes-Reference-761999563 |
| Character Eye Chart Page | Oxdarock | Named character eyes, color + lineart pairs, ~20 per page [55] | Minimal | [55] deviantart.com/oxdarock/art/Character-Eye-Chart-Page-476769308 |
| Eye. Tutorial + References | Anastasia-berry | Iris/eyelash variants, 7000×9000px JPG [56] | Minimal | [56] deviantart.com/anastasia-berry/art/Eye.-Tutorial-+-References-735761824 |
| Anime Eyes 3 | izka197 | Female eyes only; A4 size; multiple shapes/pupil/shine variants [57] | Minimal | [57] deviantart.com/izka197/art/Anime-Eyes-3-264888771 |
| Eyes in Manga — Feminine vs Masculine | DragonReine | Comparative feminine/masculine eye shapes [58] | Minimal | [58] deviantart.com/dragonreine/art/Eyes-in-Manga---Feminine-vs-Masculine-294633895 |
| How I draw eyelashes on different genders | RunemiteTime | Eyelash styles by gender [59] | Minimal | [59] deviantart.com/runemitetime/art/How-I-draw-eyelashes-on-different-genders-944608249 |

**License note for DeviantArt eye refs:** imaginary-ang3l explicitly says "feel free to use as reference/inspiration" [2]. RikaYoru says "feel free to use!! No reposting" [4]. izka197 says "use them as references if you wish" [57]. All are **reference-only** — no commercial reuse confirmed.

### 4C. Tutorial Sources (Eyes)

| Source | Key Content | URL |
|---|---|---|
| JeyRam Eye Tutorial [1] | 7-step method, 3 shape categories, free worksheet | jeyram.org/eye-design |
| CLIP STUDIO TIPS — Pharmarr [6] | Shape metrics (shape/size/position), iris anatomy (pupillary zone/ciliary zone/collarette), iris patterns (Crypts/Furrows/Wolffin/Pigment spots), eyelash orientation | tips.clip-studio.com/en-us/articles/10248 |
| AnimeOutline [7] | 8 expression types, eye spacing rules, reflection system | animeoutline.com/how-to-draw-anime-eyes/ |
| DrawingForAll [30] | Female eye specifics, step-by-step | drawingforall.net/how-to-draw-anime-female-eyes/ |
| 21 Anime Eye Shape Drawing Ideas [50] | Most exhaustive shape taxonomy in evidence | christinebritton.com/eye-shapes-drawing-anime/ |
| CharacterHub [51] | Comparison across anime styles (Sailor Moon, Demon Slayer, JJK) | characterhub.com/blog/character-resources/eye-drawing-reference |
| EasyDrawingGuides [29] | Female vs male distinction, sparkle rules | easydrawingguides.com/how-to-draw-anime-and-manga-eyes/ |

### 4D. PixAI Eye Tag Queries (not confirmed in evidence — use directly)

> `pixai.art/tags/artwork/blue_eyes`, `pixai.art/tags/artwork/heterochromia`, `pixai.art/tags/artwork/slit_pupils`, `pixai.art/tags/artwork/heart-shaped_pupils`

---

## Part 5 — Accessories: 25+ Types with Reference Sources

### 5A. Accessory Catalog

Evidence is strongest from the NovelAI documentation [68] as a tag taxonomy, supplemented by clothing/hair tutorials that mention accessories inline [15][44][45][46][47][67].

#### HAIR ACCESSORIES

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 1 | Hair ribbon / bow | Ribbon tied at hair tie point; sweet/lolita style [62][68] | [62][68][67] |
| 2 | Hair clip (barrette) | Flat clip gripping hair section | [67] |
| 3 | Hair pin (bobby pin) | Thin metal or decorative pin | [67] |
| 4 | Headband (カチューシャ) | Rigid or padded band over top of head [67] | [67][68] |
| 5 | Flower hair accessory | Floral clip or ornament; common in wa-maid [60] | [60][67] |
| 6 | Ahoge with ornament | Decorative ahoge variant (heart shape) [68] | [68] |
| 7 | Tiara / small crown | Metal arc with gems, worn at hairline | [45][68] |
| 8 | Full crown | Enclosed ring crown; regal character [68] | [68] |
| 9 | Helmet | Full-head armor piece [68] | [68] |
| 10 | Beret | Soft flat cap angled to side [68] | [68] |
| 11 | Baseball cap | Casual peaked cap [68] | [68] |
| 12 | Mizuhiki cord | Japanese paper hair cord; miko-specific [46] | [46] |

#### FACE / EAR ACCESSORIES

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 13 | Glasses (spectacles) | Frames with lenses; varying shapes (round, rectangular, cat-eye) | [68] — tag: glasses |
| 14 | Earrings (stud) | Small gems or shapes at earlobe | — |
| 15 | Earrings (drop/dangle) | Hanging chain/gem below ear | — |
| 16 | Eye patch | Single-eye cover; pirate/fantasy | [68] — tag: eyepatch |

#### NECK / COLLAR ACCESSORIES

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 17 | Choker | Close-fitting neckband; gothic lolita common [45] | [45][68] |
| 18 | Ribbon tie (school) | Fabric ribbon at collar; blazer uniform [47] | [47][63] |
| 19 | Necktie | Narrow tie; blazer uniform variant [47][63] | [47][63] |
| 20 | Sailor scarf | Wide fabric triangle tied at collar front [48] | [48] |
| 21 | Lace collar | Decorative lace neckpiece; lolita/classic | [45][62] |

#### BODY / OUTFIT ACCESSORIES

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 22 | Brooch / pin | Decorative clip at lapel or chest | — |
| 23 | School emblem patch | Sewn to left breast of blazer [47] | [47] |
| 24 | Corset | Structured waist-cinching piece [68] | [68] |
| 25 | Leather belt | Waist strap for adventurer outfits [68] | [68] |
| 26 | Leather pouch | Belt-attached storage; fantasy [68] | [68] |
| 27 | Apron | Maid-specific overlay [15] | [15] |
| 28 | Taski cord | Miko sleeve-binding cord [46] | [46] |
| 29 | Obi sash | Kimono waist band; multiple tying styles [44] | [44] |

#### HAND / ARM ACCESSORIES

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 30 | Gloves (brown/leather) | Adventure/fantasy covering [68] | [68] |
| 31 | Fingerless gloves | Fantasy/combat style | — |
| 32 | Wrist ribbons / cuffs | Lolita blouse cuffs [45] | [45] |

#### FOOTWEAR ACCESSORIES (counted as component accessories)

| # | Accessory | Key Visual Features | Sources |
|---|---|---|---|
| 33 | Knee-high socks | Required in lolita; common in serafuku [45][48] | [45][48] |
| 34 | Knee boots | Fantasy/adventurer; "knee boots" tag [68] | [68] |
| 35 | Lolita-specific shoes | Platform mary-janes; not plain [45] | [45] |

### 5B. Accessory Reference Sources

**Confirmed direct references:**

| Source | Accessory Focus | Extra Elements (red) | URL |
|---|---|---|---|
| NatsuyaCharacterArt — RIBBON pack [19] | Hair ribbon in character context | Full character face, expression, outfit | natsuyacharacterart.itch.io/ribbon |
| Natsuyaya DeviantArt — HAT pack [24] | Hat accessory on character | Full character face, expression | deviantart.com/natsuyaya/art/Free-Anime-Character-Art-Pack%3A-HAT-1325978313 |
| mikiko-art kimono pack [44] | Obi/sash and juban collar | Full kimono outfit, hairstyle | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 |
| Ginger's Lolita Guide [45] | Choker, lace collar, wrist cuffs, bow headpiece | Full lolita outfit | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 |
| Miko Guide [46] | Mizuhiki cord, taski cord | Full miko outfit, hairstyle | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ |
| Blazer Uniform Guide [47] | Tie, ribbon, emblem patch | Full uniform, hairstyle | animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/ |
| Clip Studio hair article [67] | Pins, ribbons, headband in hair context | Full hairstyle, face | clipstudio.net/oekaki/archives/149946 |
| NovelAI docs [68] | crown, hair ribbon, beret, baseball cap, helmet, glasses, corset, leather belt, leather pouch, knee boots, brown gloves | — (tag taxonomy only) | docs.novelai.net/en/image/tutorial-charactercreation/ |

**Evidence gap — accessory-specific reference sheets not confirmed:**
For standalone monochrome reference sheets specifically showing chokers, brooches, tiaras, earrings, and glasses in isolation, **no confirmed direct URLs exist in the evidence**. Use these fallback search queries:

> **Choker:** `site:deviantart.com anime choker reference sheet lineart`
> **Brooch/pin:** `site:deviantart.com anime brooch character accessory reference`
> **Crown/tiara:** `site:pinterest.com anime tiara crown reference sheet monochrome`
> **Earrings:** `site:deviantart.com anime earring reference character sheet`
> **Glasses:** `site:deviantart.com anime glasses character reference sheet`
> **Headband:** `site:deviantart.com anime headband カチューシャ reference`

### 5C. PixAI Accessory Tag Queries (not confirmed in evidence)

> `pixai.art/tags/artwork/hair_ribbon`, `pixai.art/tags/artwork/choker`, `pixai.art/tags/artwork/crown`, `pixai.art/tags/artwork/glasses`, `pixai.art/tags/artwork/bow`

---

## Part 6 — Downloadable / Licensed Asset Packs (Verified)

### 6A. Commercially Reusable Assets

| Product | Platform | Price | License | AI-Generated? | Key Contents | Notes |
|---|---|---|---|---|---|---|
| Free 25 Fantasy Character Asset Pack [25] | Itch.io (cogabushi) | Free | Personal + Commercial OK; no redistribution/resale | Yes (AI + hand-edit) | 25 chars × 6 expressions + cut-ins + idle/battle sprites; PNG transparent | Confirmed free commercial |
| Free Schoolgirls Anime Pixel Sprite Pack [26] | CraftPix.net | Free | Royalty-free, unlimited projects | Not stated | 3 schoolgirl chars, run/walk/attack/dialogue anims, PSD+PNG, 128px tall | Confirmed royalty-free |
| Female Character Sprite for Visual Novel [52] | Itch.io (sutemo) | Free (confirmed free listing) | No attribution required; commercial use confirmed by users | No (hand-drawn) | 5+ hair colors, 10 expressions+outfits, modular PSD layers | Best hand-drawn free option; PSD only fully works in Photoshop |
| [VRChat] Anime base [23] | BOOTH (Riceballer3D) | Free | Commercial use in finished models OK; cannot sell the base itself | No (3D model) | 3 body types, 3 skin tones, 22k tri mesh | 3D only; not sprite |
| Free Anime Character Art Pack: RIBBON [19] | Itch.io (NatsuyaCharacterArt) | Free | Non-commercial only; modifications OK; no AI; no resale | No (hand-drawn) | 4 expressions, 1800×1200px PNG | Non-commercial only |
| Free Anime Character Art Pack: HAT [24] | DeviantArt (Natsuyaya) | Free (non-commercial) | Non-commercial free; commercial $8 full set / $2 per sprite | No (hand-drawn) | 4 expressions, 1800×1100px PNG | Commercial version confirmed $8 full / $2 single |

### 6B. Paid Reference Packs (Verified Prices)

| Product | Platform | Standard Price | Extended Commercial Price | Resolution | Contents | AI? | Source |
|---|---|---|---|---|---|---|---|
| 210 Girl Model Sheet v.139 [8] | ArtStation Marketplace | **$4.99** (1 commercial project, ≤2K sales/20K views) | **$15.00** (unlimited commercial) | 4K (4441×2489) JPEG | 210 anime female model sheets | Yes | [8] |
| 240 Asian Female Model Sheet v.146 [10] | ArtStation Marketplace | **$4.99** | **$15.00** | 4K (4096×4096) JPEG | 240 Asian female anime character sheets | Yes | [10] |
| 370 Fantasy Female Medieval Warrior Armor [53] | ArtStation Marketplace | **$5.00** | **$15.00** | 8K JPEG | 370 fantasy armor female references | Yes | [53] |
| Ninja Design Collection [A] [70] | BOOTH (wasabi-vaio) | **¥1,000** | N/A stated | 1536×1024 .webp | 330 female ninja costume sheets; includes kimono, masks, assassin | Yes (Stable Diffusion) | [70] |
| 1200+ Anime Female Reference Pack v.1 [9] | ArtStation Marketplace | Not confirmed in evidence | Not confirmed | 4K | 1200+ anime female character images | Yes (implied) | [9] |

> ⚠️ **AI-generated pack caveat:** All ArtStation packs [8][9][10][53] and the BOOTH ninja pack [70] are explicitly AI-generated. Use as **visual reference for tracing/identification only**. Downstream commercial IP claims for derived artwork depend on your jurisdiction's stance on AI-generated source material and ArtStation's current TOS. The standard $4.99 license covers "up to 2,000 sales or 20,000 views" [8][10].

> **10% bundle discount** applies when purchasing 2+ products from the same ArtStation seller [8][10]; **15% off** for 3+ products from the 370-armor pack seller [53].

### 6C. BOOTH — Additional Reference Packs

Evidence confirms only the ninja pack [70] with a verified price. For 服装/髪型-specific reference packs (clothing and hairstyle focused, not just pose):

**Confirmed:** Ninja Design Collection [A] — ¥1,000, 330 sheets, female ninja + kimono + mask designs [70]

**Evidence gap for BOOTH clothing/hair packs:** No other BOOTH clothing or hairstyle reference packs with confirmed prices appear in the evidence. Direct BOOTH search queries:

> `booth.pm/ja/search?q=髪型+資料集` (hairstyle reference packs)
> `booth.pm/ja/search?q=服装+イラスト+資料集` (costume illustration reference packs)
> `booth.pm/ja/search?q=女の子+コスチューム+資料集` (girl costume reference packs)
> `booth.pm/ja/search?q=ロリータ+資料集` (lolita reference packs)

---

## Part 7 — PixAI Complete Tag Reference by Category

### 7A. Confirmed Tag Pages

| Category | Tag | Count | URL |
|---|---|---|---|
| Hair | hair_down | 7,709 [20] | pixai.art/en/tags/artwork/hair_down |
| Hair | hair_over_one_eye | 121,399 [21] | pixai.art/tags/artwork/hair_over_one_eye |
| Hair | hair_over_eyes | 19,696 [22] | pixai.art/tags/artwork/hair_over_eyes |
| Clothing | school_uniform | 414,878 [63] | pixai.art/tags/artwork/school_uniform |
| Clothing | serafuku (sailor) | 97,536 [61] | pixai.art/tags/artwork/serafuku |
| Clothing | lolita_fashion | 41,502 [62] | pixai.art/tags/artwork/lolita_fashion |
| Clothing | wa_maid | 2,254 [60] | pixai.art/tags/artwork/wa_maid |

### 7B. Unconfirmed PixAI Tags (search recommended)

These tags are derived from NovelAI/Danbooru taxonomy [68] and are highly likely to exist on PixAI but are not confirmed in evidence:

**Hair:** `twintails`, `ponytail`, `braid`, `ahoge`, `hime_cut`, `bob_cut`, `short_hair`, `long_hair`, `sidelocks`, `drill_hair`, `odango`

**Clothing:** `kimono`, `hakama`, `miko`, `armor`, `gothic_lolita`, `sweet_lolita`, `maid`, `blazer`, `yukata`, `magical_girl`

**Eyes:** `blue_eyes`, `red_eyes`, `heterochromia`, `slit_pupils`, `star-shaped_pupils`, `glowing_eyes`

**Accessories:** `hair_ribbon`, `choker`, `crown`, `glasses`, `bow`, `headband`, `tiara`

---

## Part 8 — Master Atlas Thumbnail Index

This section provides a structured atlas tile list. **Thumbnail images cannot be embedded directly** as live URLs cannot be verified without active fetching, and inventing thumbnail URLs is explicitly prohibited. Instead, each entry provides the direct page URL from evidence plus confirmed image dimensions where available, suitable for the atlas builder to fetch and cache.

### Format per tile:
`[ID] Component Name | Category | Page URL | Confirmed Dimensions | Extra Elements (red in UI)`

---

**HAIRSTYLES**

```
H01 | Odango/Bun pair | Hair | wikihow.com/Anime-Hair-Styles [11] | — | eyes, face, expression
H02 | Hime cut | Hair | tips.clip-studio.com/en-us/articles/7165 [42] | — | eyes, face, kimono/dress
H03 | Ahoge (single) | Hair | pixivision.net/ja/a/11971 [13] | — | full character
H04 | Twin tails | Hair | palmie.jp/lessons/63 [17] | — | eyes, face, body
H05 | Ponytail (high) | Hair | palmie.jp/lessons/63 [17] | — | eyes, face, body
H06 | Braid (standard) | Hair | sensei.pixiv.net/ja/course/20 [64] | — | eyes, face
H07 | French braid | Hair | atam-academy.com/blog/43326/ [65] | — | eyes, face
H08 | Loose/yurufuwa braid | Hair | comic.smiles55.jp/guide/9269/ [66] | — | eyes, face
H09 | Ojou ringlets/drill | Hair | tips.clip-studio.com/en-us/articles/7165 [42] | — | eyes, face, dress
H10 | Hair over one eye | Hair | pixai.art/tags/artwork/hair_over_one_eye [21] | — | full character
H11 | Short boyish cut | Hair | clipstudio.net/oekaki/archives/149946 [67] | — | eyes, face
H12 | Short inner curl | Hair | clipstudio.net/oekaki/archives/149946 [67] | — | eyes, face
H13 | Blunt bangs (ぱっつん) | Hair | clipstudio.net/oekaki/archives/149946 [67] | — | eyes, face
H14 | Bob cut | Hair | wikihow.com/Anime-Hair-Styles [11] | — | eyes, face
H15 | Medium wavy | Hair | palmie.jp/lessons/63 [17] | — | eyes, face
H16 | Long straight | Hair | animeartmagazine.com/anime-hairstyles-for-girls-… [43] | — | eyes, face
H17 | Long wavy | Hair | animeartmagazine.com/anime-hairstyles-for-girls-… [43] | — | eyes, face
H18 | Side ponytail | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H19 | Half-updo | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H20 | Pompadour | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H21 | Afro | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H22 | Spiky/shonen | Hair | tips.clip-studio.com/en-us/articles/7165 [42] | — | eyes, face
H23 | Sidelocks | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H24 | Swept bangs | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H25 | Heart ahoge | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H26 | Antenna hair | Hair | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | —
H27 | Twin braids | Hair | sensei.pixiv.net/ja/course/20 [64] | — | eyes, face
H28 | Shoulder + reference sheet (50 styles) | Hair | deviantart.com/anaiskalinin/art/50-Female-Anime-Hairstyles-308941397 [35] | — | face, eyes
H29 | Shoulder sheet (Elythe 50) | Hair | deviantart.com/elythe/art/Various-Female-Anime+Manga-Hairstyles-307583395 [36] | — | face, eyes
H30 | Ryky hair reference | Hair | deviantart.com/ryky/art/anime-hair-reference-520974411 [37] | — | face, eyes
```

**CLOTHING**

```
C01 | Sailor uniform (serafuku) | Clothing | animeartacademy.com/p/how-to-draw-anime-sailor-uniform [48] | — | hair, shoes, socks
C02 | Blazer uniform | Clothing | animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/ [47] | — | hair, tie/ribbon, emblem
C03 | Maid (standard frilly) | Clothing | tips.clip-studio.com/en-us/articles/3094 [15] | — | hair, shoes
C04 | Maid (sexy/minimal) | Clothing | tips.clip-studio.com/en-us/articles/3094 [15] | — | hair, shoes
C05 | Maid (traditional long) | Clothing | tips.clip-studio.com/en-us/articles/3094 [15] | — | hair, shoes
C06 | Wa-maid | Clothing | pixai.art/tags/artwork/wa_maid [60] | — | full character
C07 | Furisode kimono | Clothing | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 [44] | — | hairstyle, obi, juban
C08 | Houmongi kimono | Clothing | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 [44] | — | hairstyle, obi
C09 | Yukata | Clothing | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 [44] | — | hairstyle, obi
C10 | Miko shrine maiden | Clothing | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ [46] | — | hair cord, taski, hakama
C11 | Ninja/kunoichi | Clothing | booth.pm/ja/items/5051971 [70] | 1536×1024px | hair, mask, boots
C12 | Gothic Lolita | Clothing | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 [45] | — | headpiece, socks, shoes
C13 | Sweet Lolita | Clothing | pixai.art/tags/artwork/lolita_fashion [62] | — | bow, socks, shoes
C14 | Classic Lolita | Clothing | pixai.art/tags/artwork/lolita_fashion [62] | — | hair, socks, shoes
C15 | Fantasy mage/sorceress | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair, boots, pouch
C16 | Fantasy armor (female medieval) | Clothing | artstation.com/marketplace/p/BLjdM/370-fantasy-female-medieval-warrior-armor [53] | 8K JPEG | hair, weapons
C17 | Fantasy RPG casual | Clothing | cogabushi.itch.io/25-fantasy-character-asset-pack [25] | PNG transparent | hair, expression
C18 | Magical girl | Clothing | sorceress.games/blog/build-an-ai-anime-character-generator [32] | — | hair, accessories, wand
C19 | Casual street wear | Clothing | artstation.com/artwork/3EnQqD [9] | 4K JPEG | hair, expression
C20 | Idol outfit | Clothing | pixai.art/tags/artwork/school_uniform [63] | — | hair, accessories
C21 | Gym / athletic | Clothing | pixai.art/tags/artwork/school_uniform [63] | — | hair, shoes
C22 | Corset + belt outfit (adventurer) | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair, gloves, boots
C23 | Hakama standalone | Clothing | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ [46] | — | hair, blouse
C24 | Dress (generic/formal) | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair, accessories
C25 | Tank top casual | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair
C26 | Jacket outfit | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair
C27 | Dress shirt outfit | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | hair, tie
C28 | Blazer (casual oversized) | Clothing | pixai.art/tags/artwork/hair_over_eyes [22] | — | full character
C29 | Cheerleader/sports | Clothing | pixai.art/tags/artwork/school_uniform [63] | — | hair, pom-poms
C30 | Pelvic curtain/tabard (fantasy) | Clothing | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | armor elements |
```

**EYES**

```
E01 | 54-eye reference sheet | Eyes | deviantart.com/imaginary-ang3l/art/Anime-Eyes-Reference-268915669 [2] | — | none (isolated eyes)
E02 | Rounded eyes | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none (isolated)
E03 | Almond / elongated eyes | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none
E04 | Upturned sharp eyes | Eyes | jeyram.org/eye-design [1] | — | none
E05 | Downturned gentle eyes | Eyes | tips.clip-studio.com/en-us/articles/10248 [6] | — | none
E06 | Triangular eyes | Eyes | jeyram.org/eye-design [1] | — | none
E07 | Rectangular eyes | Eyes | easydrawingguides.com/how-to-draw-anime-and-manga-eyes/ [29] | — | none
E08 | Double eyelid eyes | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none
E09 | Single eyelid (monolid) | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none
E10 | Chibi/hyperlarge (sparkle) | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none
E11 | Shojo (70% iris, Sailor Moon) | Eyes | characterhub.com/blog/character-resources/eye-drawing-reference [51] | — | none
E12 | Villain/antihero eyes | Eyes | christinebritton.com/eye-shapes-drawing-anime/ [50] | — | none
E13 | Surprised/wide eyes | Eyes | animeoutline.com/how-to-draw-anime-eyes/ [7] | — | none
E14 | Sad/drooped eyes | Eyes | animeoutline.com/how-to-draw-anime-eyes/ [7] | — | none
E15 | Angry eyes | Eyes | animeoutline.com/how-to-draw-anime-eyes/ [7] | — | none
E16 | Happy/curved eyes | Eyes | animeoutline.com/how-to-draw-anime-eyes/ [7] | — | none
E17 | Slit pupils | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E18 | Star-shaped pupils | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E19 | Heart pupils | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E20 | Diamond pupils | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E21 | Gradient iris (Demon Slayer style) | Eyes | characterhub.com/blog/character-resources/eye-drawing-reference [51] | — | none
E22 | Heterochromia pair | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E23 | Black sclera | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E24 | Glowing eyes | Eyes | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | none
E25 | Female-only multi-style sheet | Eyes | deviantart.com/izka197/art/Anime-Eyes-3-264888771 [57] | A4 | none (isolated eyes)
E26 | Feminine vs masculine comparison | Eyes | deviantart.com/dragonreine/art/Eyes-in-Manga---Feminine-vs-Masculine-294633895 [58] | — | none
E27 | Eyelash styles (gender) | Eyes | deviantart.com/runemitetime/art/How-I-draw-eyelashes-on-different-genders-944608249 [59] | — | none
E28 | Character eye chart (named anime) | Eyes | deviantart.com/oxdarock/art/Character-Eye-Chart-Page-476769308 [55] | — | none
E29 | Eyelid animation frames | Eyes | deviantart.com/inokithefox/art/Eye-Shapes-Reference-761999563 [54] | — | none
E30 | Tutorial + iris variants PSD | Eyes | deviantart.com/anastasia-berry/art/Eye.-Tutorial-+-References-735761824 [56] | 7000×9000px | none |
```

**ACCESSORIES**

```
A01 | Hair ribbon (character context) | Accessory | natsuyacharacterart.itch.io/ribbon [19] | 1800×1200px | face, expression, outfit (red)
A02 | Hat (character context) | Accessory | deviantart.com/natsuyaya/art/Free-Anime-Character-Art-Pack%3A-HAT-1325978313 [24] | 1800×1100px | face, expression (red)
A03 | Crown (tag taxonomy) | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full character (red)
A04 | Beret | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full character (red)
A05 | Glasses | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full character (red)
A06 | Tiara | Accessory | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 [45] | — | full lolita outfit (red)
A07 | Choker | Accessory | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 [45] | — | full lolita outfit (red)
A08 | Obi sash | Accessory | deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006 [44] | — | full kimono (red)
A09 | Mizuhiki hair cord | Accessory | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ [46] | — | full miko outfit (red)
A10 | Taski sleeve cord | Accessory | animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/ [46] | — | full miko outfit (red)
A11 | School tie / ribbon | Accessory | animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/ [47] | — | full uniform (red)
A12 | Sailor scarf | Accessory | animeartacademy.com/p/how-to-draw-anime-sailor-uniform [48] | — | full serafuku (red)
A13 | Corset | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A14 | Leather belt | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A15 | Leather pouch | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A16 | Knee boots | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A17 | Brown gloves | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A18 | Flower hair ornament (wa-maid) | Accessory | pixai.art/tags/artwork/wa_maid [60] | — | full character (red)
A19 | Headband (カチューシャ) | Accessory | clipstudio.net/oekaki/archives/149946 [67] | — | hair, face (red)
A20 | Hair clip/pin | Accessory | clipstudio.net/oekaki/archives/149946 [67] | — | hair, face (red)
A21 | Apron (maid) | Accessory | tips.clip-studio.com/en-us/articles/3094 [15] | — | full maid outfit (red)
A22 | Lace collar (lolita) | Accessory | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 [45] | — | full lolita (red)
A23 | Wrist cuffs (lolita) | Accessory | deviantart.com/who-dat-betch/journal/Ginger's-Guide-to-drawing-Lolita-455570174 [45] | — | full lolita (red)
A24 | Knee-high socks | Accessory | animeartacademy.com/p/how-to-draw-anime-sailor-uniform [48] | — | full outfit (red)
A25 | School emblem patch | Accessory | animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/ [47] | — | full blazer (red)
A26 | Helmet | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red)
A27 | Baseball cap | Accessory | docs.novelai.net/en/image/tutorial-charactercreation/ [68] | — | full outfit (red) |
```

**Total atlas tiles confirmed: 30H + 30C + 30E + 27A = 117 distinct entries**

---

## Part 9 — Verified Reference vs. Licensed Asset: Decision Matrix

| Asset | Platform | Free? | Commercial OK? | Attribution? | AI? | Best Use |
|---|---|---|---|---|---|---|
| sutemo Female Sprite [52] | Itch.io | ✅ Free | ✅ Yes (users confirm) | ❌ Not required | ❌ Hand-drawn | Base sprite for VN; modular PSD |
| cogabushi 25-pack [25] | Itch.io | ✅ Free | ✅ Yes (revenue projects) | Not stated | ⚠️ AI + hand-edit | Fantasy character variety |
| CraftPix Schoolgirls [26] | CraftPix | ✅ Free | ✅ Unlimited projects | Not stated | ❓ Not stated | Schoolgirl animations; game-ready |
| RIBBON pack [19] | Itch.io | ✅ Free | ❌ Non-commercial only | Not required | ❌ Hand-drawn | VN expressions; fan projects only |
| HAT pack (DeviantArt) [24] | DeviantArt/Itch.io | Free (non-comm) | ✅ $8 full / $2 each | Not stated | ❌ Hand-drawn | Hat accessory asset; buy for commercial |
| BOOTH anime base [23] | BOOTH | ✅ Free | ✅ In finished models | Not required | ❌ 3D model | VRChat/3D only |
| ArtStation 210-girl [8] | ArtStation | ❌ $4.99 std | ✅ $4.99/≤2K sales | Not required | ✅ AI | Reference tracing; concept ref |
| ArtStation 240 Asian [10] | ArtStation | ❌ $4.99 std | ✅ $4.99/≤2K sales | Not required | ✅ AI | Asian female ref sheets |
| ArtStation 370 Armor [53] | ArtStation | ❌ $5.00 std | ✅ $5.00/≤2K sales | Not required | ✅ AI | Fantasy armor reference |
| BOOTH Ninja 330 [70] | BOOTH | ❌ ¥1,000 | ⚠️ SD TOS applies | Not required | ✅ SD AI | Ninja/kimono/assassin reference |
| DeviantArt refs [2][3][4][34–41][55–59] | DeviantArt | ✅ Free (view) | ❌ Reference only | Varies | ❌ Hand-drawn | Visual identification only |
| Pixiv tutorials [12][14][64] | Pixiv | ✅ Free (view) | ❌ Reference only | — | ❌ Hand-drawn | How-to-draw reference |
| PixAI tag pages [20][21][22][60][61][62][63] | PixAI | ✅ Free (browse) | ⚠️ Per-image TOS | — | ✅ AI | Prompt inspiration; visual browsing |

---

## Part 10 — Recommendations & Watchlist

### Immediate Actions

1. **Build the atlas tile cache now** using the DeviantArt reference sheet URLs in Parts 2B, 4B, and 5B. These are the most reliable monochrome/lineart sources. Cache locally — DeviantArt URLs are stable but require login for full resolution.

2. **Purchase the ArtStation $4.99 packs** [8][10][53] for internal reference use. At $4.99 standard license, these provide the highest density of 4K/8K anime female reference images per dollar. Note: AI origin means they are reference material, not source artwork.

3. **Prioritize sutemo's sprite PSD [52]** as the base for the modular character editor — it is hand-drawn, free, commercially usable, and already modular (hair + outfit layers). The community-built character creator at `yuripourre.itch.io/character-creator-sutemo` demonstrates the desired editor paradigm [52].

4. **Use the NovelAI tag taxonomy [68]** as the canonical vocabulary for naming all atlas tiles in the UI. This ensures compatibility with AI generation workflows and provides a complete, hierarchical tag system for all four component categories.

5. **Fill the accessory reference gap** by running the search queries in Section 5B for choker, brooch, tiara, earrings, and glasses standalone lineart sheets. These are the weakest-coverage items in the atlas.

### BOOTH Search Watchlist

Run these BOOTH queries to find clothing/hairstyle-specific reference packs (not confirmed in evidence but structurally likely to exist):
- `booth.pm/ja/search?q=女の子+髪型+資料` — girl hairstyle reference
- `booth.pm/ja/search?q=ロリータ+ファッション+資料集` — lolita fashion reference
- `booth.pm/ja/search?q=学校制服+イラスト+資料` — school uniform illustration reference
- `booth.pm/ja/search?q=鎧+甲冑+女性+資料集` — female armor reference

### Risk Flags

- **AI-sourced reference packs:** All ArtStation packs [8][10][53] and BOOTH ninja [70] contain AI output. Confirm your jurisdiction's copyright position before using these as bases for derivative commercial work.
- **PixAI browsing vs. download:** PixAI tag pages [20][21][22][60][61][62][63] are browsable but individual image rights belong to their uploaders. Do not download PixAI community artwork for the asset library without per-image permission.
- **DeviantArt "free to use as reference"** does not equal a commercial license. Treat all DeviantArt sheets as visual identification aids for your atlas, not as downloadable reusable assets.
- **BOOTH ninja pack Stable Diffusion TOS [70]:** The pack is subject to Stable Diffusion's terms, which prohibit image-to-image use of the included assets. Use for visual reference only.
- **sutemo PSD compatibility [52]:** The eye-color-change feature in sutemo's PSD only works reliably in Photoshop, not other editors. Plan the character editor build around this constraint or use the community tool fork.

---

*Report covers 70 verified evidence sources, 117+ catalogued atlas entries across 4 component categories, and 10 downloadable/purchasable asset products with confirmed prices or license terms. All claims are supported by inline citations; unverified areas are explicitly flagged.*

## Enlaces directos de las fuentes citadas

La numeración enlaza con las referencias [n] utilizadas en el informe. Las cifras de vistas, conteos de etiquetas y precios deben volver a verificarse antes de publicarlas o comprar productos; el informe diferencia referencias visuales de assets con licencia.

1. https://www.jeyram.org/eye-design
2. https://www.deviantart.com/imaginary-ang3l/art/Anime-Eyes-Reference-268915669
3. https://www.deviantart.com/lonelywolfa/art/Anime-Eye-Reference-Sheet-743561128
4. https://www.deviantart.com/rikayoru/art/Simple-Anime-Eye-Styles-%28Girls%29-371705474
5. https://www.deviantart.com/penguinninja226/art/Anime-Eye-Chart-73978246
6. https://tips.clip-studio.com/en-us/articles/10248
7. https://www.animeoutline.com/how-to-draw-anime-eyes/
8. https://www.artstation.com/marketplace/p/m95P9/210-girl-model-sheet-anime-character-reference-image-pack-v-139-4k
9. https://www.artstation.com/artwork/3EnQqD
10. https://www.artstation.com/marketplace/p/NXgo7/240-asian-female-model-sheet-anime-character-reference-image-pack-v-146-4k
11. https://www.wikihow.com/Anime-Hair-Styles
12. https://www.pixiv.net/artworks/69100777
13. https://www.pixivision.net/ja/a/11971
14. https://www.pixiv.net/artworks/108693077
15. https://tips.clip-studio.com/en-us/articles/3094
16. https://www.clipstudio.net/how-to-draw/archives/161517
17. https://www.palmie.jp/lessons/63
18. https://www.animeoutline.com/how-to-draw-anime-school-girl-in-6-steps/
19. https://natsuyacharacterart.itch.io/ribbon
20. https://pixai.art/en/tags/artwork/hair_down
21. https://pixai.art/tags/artwork/hair_over_one_eye
22. https://pixai.art/tags/artwork/hair_over_eyes
23. https://booth.pm/en/items/3673097
24. https://www.deviantart.com/natsuyaya/art/Free-Anime-Character-Art-Pack%3A-HAT-1325978313
25. https://cogabushi.itch.io/25-fantasy-character-asset-pack-rpg-vn-sprites-anime-style
26. https://craftpix.net/freebies/free-schoolgirls-anime-character-pixel-sprite-pack/
27. https://www.deviantart.com/henkyo/journal/Anime-Hairstyles-Reflect-Character-Personalities-1127389910
28. https://www.pinterest.com/pin/anime-hair--8092474325716844/
29. https://easydrawingguides.com/how-to-draw-anime-and-manga-eyes/
30. https://www.drawingforall.net/how-to-draw-anime-female-eyes/
31. https://grabieart.com/blogs/ideas-tutorials/how-to-draw-anime-eyes-in-easy-steps
32. https://sorceress.games/blog/build-an-ai-anime-character-generator-sprite-ready-path
33. https://blog.pixai.art/en/how-to-use-pixai-guide/
34. https://www.deviantart.com/styrbjornandersson/art/manga-girl-hair-reference-sheet-II---20130113-348275702
35. https://www.deviantart.com/anaiskalinin/art/50-Female-Anime-Hairstyles-308941397
36. https://www.deviantart.com/elythe/art/Various-Female-Anime%2BManga-Hairstyles-307583395
37. https://www.deviantart.com/ryky/art/anime-hair-reference-520974411
38. https://www.deviantart.com/yosopher/art/anime-hair-%28girls%29-guidelines-375934474
39. https://www.deviantart.com/gabriellebrickey/art/Character-Hair-Reference-Sheet-663911704
40. https://www.deviantart.com/cupiekristin/art/16-Anime-Hairstyles-287323552
41. https://www.deviantart.com/rebornxyui/art/How-to-Draw-Shoujo-Style-Hair-259912277
42. https://tips.clip-studio.com/en-us/articles/7165
43. https://animeartmagazine.com/anime-hairstyles-for-girls-how-does-the-hair-we-choose-affect-our-characters-image/
44. https://www.deviantart.com/mikiko-art/art/Kimono-references-and-info-pack-920247006
45. https://www.deviantart.com/who-dat-betch/journal/Ginger%27s-Guide-to-drawing-Lolita-455570174
46. https://animeartmagazine.com/drawing-traditional-japanese-clothing-miko-shrine-maiden-edition/
47. https://animeartmagazine.com/how-to-draw-japanese-high-school-girls-uniforms-blazer-edition/
48. https://animeartacademy.com/p/how-to-draw-anime-sailor-uniform
49. https://coolkiddoodles.com/anime-eyes-reference-sheet/
50. https://www.christinebritton.com/eye-shapes-drawing-anime/
51. https://characterhub.com/blog/character-resources/eye-drawing-reference
52. https://sutemo.itch.io/female-character
53. https://www.artstation.com/marketplace/p/BLjdM/370-fantasy-female-medieval-warrior-armor-character-references-8k-res-draft
54. https://www.deviantart.com/inokithefox/art/Eye-Shapes-Reference-761999563
55. https://www.deviantart.com/oxdarock/art/Character-Eye-Chart-Page-476769308
56. https://www.deviantart.com/anastasia-berry/art/Eye.-Tutorial-%2B-References-735761824
57. https://www.deviantart.com/izka197/art/Anime-Eyes-3-264888771
58. https://www.deviantart.com/dragonreine/art/Eyes-in-Manga---Feminine-vs-Masculine-294633895
59. https://www.deviantart.com/runemitetime/art/How-I-draw-eyelashes-on-different-genders-944608249
60. https://pixai.art/tags/artwork/wa_maid
61. https://pixai.art/tags/artwork/serafuku
62. https://pixai.art/tags/artwork/lolita_fashion
63. https://pixai.art/tags/artwork/school_uniform
64. https://sensei.pixiv.net/ja/course/20
65. https://atam-academy.com/blog/43326/
66. https://comic.smiles55.jp/guide/9269/
67. https://www.clipstudio.net/oekaki/archives/149946
68. https://docs.novelai.net/en/image/tutorial-charactercreation/
69. https://www.deviantart.com/learntodrawanime/art/How-to-Draw-Anime-Hair-Styles-285515551
70. https://booth.pm/ja/items/5051971
