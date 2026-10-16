"""Generate a KiCad 10 schematic and project-local symbols for the gate prototype.

Run: python generate_schematic.py
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parent
PROJECT = "turnstile-gate"
SHEET_UUID = "6a5b2643-c3c9-4e24-9ff4-8b6d21d2a321"


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def num(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def uid() -> str:
    return str(uuid4())


def snap(value: float) -> float:
    return round(value / 1.27) * 1.27


def font(size: float = 1.27) -> str:
    return f"(effects (font (size {num(size)} {num(size)})))"


def pin(name: str, number: str, side: str, index: int, width: float, height: float) -> tuple[str, float, float]:
    y = height / 2 - 7.62 - index * 5.08
    x = (-width / 2 - 5.08) if side == "L" else (width / 2 + 5.08)
    angle = 0 if side == "L" else 180
    part = (
        f'(pin passive line (at {num(x)} {num(y)} {angle}) (length 5.08) '
        f'(name {q(name)} {font(1.0)}) (number {q(number)} {font(1.0)}))'
    )
    return part, x, y


class Symbol:
    def __init__(self, name: str, ref_prefix: str, width: float, height: float, pins: list[tuple[str, str, str]]):
        self.name = name
        self.ref_prefix = ref_prefix
        self.width = width
        self.height = height
        self.pins = pins
        self.pin_positions: dict[str, tuple[float, float, str]] = {}

    def definition(self, embedded: bool) -> str:
        title = f"Turnstile:{self.name}" if embedded else self.name
        by_side = {"L": 0, "R": 0}
        pin_defs: list[str] = []
        for number, name, side in self.pins:
            part, x, y = pin(name, number, side, by_side[side], self.width, self.height)
            by_side[side] += 1
            self.pin_positions[number] = (x, y, side)
            pin_defs.append(part)
        ref_y = self.height / 2 + 3.81
        val_y = -self.height / 2 - 3.81
        return "\n".join(
            [
                f'(symbol {q(title)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
                f'  (property "Reference" {q(self.ref_prefix)} (at 0 {num(ref_y)} 0) {font()})',
                f'  (property "Value" {q(self.name)} (at 0 {num(val_y)} 0) {font()})',
                f'  (symbol {q(self.name + "_0_1")} (rectangle (start {num(-self.width/2)} {num(-self.height/2)}) '
                f'(end {num(self.width/2)} {num(self.height/2)}) (stroke (width 0.254) (type default)) (fill (type none))))',
                f'  (symbol {q(self.name + "_1_1")} ' + "\n    ".join(pin_defs) + ")",
                ")",
            ]
        )


symbols: dict[str, Symbol] = {
    "DC_Input": Symbol("DC_Input", "J", 30.48, 25.4, [("1", "+24V", "R"), ("2", "0V", "R")]),
    "Fuse": Symbol("Fuse", "F", 17.78, 12.7, [("1", "IN", "L"), ("2", "OUT", "R")]),
    "EStop_NC": Symbol("EStop_NC", "S", 25.4, 17.78, [("1", "COM", "L"), ("2", "NC", "R")]),
    "Relay_24V": Symbol("Relay_24V", "K", 35.56, 33.02, [("1", "COIL+", "L"), ("2", "COIL-", "L"), ("3", "CONTACT_IN", "R"), ("4", "CONTACT_OUT", "R")]),
    "Buck_24to5": Symbol("Buck_24to5", "U", 35.56, 33.02, [("1", "VIN+", "L"), ("2", "VIN-", "L"), ("3", "+5V", "R"), ("4", "GND", "R")]),
    "ESP32_DevKitC": Symbol("ESP32_DevKitC", "U", 53.34, 71.12, [
        ("1", "5V", "L"), ("2", "GND", "L"), ("3", "3V3", "L"), ("4", "GPIO16_RX", "L"),
        ("5", "GPIO17_TX", "L"), ("6", "GPIO32_IR", "L"), ("7", "GPIO33_HOME", "L"),
        ("8", "GPIO34_OPEN", "R"), ("9", "GPIO25_PWM", "R"), ("10", "GPIO26_DIR", "R"),
        ("11", "GPIO27_FLT", "R"),
    ]),
    "QR_SEN0486": Symbol("QR_SEN0486", "U", 35.56, 33.02, [("1", "VCC_3V3", "L"), ("2", "GND", "L"), ("3", "SDA_TX", "R"), ("4", "SCL_RX", "R")]),
    "HBridge_G2_24v30": Symbol("HBridge_G2_24v30", "U", 50.8, 50.8, [
        ("1", "VIN", "L"), ("2", "GND", "L"), ("3", "PWM", "L"), ("4", "DIR", "L"),
        ("5", "FLT", "R"), ("6", "OUTA", "R"), ("7", "OUTB", "R"),
    ]),
    "Motor_24V": Symbol("Motor_24V", "M", 30.48, 25.4, [("1", "A", "L"), ("2", "B", "L")]),
    "IR_ThroughBeam": Symbol("IR_ThroughBeam", "B", 48.26, 50.8, [
        ("1", "TX_+24V", "L"), ("2", "TX_0V", "L"), ("3", "RX_+24V", "L"),
        ("4", "RX_0V", "L"), ("5", "RELAY_COM", "R"), ("6", "RELAY_NO", "R"),
    ]),
    "Opto_PC817": Symbol("Opto_PC817", "U", 33.02, 30.48, [("1", "ANODE", "L"), ("2", "CATHODE", "L"), ("3", "EMITTER", "R"), ("4", "COLLECTOR", "R")]),
    "Limit_NC": Symbol("Limit_NC", "S", 27.94, 17.78, [("1", "COM", "L"), ("2", "NC", "R")]),
    "Resistor": Symbol("Resistor", "R", 20.32, 12.7, [("1", "1", "L"), ("2", "2", "R")]),
    "Capacitor": Symbol("Capacitor", "C", 20.32, 12.7, [("1", "+", "L"), ("2", "-", "R")]),
    "Flyback_Diode": Symbol("Flyback_Diode", "D", 25.4, 12.7, [("1", "K", "L"), ("2", "A", "R")]),
}


# Component placements and connected net for each pin number.
components: list[tuple[str, str, str, float, float, dict[str, str]]] = [
    ("J1", "DC_Input", "24V PSU EXTERNAL", 45, 60, {"1": "+24V", "2": "GND"}),
    ("F1", "Fuse", "MOTOR FUSE TBD", 120, 60, {"1": "+24V", "2": "F1_OUT"}),
    ("K1", "Relay_24V", "24V DC MOTOR RELAY", 220, 60, {"1": "K1_COIL_P", "2": "GND", "3": "F1_OUT", "4": "MOTOR24"}),
    ("U4", "HBridge_G2_24v30", "Pololu G2 24v30 CS", 380, 60, {"1": "MOTOR24", "2": "GND", "3": "PWM25", "4": "DIR26", "5": "FLT27", "6": "MOTOR_A", "7": "MOTOR_B"}),
    ("M1", "Motor_24V", "24V DC GEAR MOTOR", 535, 60, {"1": "MOTOR_A", "2": "MOTOR_B"}),
    ("D1", "Flyback_Diode", "COIL FLYBACK", 220, 122, {"1": "K1_COIL_P", "2": "GND"}),
    ("C1", "Capacitor", "470uF 50V", 380, 122, {"1": "MOTOR24", "2": "GND"}),
    ("F2", "Fuse", "CONTROL FUSE TBD", 120, 175, {"1": "+24V", "2": "CTRL24"}),
    ("S0", "EStop_NC", "E-STOP LATCH NC", 220, 175, {"1": "CTRL24", "2": "K1_COIL_P"}),
    ("U1", "Buck_24to5", "24V TO 5V DC-DC", 320, 175, {"1": "CTRL24", "2": "GND", "3": "+5V", "4": "GND"}),
    ("U2", "ESP32_DevKitC", "ESP32-WROOM DevKitC", 470, 185, {"1": "+5V", "2": "GND", "3": "+3V3", "4": "QR_TX", "5": "QR_RX", "6": "IR32", "7": "HOME33", "8": "OPEN34", "9": "PWM25", "10": "DIR26", "11": "FLT27"}),
    ("U3", "QR_SEN0486", "DFRobot SEN0486", 70, 315, {"1": "+3V3", "2": "GND", "3": "QR_TX", "4": "QR_RX"}),
    ("B1", "IR_ThroughBeam", "24V IR TX + RX", 205, 315, {"1": "CTRL24", "2": "GND", "3": "CTRL24", "4": "GND", "5": "IR_COM", "6": "GND"}),
    ("R1", "Resistor", "330R 0.5W", 305, 265, {"1": "+5V", "2": "OPTO_ANODE"}),
    ("U5", "Opto_PC817", "PC817", 365, 315, {"1": "OPTO_ANODE", "2": "IR_COM", "3": "GND", "4": "IR32"}),
    ("S1", "Limit_NC", "0 DEG HOME", 465, 315, {"1": "GND", "2": "HOME33"}),
    ("S2", "Limit_NC", "90 DEG OPEN", 545, 315, {"1": "GND", "2": "OPEN34"}),
    ("R2", "Resistor", "10k IR pullup", 275, 375, {"1": "+3V3", "2": "IR32"}),
    ("R3", "Resistor", "10k HOME pullup", 345, 375, {"1": "+3V3", "2": "HOME33"}),
    ("R4", "Resistor", "10k OPEN pullup", 415, 375, {"1": "+3V3", "2": "OPEN34"}),
    ("R5", "Resistor", "10k FLT pullup", 495, 375, {"1": "+3V3", "2": "FLT27"}),
]


def instance(ref: str, sym: Symbol, value: str, x: float, y: float) -> str:
    s_uuid = uid()
    props = [
        f'(property "Reference" {q(ref)} (at {num(x)} {num(y - sym.height/2 - 4.5)} 0) {font()})',
        f'(property "Value" {q(value)} (at {num(x)} {num(y + sym.height/2 + 4.5)} 0) {font(1.1)})',
    ]
    pin_uuids = " ".join(f'(pin {q(number)} (uuid {uid()}))' for number, _, _ in sym.pins)
    path = f"/{SHEET_UUID}"
    return (
        f'(symbol (lib_id {q("Turnstile:" + sym.name)}) (at {num(x)} {num(y)} 0) (unit 1) '
        f'(in_bom yes) (on_board yes) (dnp no) (uuid {s_uuid}) '
        + " ".join(props)
        + f' {pin_uuids} (instances (project {q(PROJECT)} (path {q(path)} (reference {q(ref)}) (unit 1)))))'
    )


def wire_label(x: float, y: float, side: str, net: str) -> tuple[str, str]:
    end_x = x - 5.08 if side == "L" else x + 5.08
    wire = (
        f'(wire (pts (xy {num(x)} {num(y)}) (xy {num(end_x)} {num(y)})) '
        f'(stroke (width 0) (type default)) (uuid {uid()}))'
    )
    # At the endpoint, the label text follows the short wire and stays outside the body.
    justify = "left bottom" if side == "R" else "left bottom"
    label = f'(label {q(net)} (at {num(end_x)} {num(y)} 0) (effects (font (size 1 1)) (justify {justify})) (uuid {uid()}))'
    return wire, label


def note(text: str, x: float, y: float, size: float = 1.3) -> str:
    return f'(text {q(text)} (at {num(x)} {num(y)} 0) (effects (font (size {num(size)} {num(size)}))) (uuid {uid()}))'


def main() -> None:
    defs = [symbol.definition(embedded=True) for symbol in symbols.values()]
    lib_defs = [symbol.definition(embedded=False) for symbol in symbols.values()]
    (ROOT / "Turnstile.kicad_sym").write_text(
        '(kicad_symbol_lib (version 20231120) (generator "codex")\n' + "\n".join(lib_defs) + "\n)\n",
        encoding="utf-8",
    )
    (ROOT / "sym-lib-table").write_text(
        '(sym_lib_table\n  (lib (name "Turnstile") (type "KiCad") (uri "${KIPRJMOD}/Turnstile.kicad_sym") (options "") (descr "Turnstile project symbols"))\n)\n',
        encoding="utf-8",
    )
    (ROOT / f"{PROJECT}.kicad_pro").write_text('{"meta":{"version":1}}\n', encoding="utf-8")

    items: list[str] = []
    for ref, sym_name, value, x, y, nets in components:
        x, y = snap(x), snap(y)
        sym = symbols[sym_name]
        items.append(instance(ref, sym, value, x, y))
        for pin_number, net in nets.items():
            px, py, side = sym.pin_positions[pin_number]
            wire, label = wire_label(x + px, y - py, side, net)
            items.extend((wire, label))

    items.extend(
        [
            note("TURNSTILE GATE - SCHEMATIC PROTOTYPE / 24 V DC / 1 LEAF 90 DEG", 250, 22, 2),
            note("External certified 24 V PSU and mains protection not shown. See README and BOM.", 255, 36),
            note("K1 is a prototype relay concept. Safety-rated architecture is required for public use.", 300, 150),
            note("B1 relay must close only when powered and beam clear. PC817 provides contact wetting current.", 300, 245),
            note("PIN NUMBERS ARE LOGICAL, NOT PHYSICAL HEADERS. Verify datasheets. No PCB footprints assigned.", 300, 405),
        ]
    )
    schematic = (
        f'(kicad_sch (version 20260306) (generator "codex") (generator_version "10.0") '
        f'(uuid {SHEET_UUID}) (paper "A2") '
        '(title_block (title "Turnstile Gate - Electrical Schematic") (rev "A") (company "Prototype") '
        '(comment 1 "ESP32 + UART QR + 24V motor + IR + limit switches")) '
        '(lib_symbols\n' + "\n".join(defs) + '\n)\n' + "\n".join(items)
        + f'\n(sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n'
    )
    (ROOT / f"{PROJECT}.kicad_sch").write_text(schematic, encoding="utf-8")


if __name__ == "__main__":
    main()
