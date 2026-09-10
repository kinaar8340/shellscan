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
| Face-degree paint on Goldberg T=7 is Caspar–Klug: 12 pentagons → pentamer, 60 hexagons → hexamer, 420 subunits. `capsid-t7-p22` vs `capsid-t7` is 1.0 (same paint). vs polyoma is \(12/72=1/6\): pentagons agree, hexagons do not. | **Model** + **Software fact**. Not a Hypothesis about organisms. |
| Larval setal maps / chrysalis hang / adult wing mosaics are low-frequency instances of the same schedule. | **Hypothesis** — visual rhyme, not a developmental proof |
| A digitized setal-position table (CSV) snapped to nearest Goldberg faces yields a `qga_pixel` field that can be compared, facewise, to a generative recipe on the same net. | **Hypothesis** (biology) + **Software fact** (snap + compare) |
| Open 13×36 cylinder: Hinton group order (`phi_order_ok`) holds through measured danaine, Heliconiini, and Papilionidae. Abdomen isolines; T1/T2 may walk one 10° bin. Atlas stop. | **Hypothesis (bounded)** |
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
| `capsid-t3-ms2.yaml` | (1,1) Class II | 3 | MS2 dimer (hexagon ≠ hexamer) | vs CK \(12/32=0.375\); 12 pentamer + 20 dimer |
| `capsid-t3-kite.yaml` | (1,1) Class II | 3 | kite / trimer (hexagon ≠ hexamer) | vs CK and MS2 kind \(12/32\); vs CK section 1.0 |
| `capsid-t3-rhomb30.yaml` | rhombille of (1,1) | 3 | all dimer / parabolic | F=90 V=92 E=180 χ=2; compare F=32 rejected |
| `capsid-t7.yaml` | (2,1) Class III | 7 | Caspar–Klug | 12 pentamers, 60 hexamers, 420 subunits |
| `capsid-t7-polyoma.yaml` | (2,1) Class III | 7 | all-pentamer | 72 pentamers painted, 360 subunits |
| `monarch-setal.yaml` | (3,0) Class I | 9 | setal table `setal/monarch.csv` | 4 tentacles from table; rings as bands |
| `tussock-setal.yaml` | (3,0) Class I | 9 | setal table `setal/tussock.csv` | 4 tufts + 1 rear horn |
| `setal-hinton.yaml` | (3,0) Class I | 9 | Hinton/Stehr named sites | 68 sites; SV/V collapse (`phi_order_ok` false) |
| `setal-hinton-cylinder.yaml` | open cylinder | — | Hinton sites, segment-indexed `u` | 13×36; `phi_order_ok` true |
| `setal-hinton-helicoid.yaml` | cylinder `twist=π` | — | inherit Hinton sites | chart order holds; embed shears |
| `setal-danaus-gilippus.yaml` | open cylinder | — | Hinton + A2 tubercles | 70 sites; order holds |
| `setal-plexippus-cylinder.yaml` | open cylinder | — | Scott Fig. 34 measured φ | D1 `σ_φ` 4.08° (one bin); order holds |
| `setal-melpomene-cylinder.yaml` | open cylinder | — | Scott Fig. 52 Heliconiini | SD ~78°; order holds |
| `setal-polyxenes-cylinder.yaml` | open cylinder | — | Scott Fig. 28 Papilionidae | extra-familial order holds |
| `capsid-t7-p22.yaml` | (2,1) Class III | 7 | VIPERdb P22 CK paint | vs `capsid-t7` kind 1.0; vs polyoma 0.167 |
| `capsid-t7-p22-portal.yaml` | (2,1) Class III | 7 | one pentagon = portal | vs CK \(71/72 \approx 0.986\); 11+60+1 |
| `capsid-t7-p22-1-2.yaml` | (1,2) Class III | 7 | P22 face-degree, 7d | occupancy 12+60; vs (2,1) kind \(68/72\) |

## Setal table (paint input)

A photograph is **digitized by hand** into CSV. Automatic vision is a different claim. Do not vendor JPEGs.

