# Recipe sidecar — dynamics → carrier → wrap → paint

**Not a faceplate verb.** `make scan` is still the only unfrozen loom target. This sidecar writes `output/recipe/<name>/`, never `output/pick/qga_pixel.bin`, never `γ(s)`.

A recipe is a generative schedule. It is **not** a theorem that organisms are designed this way.

## Claims

| Sentence | Label |
|---|---|
| Helicoid and catenoid form an associate family of minimal surfaces. The VMM chart with parameter `aa` interpolates them isometrically. | **Theorem** (cited: VMM / classical DG) |
| Icosahedral geodesic/Goldberg nets are parameterized by `(m,n)` with `T = m² + mn + n²`. Class I: one index vanishes. Class II: `m=n`. Class III: both nonzero and unequal. Dual: triangles ↔ 12 pentagons + `10(T−1)` hexagons. `V_geo = 10T+2`, `F_geo = 20T`. | **Theorem** (cited: Wenninger; Wikipedia list) |
| Caspar–Klug (1962): close a hexagonal lattice by 12 pentagons, preserving icosahedral 532. Particle has `60T` subunits, 12 pentamers, `10(T−1)` hexamers. Quasi-equivalence: same contact surfaces, slightly different geometry (flexible arms). | **Theorem** (cited) |
| Four Archimedean lattices contain a hexagonal sublattice and admit the CK close: hexagonal `6.6.6`, trihexagonal `3.6.3.6`, snub hexagonal `3⁴.6`, rhombitrihexagonal `3.4.6.4`. Their Laves duals are triangle / rhomb / floret / kite tiles. Dual counts: `20T` triangles, `30T` rhombs, `60T` florets, `60T` kites (Twarock & Luque 2019, Suppl. Table 5). | **Theorem** (cited: Nat Commun 10, 4414) |
| Hopf `S³→S²` and the 32-byte `QgaPixel` layout. | **Theorem** (Hopf) + **Software fact** (layout) |
| This crate compiles a recipe into a painted net and an `N×32` field dump. | **Model** + **Software fact** (counts, round-trip) |
| Larval setal maps / chrysalis hang / adult wing mosaics are low-frequency instances of the same schedule. | **Hypothesis** — visual rhyme, not a developmental proof |
| Two-clock interlacing on the faceplate will read the painted field as a living form. | **Out of scope.** Falsified at sculpture distance. Do not re-test on `γ(s)`. |

If a sentence cannot wear one of those tags, it does not belong here.

## Why virus capsids are the documented instance

Goldberg polyhedra are the geometric blueprint for icosahedral virus capsids. That is the strongest biological connection; clathrin coats are a more flexible pentagon-plus-hexagon family; pollen / radiolaria / diatoms rarely match a clean icosahedral Goldberg lattice.

Crick and Watson (1956): a small genome cannot encode a unique protein for every position. Icosahedral 532 (6 five-folds, 10 three-folds, 15 two-folds) plus a T-number is the default spherical solution. Helices package linear genomes (the helicoid carrier). Complex/binal forms combine modules (phage T4 prolate head). Those symmetries are not interchangeable.

Quasi-equivalence is the paint rule: one subunit type on pentamer and hexamer sites, with conformational give in the arms. Picornaviruses are geometrically T=3 but chemically pseudo-T=3 (VP1/VP2/VP3). Polyoma and papilloma place 72 pentamers on a T=7 lattice (360 subunits, not 420) — Caspar–Klug gets locations, not capsomer type. Viral tiling theory (Twarock) records dimer vs trimer bonds as rhombs and kites. The 2019 Archimedean-plus-dual list puts CK triangulations and VTT tiles in one family.

In recipe language:

1. Dynamics / function first (protect a genome, hang, twist, open).
2. Carrier: helicoid–catenoid parameter **or** `(m,n)` / T on one of the four hexagonal-containing Archimedean lattices.
3. Topological wrap: Euler characteristic, 12 pentagons of curvature, inverse-Hopf → `QgaPixel`.
4. Paint: pentamer vs hexamer (quasi-equivalence), or kite/rhomb class, or larval bands and tentacles.

v1 generates the hexagonal parent and its triangular dual (geodesic / Goldberg). The other six families are counted, not meshed.

## What `make recipe` does

CPU only. No Vulkan. No sibling checkout.

1. Load `recipes/*.yaml`.
2. Build the carrier net.
3. Paint faces (four-bin sections only).
4. Pack `output/recipe/<name>/qga_pixel_field.bin` (`N×32` bytes) plus JSON manifest.
5. Write `net.png`, `field_preview.png`, `morph.gif` (helicoid→catenoid, 8 frames).

Occupancy 256 is a faceplate number. Face count `10T+2` (Goldberg) is independent. Do not force `N == 256`. Do not bind the dump to `γ(s)`.

## Recipes shipped

| File | `(m,n)` | T | Paint | Software fact |
|---|---|---|---|---|
| `banded-larva.yaml` | (3,0) Class I | 9 | period-3 bands + 4 tentacles | F=92, 12 pentagons, 4 tentacles amp=1 |
| `hang-chrysalis.yaml` | (3,0) Class I | 9 | none, `morph_t=1` | same net; catenoid still |
| `capsid-t3.yaml` | (1,1) Class II | 3 | Caspar–Klug | 12 pentamers, 20 hexamers, 180 subunits |
| `capsid-t7.yaml` | (2,1) Class III | 7 | Caspar–Klug | 12 pentamers, 60 hexamers, 420 subunits |
| `capsid-t7-polyoma.yaml` | (2,1) Class III | 7 | all-pentamer | 72 pentamers painted, 360 subunits |

`(2,1)` and `(1,2)` are enantiomorphs. The T=7 file does not swap them.

## Palette (do not invent a fifth)

Same four inner_cone hues as `docs/SPEC.md`: elliptic cyan, parabolic gold, hyperbolic orange, flat-pockets magenta. `rgb_preview` is a witness, not a pigment store.

## Freeze

Do not: grow a 33rd byte, fold this into `bin/shellscan.rs` or `pick`, instance geodesic orbs in `qga_gpu`, promote unfinished math into `flux_hopf_lib`, ingest photographs, claim Goldberg polyhedra occur in lepidopteran development, re-prove clocks or nested shells as pictures.

`qga_gpu` Class I stamp (`scene_core.rs`, default 2v → 80 faces) is a volume-bench object. This sidecar’s `(2,0)` geodesic matches those counts and then stops.

`wetware_printer` stays the tree/meristem analog. Do not collapse capsids into a fourth stylus there.

## Cited stills (external; not vendored)

- Hexagonal lattice + 12 pentagons: [Twarock & Luque 2019 Fig. 1](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41467-019-12367-3/MediaObjects/41467_2019_12367_Fig1_HTML.png)
- Capsids by T-number: [JBC 2021 Fig. 5](https://www.jbc.org/cms/10.1016/j.jbc.2021.100554/asset/3a9964ff-0081-4028-806c-bea57b983e70/main.assets/gr5_lrg.jpg)
- 532 axes: [Alamy diagram](https://c8.alamy.com/comp/2JAYNMM/symmetry-variations-of-viral-icosahedron-capsid-three-types-of-icosahedron-capsid-twofold-threefold-and-fivefold-symmetry-2JAYNMM.jpg)
- Helicoid–catenoid: [VMM](https://virtualmathmuseum.org/Surface/helicoid-catenoid/helicoid-catenoid.html)
- Geodesic/Goldberg table: [Wikipedia](https://en.wikipedia.org/wiki/List_of_geodesic_polyhedra_and_Goldberg_polyhedra#Icosahedral)

The structure is a reusable schedule. It is not proof that every organism was designed this way.
