# Strain Gauge Data Logging System - Setup Guide

## Hardware Components
- **ESP32 Development Board** (e.g., ESP32 DOIT DevKit v1)
- **HX711 Load Cell Amplifier Breakout Board**
- **Strain Gauges** (4x for Wheatstone bridge configuration)
- **MicroSD card module / socket** (SPI interface)
- **MicroSD card** (formatted FAT32)
- **USB Cable** for ESP32 connection to computer
- **Jumper Wires**
- **Power Supply** (optional, if not using USB power)

## Wiring Diagram

### ESP32 to HX711
```
ESP32 Pin          HX711 Pin
---------          ---------
GPIO 25 (D25)  →   DT (Data)
GPIO 26 (D26)  →   SCK (Clock)
GND            →   GND
3.3V           →   VCC
```

### ESP32 to SD Card Module
```
ESP32 Pin      SD Module Pin
---------      -------------
3.3V            → VCC
GND             → GND
GPIO 18 (SCK)   → SCK
GPIO 23 (MOSI)  → MOSI
GPIO 19 (MISO)  → MISO
GPIO 5          → CS (chip select)
```

_You can move the CS pin to another GPIO if desired; just update `SD_CS_PIN` in the firmware._


### Strain Gauges to HX711
The HX711 is designed for load cells but works great with strain gauges in a Wheatstone bridge:
HX711 Connections:
- E+ (Excitation +) → Wheatstone bridge +5V
- E- (Excitation -) → Wheatstone bridge GND
- A+ (Signal +) → Bridge mid-point
- A- (Signal -) → Bridge mid-point (other side)
```

## Software Setup

### 1. ESP32 Firmware Setup (PlatformIO)

#### Using PlatformIO in VS Code:
1. Install PlatformIO IDE extension in VS Code
2. Open the `firmware/` folder as a workspace
3. The `platformio.ini` file is already configured for ESP32
   - the HX711 library is specified under `lib_deps`
   - no additional dependency is required for SD since it's part of the Arduino core
4. Connect the SD module and HX711 as shown in the wiring diagram
5. Insert a FAT32‑formatted microSD card into the module
6. Install dependencies: Click `PlatformIO` → `Build` → `Install`
7. Connect ESP32 via USB
8. Upload: Click `PlatformIO` → `Upload`
9. Monitor: Click `PlatformIO` → `Monitor Serial`

Firmware now writes every sample to two places:
- serial output (same as before)
- a CSV file on the SD card (created at boot with a timestamped name)

The default CS pin for the SD card is GPIO 5; change `SD_CS_PIN` in `strain_gauge_logger.ino` if needed.

#### Troubleshooting:
- If upload fails, try holding the BOOT button during upload start
- Check Tools → Ports in Arduino IDE for the correct COM port
- Linux: May need to add user to dialout group: `sudo usermod -aG dialout $USER`

### 2. Calibration (IMPORTANT!)

Before logging real data, you must calibrate the HX711:

1. Upload the firmware
2. Open Serial Monitor (115200 baud)
3. The scale will auto-zero when powered on
4. Place a known weight on the sensor (e.g., 1000g)
5. Note the raw value displayed
6. Calculate: `CALIBRATION_FACTOR = known_weight / raw_value`
7. Update line in firmware: `const long CALIBRATION_FACTOR = YOUR_VALUE;`
8. Re-upload firmware

Example:
```
Known weight: 1000g
Raw value: 420000
CALIBRATION_FACTOR = 1000 / 420000 = 0.00238
```

### 3. Python Logger Setup

#### Step 1: Create Virtual Environment
```bash
cd computer-app
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Find Your Serial Port

**Windows:**
```bash
python strain_gauge_logger.py --list-ports
```

**Linux/Mac:**
```bash
ls /dev/tty.* # or /dev/ttyUSB*
```

#### Step 4: Run the Logger
```bash
python strain_gauge_logger.py --port COM3 --baud 115200
```

> **Tip:** this step is optional if you're already logging to the SD card.  Use the Python logger only when you want a live stream to the computer or want consolidated CSV files on the host.

Options:
- `--port COM3`: Your serial port (default: COM3)
- `--baud 115200`: Baud rate (default: 115200)
- `--output ../data`: Output directory for CSV files

### 4. Data Output Format

CSV files are saved with timestamp: `strain_gauge_20260304_143025.csv`

Columns:
- **Timestamp_ms**: Milliseconds since ESP32 boot
- **Weight_g**: Measured weight/force in grams (calibrated)
- **RawValue**: Raw ADC reading from HX711
- **DateTime**: Human-readable timestamp

Example data:
```csv
Timestamp_ms,Weight_g,RawValue,DateTime
1000,2.345,123456,2026-03-04T14:30:25.123456
1100,2.348,123500,2026-03-04T14:30:25.223456
1200,2.341,123400,2026-03-04T14:30:25.323456
```

## Sampling Rate Configuration

Default: 10 Hz (100ms between samples)

To change:
1. Edit `firmware/strain_gauge_logger.ino`
2. Line 35: `const int SAMPLE_RATE_MS = 100;` ← Change this
   - 50ms = 20 Hz
   - 100ms = 10 Hz
   - 200ms = 5 Hz
3. Recompile and upload

## Troubleshooting

### Serial port not found
- Ensure ESP32 is plugged in
- Install/update CH340 USB driver (most common for ESP32)
- Restart Arduino IDE

### HX711 "not ready" errors
- Check wiring connections
- Verify GPIO pins match firmware
- Try power cycling the ESP32

### Noisy measurements
- Add filtering: Increase `NUM_AVERAGES` in firmware (line 39)
- Shorten HX711 wiring
- Ensure proper electrical grounding
- Add 100nF capacitor across strain gauge input

### Data logging stops
- Check serial connection stability
- Reduce sampling rate (`SAMPLE_RATE_MS`)
- Reduce averaging (`NUM_AVERAGES`)

## Next Steps

1. **Real-time Visualization**: Use matplotlib or Processing to plot CSV data
2. **Database Storage**: Modify Python script to use SQLite instead of CSV
3. **Web Dashboard**: Use Flask/Django + chart.js for live monitoring
4. **Long-term Testing**: Monitor stability and drift over time

## References

- [HX711 Library Documentation](https://github.com/bogde/HX711)
- [ESP32 Pinout](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/hw-reference/esp32_devkitc.html)
- [Wheatstone Bridge Configuration](https://en.wikipedia.org/wiki/Wheatstone_bridge)