Chart: `s=0` anterior (`+z`), `s=1` posterior (`−z`); `phi_deg` around the body. Empty `phi_deg` on a `band` row paints a ring of faces whose `shell_s` is within `width`. Point sites (`seta`, `tuft`, `tentacle`, `spine`) snap to the nearest face centroid. Collisions: higher amplitude wins; logged in `setal_log.json`.

```
id,kind,segment,chart,s,phi_deg,amplitude,section,width,psi
ant-L,tentacle,T2,dorsal,0.04,25,1.0,parabolic,,
b0,band,T1,circumferential,0.10,,0.70,elliptic,0.08,
```

`kind` ∈ {seta, tuft, tentacle, band, spine}. `section` is one of the four inner_cone hues.

```
PYTHONPATH=scripts python3 -m recipe --name monarch-setal
PYTHONPATH=scripts python3 -m recipe compare monarch-setal banded-larva
```

Compare requires the same `(m,n)` / `T` / face count. It reports `section_agree` and `kind_agree` plus the two kind histograms. Self-compare is 1.0 (Software fact). Table vs `banded-larva` is a Hypothesis test: same 4 tentacles on the same net, not proof that Monarchs use a T=9 Goldberg.

Output extras: `painted.json`, `setal_log.json` (row → face, `snap_deg`).

## Hinton sites (cylinder unroll)

Primary chaetotaxy is a homology language on a cylinder (Hinton 1946 / Stehr 1987), not a Caspar–Klug capsid. `paint.mode: sites` still wraps onto the existing T=9 Goldberg so the wrap can be scored.

- Axial chart: segment order T1…A10 → `s`. Azimuth: `phi` from the middorsal line (left-side map).
- Groups lock the four-bin palette: XD/D elliptic, SD parabolic, L hyperbolic, SV/V flat-pockets. `gold` → parabolic. No fifth hue.
- `make recipe RECIPE=setal-hinton` then `python3 -m recipe score setal-hinton`.

Score (Hypothesis, except where tagged):

| Check | Meaning |
|---|---|
| `cluster_pure` | each homology group occupies one section — **Software fact** of the paint rule |
| `axial_hue_pure` | T1 vs A3 homologs (D1, SD1, L1, …) keep that section |
| `shell_s_range` on D1 | homologs differ in the axial coordinate |
| `phi_order_ok` | mean face-φ of D < SD < L < SV < V after wrap. **If this is false, T=9 scrambled the cylinder** — next carrier is an open helicoid/cylinder, not a fifth hue and not a silent T bump on the faceplate |

A9–A10 and species maps (Kitching *Danaus gilippus*, measured *D. plexippus* pinacula) reuse the same `sites:` list. Do not vendor photographs.

## Open cylinder chart

T=9 Goldberg closed the sphere and mixed SV with V. The next carrier is an **open cylinder** (`carrier.kind: cylinder`): 13 segment rings × `n_phi` azimuthal quads, no pentagons, no polar identification. `u` is the segment index. `twist` rotates the generators (helicoid); `twist: 0` is a circular cylinder.

Snap stays on the ring: exact segment, nearest unused φ bin. Homologs of D1 differ in `shell_s` (= `u`), not in φ. This is not a higher T on the faceplate and not a fifth hue.

```
make recipe RECIPE=setal-hinton-cylinder
PYTHONPATH=scripts python3 -m recipe score setal-hinton-cylinder
PYTHONPATH=scripts python3 -m recipe twist-scan setal-hinton-cylinder
make recipe RECIPE=setal-danaus-gilippus
```

Scored dumps: [docs/recipe-scores/](recipe-scores/). Faceplate stays frozen.

```
Hypothesis (bounded). Open 13×36 cylinder, snap = exact ring + nearest unused azimuth. Four-bin palette only.
  phi_order_ok holds for Hinton-nominal, D. gilippus, measured D. plexippus (Scott Fig. 34),
    Heliconiini-typical (Scott Fig. 52), and Papilio polyxenes (Scott Fig. 28).
  Abdomen homologs are isolines of chart φ; T1/T2 may walk one 10° bin.
  SD azimuth is tribe-shaped (47° danaine, 75–78° heliconiine/papilionid) and does not cross L on these plates.
  D1 σ_u = 0.2516 is the shared segment list.
  embed_phi_order_ok last true at π/4, first false at ~0.94 on plexippus.
Not claimed: larvae are this mesh; Fig. 52 is species-specific; a pierid was scored; field on γ(s).
Atlas stop. No pierid for completeness.
```

