# Ticket turnstile gate electrical component plan

**Version:** 16 October 2026  
**Scope:** one lane, one leaf swinging 0–90°, ESP32, QR scanner, 24 V DC gearmotor, and an IR beam for passage detection.  
**Currency:** Indonesian rupiah (IDR). Prices are **indicative per-item prices** observed on product pages during research, not quotations or stock guarantees. Rows marked **budget** are planning allowances, not seller prices.

This document follows the [wiring diagram](./wiring-turnstile-gate.svg) and [pin table](./README.md). The budget below covers **one prototype unit**. It excludes the frame, leaf, bearings, coupling, fabrication, AC installation, ticketing/backend, shipping, and import tax.

## Core BOM

| Ref. | Component / minimum specification | Example brand, type, and price source | Qty | Unit price | Total | Status |
|---|---|---|---:|---:|---:|---|
| PS1 | 24 V DC PSU, ≥14 A, overcurrent protection; verify it can handle motor starting current | [Mean Well LRS-350-24, 24 V 14.6 A](https://www.gmp-electric.com/products/power-supply-meanwell-lrs-350-24) | 1 | Rp435,000 | Rp435,000 | Listing |
| F1–F2 | Two DC fuses and holders: one for the motor, one for control. Final ratings depend on motor current and wire size | Example [30 A blade fuse holder](https://heksagonal.net/holder-housing-rumah-fuse-blade-sekring-tancap-kecil-besar-balikpapan/) and fuses sized for the design | 1 set | Rp80,000 | Rp80,000 | Budget |
| K1 | 24 V DC coil power relay, NO contact with a **DC rating** above measured running/starting current; includes socket and coil diode | Prototype-class example: [Autovision 24 V 40 A](https://www.blibli.com/p/autovision-relay-kaki-4-pin-24v-40a-960w-original-untuk-pasang-klakson-lampu-led-watt-tinggi-pada-truk-barang/ps--AUE-70070-01325), relay listing Rp23,900 | 1 set | Rp50,000 | Rp50,000 | Budget; **not a safety relay** |
| S0 | Latching mushroom emergency stop, NC contact | [Schneider Harmony XB5AT842](https://www.gmp-electric.com/products/schneider-harmony-xb5-emergency-stop-mushroom-push-button-xb5at842-xb5as8442-xb5at42-xb5es542) | 1 | Rp156,000 | Rp156,000 | Rounded listing price |
| U1 | 24 V → 5 V buck converter, ≥2 A output; set and measure 5.0 V before connecting the ESP32 | [9–35 V → 5 V buck module](https://shopee.co.id/DC-DC-Step-Down-9-35V-24V-12V-to-5V-5A-Buck-Convert-055L-Super-LM2596-i.421203311.29766637237) | 1 | Rp49,000 | Rp49,000 | Listing; prototype |
| U2 | ESP32-DevKitC / DevKit V1 based on **ESP32-WROOM-32**, with GPIO16/17 available and a board-level 5 V input | [DOIT ESP32 DevKit V1, 30 pins](https://shopee.co.id/ESP32-ESP-32-Devkit-V1-Board-30-Pin-ESP-32S-DOIT-Wifi-Bluetooth-IOT-i.40647041.25513065308) | 1 | Rp79,000 | Rp79,000 | Listing; check actual board pinout |
| U3 | 2D QR scanner, 3.3 V UART, <70 mA | [DFRobot Gravity SEN0486](https://www.blibli.com/p/gravity-ring-2d-qr-code-scanner/ps--ITE-70030-00215); [manufacturer specifications](https://wiki.dfrobot.com/sen0486/) | 1 | Rp845,000 | Rp845,000 | Listing; verify genuine SKU |
| U4 | H-bridge for a 24 V brushed DC motor, 3.3 V logic input, PWM/DIR/FLT, continuous current ≥ motor current | [Pololu G2 24v30 CS #5692](https://www.pololu.com/product/5692), manufacturer price **US$74.95**; temporary IDR allowance before shipping/import tax | 1 | Rp1,600,000 | Rp1,600,000 | **Budget**; no verified local price |
| M1 | 24 V brushed DC gearmotor with gearbox/shaft suited to the leaf; torque, RPM, duty cycle, and stall current **must be calculated** | Price example: [24 V 100 W / 50 rpm worm gearmotor at Rp2,000,000](https://shopee.co.id/DC-Motor-Type-Worm-Gear-24V-100W-Ratio-1-30-50Rpm-i.175905248.14302813745) (sold-out listing); another [24 V worm gearmotor listing with several variants at Rp2,353,000](https://shopee.co.id/12V-24V-80W-90W-100W-120W-150W-30RPM-70RPM-DC-Worm-Gear-Motor-DC-Geared-Motor-Copper-Gear-i.1408217927.43129050956) | 1 | Rp2,200,000 | Rp2,200,000 | **Budget**; final specification undecided |
| B1 | IR **through beam** transmitter and receiver, 24 V DC supply, relay output; select a mode in which the relay is energised when the path is clear | [Omron E3JK-TR14-C 2M](https://www.fa.omron.co.jp/product/item/E3JK-TR14-C_2M/en/) (infrared, 5 m, relay). Similar local product using **visible red light**: [E3JK-TR12-C at Rp681,000](https://www.gmp-electric.com/products/photo-electric-sensor-omron-e3jk-tr12-c-through-beam-5m-ac-dc-braket) | 1 set | Rp900,000 | Rp900,000 | **Budget** for IR variant; request a local quote |
| S1–S2 | Roller limit switches with COM/NC terminals for the 0° and 90° positions | [Shemsco TZ-8108](https://www.gmp-electric.com/products/limit-switch-tz-8108-shemcso) | 2 | Rp77,000 | Rp154,000 | Listing |
| U5 | PC817 optocoupler + 330 Ω/0.5 W resistor + 3–4 10 kΩ pull-ups + perfboard/terminal | Example [PC817 module](https://cncstorebandung.com/product/pc817-4-channel-2ch-optocoupler-opto-coupler-isolation-board/) at Rp8,500 (check the module's resistor values); allowance covers the complete circuit | 1 set | Rp60,000 | Rp60,000 | Budget |
| C1 | Bulk capacitor near the driver; start with 470 µF/50 V low-ESR, then adjust for cable length and driver datasheet | Example [470 µF/50 V capacitor](https://store.ichibot.id/product/470uf-50v-capacitor-kapasitor-470-uf-50-v-electrolytic-komponen/) | 1 set | Rp30,000 | Rp30,000 | Budget |
| P1 | Metal panel enclosure, at least IP55 in a sheltered location, about 40 × 30 × 20 cm; allow room for wiring and PSU ventilation | [Fort FMBO403020, 40 × 30 × 20 cm, IP55](https://www.blibli.com/p/box-panel-listrik-outdoor-40x30x20-topi-2-sisi-ip55-fort-fmbo403020/ps--DEE-70391-00033) | 1 | Rp406,000 | Rp406,000 | Listing; choose another type if a wet location needs IP65 |
| W1 | Motor/control wiring, terminal blocks, ferrules, cable glands, DIN rail, PE lug, wire labels | [Cable gland example](https://www.blibli.com/jual/cabel-gland); select conductor sizes from actual current and run length | 1 lot | Rp300,000 | Rp300,000 | Budget |
| A1 | AC input protection and connections for the PSU: suitable MCB, PE terminal, power cable, and strain relief | [2P 6 A MCB example](https://berkahelectric.com/produk/general-produk/produk-lainnya/acti9-ic60h-2p-6a-d-miniature-circuit-br/); final rating depends on the installation | 1 lot | Rp200,000 | Rp200,000 | Budget; installation by an electrician |

**Materials subtotal:** Rp7,544,000  
**20% contingency (prices/stock/small parts):** Rp1,509,000  
**Suggested prototype budget cap:** **Rp9,053,000**

This is not a price estimate for a complete, ready-to-use turnstile. The **motor** and **driver** have the largest effect on cost and may change after load testing. U4's manufacturer price in USD was not converted directly; Rp1.6 million is a purchasing/import allowance that must be checked when ordering.

## Decisions to settle before purchasing

1. **Leaf size and performance:** establish length, weight, shaft offset, 90° swing, opening/closing time, people per hour, and manual-release method. With direct drive, 90° in 0.75–1.5 seconds corresponds to roughly 10–20 rpm at the output shaft; a linkage ratio can change this. Measure torque and starting/stall current before selecting M1, PS1, U4, F1, K1, and cable sizes.
2. **Sensor arrangement:** one B1 beam detects only one line across the passage. For a public gate, define sensing of the full swing area, force/speed limits, pinch protection, and the safety system after a risk assessment. A generic 12–24 V beam [listed at Rp100,000](https://www.blibli.com/p/sensor-infrared-beam-12-24v-waterproof-sensor-pengaman-otomatis-pintu-gerbang-otomatis-infra-merah/ps--PRB-70152-00016) may be used for bench tests, but its response and failure behaviour need verification before it can protect people. The Blender model shows a reflective sensor in the upper beam rather than this BOM's through beam pair; choose and validate one architecture before fabrication.
3. **Sensor contact to ESP32:** the Omron E3JK relay series specifies a **5 V DC, 10 mA** minimum contact load; a GPIO pull-up at 3.3 V/10 kΩ supplies only about 0.33 mA. U5 therefore uses a 5 V supply, a 330 Ω resistor, and a PC817 optocoupler. Confirm that `COM-NO` **closes only while the beam is received and the sensor is powered**. If B1 loses power or its cable breaks, GPIO32 must become HIGH. [Omron E3JK datasheet](https://www.ia.omron.com/data_pdf/cat/e3jk_e432-e1_8_6_csm1012459.pdf?id=3179)
4. **A cheaper driver is not a drop-in substitute:** [BTS7960/IBT-2](https://digiwarestore.com/id/driver-modules/motor-driver-bts7960-h-bridge-43a-713514.html) is listed at about Rp119,400, but its 5 V interface and control pins differ from U4. Substitution requires new wiring, logic-level tests, current protection, and thermal measurements. A listing's “43 A” figure does not establish continuous capacity inside an enclosure.
5. **Power loss and emergency stop:** design a safe state and manual release. The automotive relay K1 and ESP32 control in this BOM are prototype concepts. Public use requires a qualified designer to select components and the safety architecture.

## Procurement sequence

1. Measure the mechanics and select a motor from actual torque, RPM, and current requirements.
2. Establish motor current, then jointly select the PSU, H-bridge, fuses, DC relay/contactor, and cable sizes.
3. Order the ESP32, scanner, IR beam, two limit switches, buck converter, and interface components.
4. Assemble the panel; test QR scanning, every sensor, and the motor **without the leaf** first.
5. Test with the leaf: 0°/90°, sensor failure, broken cable, emergency stop, power loss, mechanical jam, and a person crossing before allowing users through.
