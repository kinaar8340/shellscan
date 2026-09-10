"""Recipe sidecar — dynamics → carrier → Hopf wrap → paint.

Model of a generative schedule. Not a faceplate verb. Not a theorem of biology.
"""

from .archimedean import FAMILY_TABLE, family_counts, hex_class, triangulation_number
from .geodesic import geodesic_polyhedron
from .goldberg import goldberg_dual
from .helicoid_catenoid import associate_point, morph_aa

__all__ = [
    "FAMILY_TABLE",
    "associate_point",
    "family_counts",
    "geodesic_polyhedron",
    "goldberg_dual",
    "hex_class",
    "morph_aa",
    "triangulation_number",
]