## Measured φ (*D. plexippus*, Scott 2020 Fig. 34)

Measured φ keeps order, replaces D1 `σ_φ` = 0 with ≤ one 10° bin, puts tentacles at 35° not 0°, embed bound unchanged. Same 13×36 cylinder, same snap. Do not compare this field to `banded-larva` (468 vs 92 faces). L2 φ by segment: T1 78°, T2/A3–A6 108°. The 12° L2 spread is an anterior T1 offset, not A7/A8; leave `n_phi = 36`.

```
make recipe RECIPE=setal-plexippus-cylinder
PYTHONPATH=scripts python3 -m recipe score setal-plexippus-cylinder
PYTHONPATH=scripts python3 -m recipe twist-scan setal-plexippus-cylinder
```

Filed: `docs/recipe-scores/setal-plexippus-cylinder.field.json`, `.homology.json`, `twist_scan_setal-plexippus-cylinder.json`.

## Heliconiini outgroup (Scott 2020 Fig. 52)

Typical Dione–Heliconius unroll (Fleming 1960 via Scott), same protocol, not a species-specific *H. melpomene* plate. `phi_order_ok` stays true: D 25° < SD 77.5° < L 116.5° < SV 144° < V 175°. D1 `σ_φ` chart = 0, `σ_u` = 0.2516. Embed bound unchanged (π/4 holds, π/2 fails). SD is ~30° more ventral than danaine SD (~47°) but does not cross L. Hypothesis widens to two nymphalid subfamilies (Danainae, Heliconiini), still not a theorem.

Plexippus L2 abdomen-only: T1 78° vs T2/A3–A6 108°; abdomen `std_phi_deg` → 0. Dense twist: `embed_phi_order_ok` last true at π/4, first false at 0.94. Same-net compare (468 faces): plexippus vs hinton `section_agree` 0.94 / `kind_agree` 0.93; vs gilippus 0.94 / 0.92.

```
make recipe RECIPE=setal-melpomene-cylinder
PYTHONPATH=scripts python3 -m recipe score setal-melpomene-cylinder
PYTHONPATH=scripts python3 -m recipe twist-scan setal-melpomene-cylinder
PYTHONPATH=scripts python3 -m recipe twist-scan setal-plexippus-cylinder --dense
PYTHONPATH=scripts python3 -m recipe compare setal-plexippus-cylinder setal-hinton-cylinder
PYTHONPATH=scripts python3 -m recipe compare setal-plexippus-cylinder setal-danaus-gilippus
```

## Extra-familial: *Papilio polyxenes* (Scott 2020 Fig. 28)

One papilionid unroll, then the atlas stops. Plate labels BD/BSD/BL/BSV; rows use Hinton D/SD/L/SV. `phi_order_ok` true: D 30° < SD 75° < L 103° < SV 125° < V 175°. SD ~75° matches Heliconiini, not danaine ~47°, and still does not reach L. D1 `σ_φ` 4.08° all-segments, 0° abdomen. Embed bound unchanged (π/4 yes, π/2 no). Compare vs plexippus (468 faces): section_agree 0.89 / kind_agree 0.89 (no tentacles; 37 setae vs 60).

```
make recipe RECIPE=setal-polyxenes-cylinder
PYTHONPATH=scripts python3 -m recipe score setal-polyxenes-cylinder
PYTHONPATH=scripts python3 -m recipe twist-scan setal-polyxenes-cylinder
PYTHONPATH=scripts python3 -m recipe compare setal-polyxenes-cylinder setal-plexippus-cylinder
```

Nymphalidae is a closed loop on this carrier. Atlas stop. No pierid for completeness.

## Capsid track (different claim family)

Closed 532, `(m,n)` / T, 12 pentagons. Not the cylinder. P22 did **not** add a new paint rule. It showed the two T=7 paints already shipped are the only two occupancy classes on that net.

