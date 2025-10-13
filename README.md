# BLE Sniffer 🔍

A sophisticated Bluetooth Low Energy (BLE) device detection and counting system with intelligent device merging and real-time monitoring capabilities.

## 📋 Features

- **Real-time BLE scanning** with configurable RSSI filtering
- **Smart device merging** - Combines related devices (iPhone + background services, AirPods components)
- **Sliding time window** for accurate presence tracking
- **Manufacturer identification** for Apple, Samsung, Google, and more
- **Service analysis** to understand device capabilities
- **Debug mode** for detailed BLE signal analysis
- **Signal quality indicators** with emoji visualization
- **Clean, modular codebase** with proper separation of concerns

## 🚀 Quick Start

### Prerequisites

- Python 3.7+ 
- macOS, Windows, or Linux
- Bluetooth adapter with BLE support

### Installation

1. Clone or download the project:
   ```bash
   cd ble-sniffer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the scanner:
   ```bash
   python3 main.py
   ```

## ⚙️ Configuration

Edit `config/settings.py` to customize the scanner behavior:

```python
# Scanning Configuration
WINDOW_SEC = 10                     # Time window for device presence (seconds)
PRINT_INTERVAL = 2                  # Display update interval (seconds)
RSSI_THRESHOLD = -40                # Minimum signal strength (dBm)
MIN_SAMPLES_PER_DEVICE = 1          # Minimum detections to count device

# Display Configuration
DEBUG_MODE = False                  # True = show all BLE signals, False = merge devices
```

### RSSI Threshold Guide

- **-30 to -40 dBm**: Very close (1-3 meters) - devices on your person
- **-40 to -60 dBm**: Close (3-10 meters) - same room
- **-60 to -80 dBm**: Medium range (10-20 meters) - nearby rooms
- **-80+ dBm**: Far away - weak signals

## 📊 Output Modes

### Merged Mode (Default)
Shows logical devices with combined information:
```
[12:30:15] Count (fenêtre 10s) = 2 | total tracked ids = 4 [MERGED MODE]
Devices detected:
  • 😽clat (RSSI: -35 dBm) 📶 Very Good
    └─ Manufacturer: Apple
    └─ BLE Services: 2 active
    └─ ID: DE45E357...

  • AirPods a moi (RSSI: -36 dBm) 📶 Very Good
    └─ Manufacturer: Apple
    └─ Components: Case + Left earbud + Right earbud
    └─ ID: F1ECD569...
```

### Debug Mode
Shows all individual BLE signals with technical details:
```
[12:30:15] Count (fenêtre 10s) = 4 | total tracked ids = 4 [DEBUG MODE]
Devices detected:
  • 😽clat (RSSI: -35 dBm) 📶 Very Good
    └─ Manufacturer: Apple
    └─ Services: Device Information, Apple Continuity
    └─ TX Power: 12 dBm
    └─ ID: DE45E357...
```

## 🏗️ Project Structure

```
ble-sniffer/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                 # This file
├── config/                   # Configuration
│   ├── __init__.py
│   └── settings.py           # All settings and constants
├── src/                      # Main source code
│   ├── __init__.py
│   └── ble_scanner.py        # Core scanner class
├── models/                   # Data models
│   ├── __init__.py
│   └── device_manager.py     # Device tracking and management
└── utils/                    # Utility modules
    ├── __init__.py
    ├── ble_analyzer.py       # Device analysis and identification
    └── display.py            # Output formatting and device merging
```

## 🧠 Smart Device Detection

### iPhone Behavior
- **Primary identity**: Your iPhone's actual name (e.g., "😽clat")
- **Background services**: Anonymous "Unknown Device" for AirDrop, Handoff, etc.
- **Merged view**: Shows as one device with service count

### AirPods Behavior
- **Individual components**: Each AirPod + case has separate BLE radio
- **Progressive detection**: Case → Case + earbuds as they wake up
- **Merged view**: Shows as one device with component list

### Other Devices
- **Manufacturer identification**: Apple, Samsung, Google, Microsoft, etc.
- **Service analysis**: Battery, Audio, Device Information services
- **Signal quality**: Real-time RSSI with quality indicators

## 🔧 Usage Examples

### Basic Monitoring
```bash
python3 main.py
```

### Enable Debug Mode
1. Edit `config/settings.py`:
   ```python
   DEBUG_MODE = True
   ```
2. Run the scanner to see all individual BLE signals

### Adjust Detection Range
1. Edit `config/settings.py`:
   ```python
   RSSI_THRESHOLD = -30  # Only very close devices (1 meter)
   # or
   RSSI_THRESHOLD = -70  # Wider range (10+ meters)
   ```

## 🎯 Use Cases

- **Personal device tracking**: Monitor your iPhone, AirPods, smartwatch
- **Proximity detection**: Know when devices are very close (1-meter range)
- **BLE research**: Analyze Bluetooth advertising behavior
- **Smart home integration**: Detect when family members are home
- **Privacy analysis**: Understand what your devices broadcast

## 🔍 Understanding the Output

- **Count**: Number of unique logical devices detected
- **Total tracked IDs**: Raw number of BLE advertisement sources
- **RSSI**: Signal strength in dBm (closer to 0 = stronger)
- **Signal quality**: 📶 Excellent/Very Good/Good/Fair/Weak/Very Weak
- **Manufacturer**: Device brand (Apple, Samsung, etc.)
- **Services**: BLE capabilities the device advertises
- **Components**: For AirPods, shows which parts are active

## 🐛 Troubleshooting

### No devices detected
- Check Bluetooth is enabled
- Lower RSSI threshold (e.g., -80 dBm)
- Ensure devices are advertising (open Bluetooth settings on phone)

### Devices appear/disappear frequently
- This is normal BLE behavior
- Devices advertise intermittently to save battery
- AirPods only advertise when case is open

### "Unknown Device" entries
- Common for Apple devices using privacy features
- Shows background services (AirDrop, Handoff, Find My)
- Enable DEBUG_MODE for more details

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional manufacturer IDs
- More BLE service definitions
- Enhanced device type detection
- Performance optimizations

---

**Note**: This tool is for educational and personal use. Respect privacy and follow local regulations regarding Bluetooth scanning.