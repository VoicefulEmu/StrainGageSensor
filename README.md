# Strain Gauge Data Logging System

A complete embedded system for real-time strain gauge measurement using ESP32 and HX711 load cell amplifier.

## Overview

This project enables you to:
- ✓ Read strain gauges arranged in a Wheatstone bridge configuration
- ✓ Amplify readings using HX711 breakout board
- ✓ Process on ESP32 microcontroller
- ✓ Log data to CSV on your computer via serial connection
- ✓ Analyze measurements in Python/Excel

## Project Structure

```
StrainGageSensor/
├── firmware/
│   ├── strain_gauge_logger.ino    # ESP32 firmware
│   └── platformio.ini              # PlatformIO configuration
├── computer-app/
│   ├── strain_gauge_logger.py      # Python data logger
│   └── requirements.txt            # Python dependencies
├── docs/
│   ├── SETUP_GUIDE.md             # Detailed setup instructions
│   └── WIRING.md                  # Wiring diagrams (optional)
├── data/                           # CSV log files saved here
└── README.md                       # This file
```

## Quick Start

### Hardware Setup
1. Connect HX711 to ESP32:
   - HX711 DT → GPIO 25
   - HX711 SCK → GPIO 26
   - HX711 GND → GND
   - HX711 VCC → 3.3V

2. Connect Wheatstone bridge strain gauges to HX711

### Firmware Upload
1. Install PlatformIO in VS Code
2. Open `firmware/` folder
3. Click PlatformIO → Upload
4. Calibrate the HX711 (see SETUP_GUIDE.md)

### Start Logging
```bash
cd computer-app
python -m venv venv
venv\Scripts\activate  # Windows; use source venv/bin/activate on Linux
pip install -r requirements.txt
python strain_gauge_logger.py --port COM3
```

## Key Features

- **10 Hz Sampling Rate**: Configurable up to 100+ Hz
- **Averaged Readings**: 5-point averaging for noise reduction
- **CSV Format**: Easy analysis with Excel/Python/Pandas
- **Timestamped Data**: Millisecond precision from ESP32
- **Cross-platform**: Windows/Linux/Mac compatible
- **Calibration Support**: Easy weight-based calibration

## Data Files

Logged data is saved to `data/` folder in CSV format:
```
strain_gauge_20260304_143025.csv
```

Columns:
- Timestamp_ms: Milliseconds since ESP32 boot
- Weight_g: Calibrated weight measurement
- RawValue: Raw HX711 ADC value
- DateTime: ISO format timestamp

## Configuration

### Sampling Rate
Edit `firmware/strain_gauge_logger.ino` line 35:
```cpp
const int SAMPLE_RATE_MS = 100;  // 10 Hz (change to 50 for 20 Hz, etc)
```

### Noise Reduction
Increase averaging in line 39:
```cpp
const int NUM_AVERAGES = 5;  // Increase for less noise
```

### Calibration Factor
After calibration (see SETUP_GUIDE.md):
```cpp
const long CALIBRATION_FACTOR = 420.0;  // Update with your value
```

## Requirements

### Hardware
- ESP32 microcontroller board
- HX711 load cell amplifier
- Strain gauges (4x in Wheatstone bridge)
- USB cable for ESP32
- Jumper wires

### Software
- PlatformIO (for firmware)
- Python 3.6+ (for logger)
- pyserial library (installed via pip)

## Troubleshooting

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed troubleshooting.

Common issues:
- **Port not found**: Install CH340 USB driver
- **HX711 not ready**: Check GPIO connections
- **Noisy data**: Increase NUM_AVERAGES or shorten wiring

## Next Steps

1. **Visualization**: Plot CSV data with matplotlib
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt
   
   df = pd.read_csv('data/strain_gauge_20260304_143025.csv')
   plt.plot(df['Timestamp_ms'], df['Weight_g'])
   plt.show()
   ```

2. **Database**: Modify logger to use SQLite for large datasets

3. **Real-time Monitoring**: Add Flask web server for live dashboard

## References

- [HX711 Library](https://github.com/bogde/HX711)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Wheatstone Bridge Theory](https://en.wikipedia.org/wiki/Wheatstone_bridge)

## License

MIT License - Feel free to use and modify for your projects.

---

For detailed setup instructions, see [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