Face-degree paint on a Goldberg T=7 net is Caspar–Klug: 12 pentagonal faces → pentamer, 60 hexagonal faces → hexamer, 420 subunits. Same `(2,1)`, same F=72, same 12+60 split. `capsid-t7-p22` vs `capsid-t7` is 1.0 / 1.0 — self-compare in all but name. **Software fact.**

vs polyoma is \(12/72 = 1/6 \approx 0.167\): the twelve pentagons agree (pentamer either way); the sixty hexagons do not (hexamer vs all-pentamer). That is CK locations vs polyoma/papilloma capsomer type on one net — the sentence this doc already had, now a number. **Software fact.**

Nothing in that pair is a Hypothesis about organisms. VIPERdb supplied the degree table; the mesh supplied the faces. Do not write it as if P22 “confirmed” T=7 in nature.

```
make recipe RECIPE=capsid-t7-p22
PYTHONPATH=scripts python3 -m recipe compare capsid-t7-p22 capsid-t7
PYTHONPATH=scripts python3 -m recipe compare capsid-t7-p22 capsid-t7-polyoma
```

Filed: `docs/recipe-scores/capsid-t7-p22.field.json`, `compare_t7_p22_t7.json`, `compare_t7_p22_polyoma.json`. Do not mesh snub/rhombitrihexagonal. Do not fold into `make scan`.

`(2,1)` and `(1,2)` are enantiomorphs (VIPERdb 7l / 7d). The `(2,1)` file does not swap them. `capsid-t7-p22-1-2` is the one-line swap of the P22 face-degree table onto `(1,2)`. Occupancy still 12+60 / 420. Face-index compare vs `(2,1)` is \(68/72 \approx 0.944\): same paint rule, hull order is not a 532 correspondence. **Model** + **Software fact**. Not a Hypothesis that 7d “is” P22.

```
make recipe RECIPE=capsid-t7-p22-1-2
PYTHONPATH=scripts python3 -m recipe compare capsid-t7-p22-1-2 capsid-t7-p22
```

Portal mark: `capsid-t7-p22-portal` paints one pentagon as `portal` (parabolic; four-bin, not a fifth hue). 11 pentamer + 60 hexamer + 1 portal. vs CK `kind_agree` \(71/72 \approx 0.986\) — one unique vertex, not the polyoma 0.167. Face-degree still cannot see the 12-fold portal geometry; this is a one-face flag. **Model** of the unique vertex + **Software fact** of \(1/72\). Not a Hypothesis that P22 “is” this mesh.

```
make recipe RECIPE=capsid-t7-p22-portal
PYTHONPATH=scripts python3 -m recipe compare capsid-t7-p22-portal capsid-t7
```

A later pass, if opened: mesh 30T rhombs or mixed papova 60+90 (new F). Not a fourth paint on F=32, not `make scan`.

## T=3 (catalog vs occupant)

Smallest net that can show both coincidence and disagreement. `(1,1)` Class II, GP(1,1), F=32, 12 pentagons + 20 hexagons, \(60T=180\). Topology unchanged: twelve pentagons still spend \(\chi=2\). Face-degree `capsid-t3` is the CK outline; it cannot prove which oligomer sits in a hexagon.

`capsid-t3-ms2`: hexagons painted `dimer` (parabolic), pentagons stay pentamer. Stoichiometry still 180; generator is the dimer (MS2 / \(\mathrm{TD}_t(1,1)\)). Goldberg face resolution, not 90 rhombs meshed. Compare vs CK at F=32: kind and section \(12/32=0.375\) — agree only on pentagons. Four bins, pentagons elliptic, hexagons parabolic instead of hyperbolic. **Model** + **Software fact**. Not a Hypothesis that MS2 “is” this mesh.

`capsid-t3-kite`: hexagons painted `trimer` (hyperbolic), pentagons elliptic. Laves dual of 3.4.6.4 at Goldberg resolution, not 60T kites meshed. vs CK: kind \(12/32\), section 1.0 (hexagons both hyperbolic). vs MS2: kind and section \(12/32\) (dimer/parabolic vs trimer/hyperbolic). Three paints, one catalog. pT=3 (VP1/VP2/VP3) stays closed.

