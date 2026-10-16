# Turnstile gate hardware model

[Open the Blender model](../hardware.blend)

The model was built in Blender 5.2 using metres. Open `hardware.blend`, select `Camera | service-side isometric`, and inspect frames **1–128**:

- Frame 1: the gate leaf is closed at 0°.
- Frames 48–80: the leaf opens and remains at 90°.
- Frame 128: the leaf returns to 0°.

The 24 V DC motor, gearbox, 14-tooth pinion, 40-tooth output gear, and splined shaft sleeve sit **inside the lower beam**. The motor pinion drives the output gear attached to the leaf shaft; the visual gear ratio is 40:14. Two shaft bearings remain, one in the lower beam and one in the upper beam. The motor, gears, shaft sleeve, bearings, limit switches, and stops can be inspected and edited separately.

The `HOME 0°` and `OPEN 90°` objects represent end-position microswitches and mechanical travel stops. They are inside the lower beam. The former external `mark` labels have been removed. Switch actuation remains a visual concept.

The **QR scanner** retains its earlier shape above the frame, including its optical window, lens, illumination LEDs, status indicator, and `QR SCAN` label. A reflective IR module sits **inside the upper beam**, with its emitter and receiver behind one flush window on the lane-facing side. The control PCB is still a **visual placeholder**. The IR geometry illustrates placement; it does not establish detection performance. The electrical schematic currently specifies a separate through beam sensor, so the final sensor architecture must be reconciled before fabrication.

The frame extends **along the walking direction** and has an open centre. It is about **0.90 m long**, **0.38 m wide** across the upper and lower beams, and **1.23 m high**. Both end uprights use the same material as the shell and overlap the beams so the exterior reads as one frame. Their profiles remain narrower than the beams to clear the leaf throughout its 90° swing. The gear housing is integrated into the lower beam, with no separate exterior gear box. Two short clamps hold the clearer glass leaf, and the service panel is flush with the outside face of the lower beam. To inspect the mechanism, hide the `10 Lower enclosure shell` and `09 Removable gear cover` collections in Blender.

Mesh checks at frames 1, 12, 24, 36, 48, 80, and 128 found no intersection between the moving leaf and the frame or mechanism covers. Dimensions, tooth profiles, clearances, bearings, and motor torque are still visual assumptions. This model is neither a fabrication drawing nor proof of safety; verify physical components and calculations before building the gate.

Procedural source: [build_hardware.py](./build_hardware.py). Running it rebuilds the scene from scratch and overwrites `hardware.blend`.
