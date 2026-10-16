# Turnstile gate control PCB — rev A

[Open the KiCad layout](./control-board.kicad_pcb) · [Preview](./control-board-preview.svg) · [DRC report](./control-board-drc.txt)

This **115 × 95 mm**, two-layer PCB is a carrier for the **ESP32-DevKitC V4 with an ESP32-WROOM module**. It holds two 19-pin sockets, a PC817, a 330 Ω/0.5 W resistor, four 10 kΩ pull-ups, signal terminals, and four M3 mounting holes. PCB traces are 0.30 mm wide. An external buck converter supplies 5 V.

**The PCB carries only 5 V, 3.3 V, and signals.** The 24 V supply, fuses, emergency stop, power-cut relay, motor driver, power capacitor, motor, and IR sensor supply are installed in the panel according to the [system schematic](../turnstile-gate.kicad_sch). The PCB's IR terminal carries only the sensor's relay contact. Motor current does not flow through this PCB.

## PCB terminals

Read terminal pin numbers from the pin 1 marking on each footprint and the PCB top view. Do not infer wire order from the SVG preview alone; check pad numbers in KiCad before assembly.

| Terminal | Pin 1 | Pin 2 | Pin 3 | Pin 4 |
|---|---|---|---|---|
| J1 — external buck input | +5 V | GND | — | — |
| J2 — SEN0486 QR scanner | 3V3 | GND | scanner `SDA/TX` → GPIO16 | scanner `SCL/RX` ← GPIO17 |
| J3 — Pololu driver logic | GND | PWM/GPIO25 | DIR/GPIO26 | FLT/GPIO27 |
| J4 — IR relay | sensor `COM` | sensor `NO` | — | — |
| J5 — 0° NC limit | COM/GND | NC/GPIO33 | — | — |
| J6 — 90° NC limit | COM/GND | NC/GPIO34 | — | — |

The Pololu G2 24v30 CS driver's `SLP` connection is not required here because the driver module already pulls that pin up and enables it by default. Wire power `VIN`, power `GND`, `OUTA`, and `OUTB` directly at the driver/panel using conductors rated for the actual current.

## ESP32 and board components

- J7 = ESP32 `J2` socket per the [Espressif pin table](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html#header-block). Pin 1 `3V3`, 5 `GPIO34`, 7 `GPIO32`, 8 `GPIO33`, 9 `GPIO25`, 10 `GPIO26`, 11 `GPIO27`, 14 `GND`, 19 `5V`.
- J8 = ESP32 `J3` socket. Pins 1 and 7 are `GND`; pin 11 is `GPIO17`, and pin 12 is `GPIO16`.
- J7 and J8 have **25.40 mm** between rows. Check this against the [official DevKitC V4 dimensions](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf) and the physical module before fabrication. The WROVER version is unsuitable because it uses GPIO16/17 internally.
- Physical U5 PC817 pins: 1 anode, 2 cathode, **3 emitter/GND, 4 collector/GPIO32**. R1 is 330 Ω/0.5 W in series with the U5 LED. R2–R5 are 10 kΩ pull-ups to 3V3 for IR, HOME, OPEN, and FLT.
- J1 powers the ESP32 `5V` pin. Do not also power it over USB while J1 is live; [Espressif specifies one power source at a time](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html#power-supply-options).

## Checks and design limits

KiCad 10.0.7 DRC: **0 violations, 0 unconnected items**. This confirms that the layout rules and all defined nets are connected. This PCB does not yet have its own PCB schematic synchronised through *Update PCB from Schematic*. The [system schematic](../turnstile-gate.kicad_sch) also depicts panel components and uses logical module pin numbers. Cross-check all terminals against the table above before production.

Before ordering the PCB, print it at 1:1 scale and check the physical ESP32 and terminal blocks for size and orientation. Check USB and antenna clearance, socket height, component spacing, cable connectors, and M3 holes. The preview and DRC do not replace an assembly test. A public gate needs mechanical/electrical safety assessment and additional safety sensors; this control board is not a certified safety device.

## Regenerating the board

`prepare_footprints.py` copies stock KiCad footprints into the project. Run `generate_board.py`, then `route_board.py`, using Python with KiCad 10's `pcbnew` module. The `.kicad_pcb` file embeds its footprints and can be opened without the scripts; footprint copies are included so the generator can be rerun.