`capsid-t3-rhomb30`: **one Laves dual meshed.** Edge-rhombille of GP(1,1): keep 60 parent verts, add 32 face centroids, one quad per parent edge. F=90, V=92, E=180, χ=2. All faces dimer/parabolic. 90 dimers, 180 subunits (not written into the 32-byte field). Index compare vs F=32 is rejected. Not a Hypothesis that the quads are MS2 Cα. Snub, floret, kite mesh, and papova 60+90 still counted only. T=7 30T=210 still unmeshed.

```
make recipe RECIPE=capsid-t3-rhomb30
```

```
make recipe RECIPE=capsid-t3-ms2
PYTHONPATH=scripts python3 -m recipe compare capsid-t3-ms2 capsid-t3
make recipe RECIPE=capsid-t3-kite
PYTHONPATH=scripts python3 -m recipe compare capsid-t3-kite capsid-t3
PYTHONPATH=scripts python3 -m recipe compare capsid-t3-kite capsid-t3-ms2
```

Pentagons remain the elliptic cells; hexagons are the remainder. The outline still cannot prove it captured the occupant. Butterfly rows stay on the cylinder. No \(S^3\) / \(\mathbb{RP}^3\) lift. No \(\gamma(s)\).

## This pass (closed)

| Track | Status | Label |
|---|---|---|
| Five cylinder scores (Hinton, gilippus, plexippus, Heliconiini, Papilio) | frozen | Hypothesis |
| Danaine same-net compares ~0.94 | frozen | Hypothesis |
| Extra-familial compare 0.89 | frozen | Hypothesis |
| T=7 P22 vs CK 1.0, vs polyoma 0.167 | frozen | Model + Software fact |
| T=7 one-face portal vs CK \(71/72\) | frozen | Model + Software fact |
| T=3 MS2-dimer vs CK \(12/32\) | frozen | Model + Software fact |
| T=3 kite-trimer vs CK and MS2 \(12/32\) | frozen | Model + Software fact |
| T=7 P22 (1,2) vs (2,1) occupancy 12+60, kind \(68/72\) | frozen | Model + Software fact |
| T=3 rhombille 30T F=90 χ=2 all-parabolic | frozen | Model + Software fact |
| Atlas / pierid / faceplate / \(\gamma(s)\) / snub mesh | off | — |

## Palette (do not invent a fifth)

Same four inner_cone hues as `docs/SPEC.md`: elliptic cyan, parabolic gold, hyperbolic orange, flat-pockets magenta. `rgb_preview` is a witness, not a pigment store.

## Freeze

Do not: grow a 33rd byte, fold this into `bin/shellscan.rs` or `pick`, instance geodesic orbs in `qga_gpu`, promote unfinished math into `flux_hopf_lib`, run automatic photograph segmentation, claim Goldberg polyhedra occur in lepidopteran development, re-prove clocks or nested shells as pictures, bind the field dump to `γ(s)`.

`qga_gpu` Class I stamp (`scene_core.rs`, default 2v → 80 faces) is a volume-bench object. This sidecar’s `(2,0)` geodesic matches those counts and then stops.

`wetware_printer` stays the tree/meristem analog. Do not collapse capsids into a fourth stylus there.

## Cited stills (external; not vendored)

- Hexagonal lattice + 12 pentagons: [Twarock & Luque 2019 Fig. 1](https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41467-019-12367-3/MediaObjects/41467_2019_12367_Fig1_HTML.png)
- Capsids by T-number: [JBC 2021 Fig. 5](https://www.jbc.org/cms/10.1016/j.jbc.2021.100554/asset/3a9964ff-0081-4028-806c-bea57b983e70/main.assets/gr5_lrg.jpg)
- 532 axes: [Alamy diagram](https://c8.alamy.com/comp/2JAYNMM/symmetry-variations-of-viral-icosahedron-capsid-three-types-of-icosahedron-capsid-twofold-threefold-and-fivefold-symmetry-2JAYNMM.jpg)
- Helicoid–catenoid: [VMM](https://virtualmathmuseum.org/Surface/helicoid-catenoid/helicoid-catenoid.html)
- Geodesic/Goldberg table: [Wikipedia](https://en.wikipedia.org/wiki/List_of_geodesic_polyhedra_and_Goldberg_polyhedra#Icosahedral)

The structure is a reusable schedule. It is not proof that every organism was designed this way.
