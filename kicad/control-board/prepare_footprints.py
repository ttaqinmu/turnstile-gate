"""Copy the exact KiCad stock footprints used by this board into the project."""
from pathlib import Path
import glob
import shutil

ROOT = Path(__file__).resolve().parent
BASE = "/var/lib/flatpak/runtime/org.kicad.KiCad.Library.Footprints/x86_64/stable/active/files/footprints"
ITEMS = {
    "Connector_PinSocket_2.54mm": ["PinSocket_1x19_P2.54mm_Vertical"],
    "TerminalBlock_Phoenix": [
        "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        "TerminalBlock_Phoenix_MKDS-1,5-4-5.08_1x04_P5.08mm_Horizontal",
    ],
    "Package_DIP": ["DIP-4_W7.62mm"],
    "Resistor_THT": [
        "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
        "R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal",
    ],
    "MountingHole": ["MountingHole_3.2mm_M3"],
}

for lib, names in ITEMS.items():
    dest = ROOT / "footprints" / f"{lib}.pretty"
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        matches = glob.glob(f"{BASE}/{lib}.pretty/{name}.kicad_mod")
        if len(matches) != 1:
            raise RuntimeError(f"Footprint not uniquely found: {lib}:{name}, matches={matches}")
        shutil.copy2(matches[0], dest / f"{name}.kicad_mod")
print("Footprints copied")
