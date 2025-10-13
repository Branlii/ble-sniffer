"""
Configuration settings for the BLE sniffer application.
"""

# Scanning Configuration
WINDOW_SEC = 10                     # fenêtre glissante en secondes pour compter "présents"
PRINT_INTERVAL = 2                  # intervalle d'affichage en secondes
RSSI_THRESHOLD = -40                # ignorer paquets dont RSSI < seuil (trop faibles / hors zone)
MIN_SAMPLES_PER_DEVICE = 1          # nombre minimum de détections d'un device dans la fenêtre pour le compter

# Display Configuration
DEBUG_MODE = False                  # True = afficher tous les signaux BLE séparément, False = fusionner les appareils liés

# BLE Manufacturer IDs
MANUFACTURER_IDS = {
    76: "Apple",                    # 0x004C
    6: "Microsoft",                 # 0x0006
    117: "Samsung",                 # 0x0075
    224: "Google",                  # 0x00E0
    89: "Qualcomm",                 # 0x0059
    15: "Broadcom",                 # 0x000F
    13: "Texas Instruments",        # 0x000D
    25: "Nordic Semiconductor",     # 0x0019
}

# Known BLE Service UUIDs
KNOWN_SERVICES = {
    "0000180F-0000-1000-8000-00805F9B34FB": "Battery Service",
    "0000180A-0000-1000-8000-00805F9B34FB": "Device Information",
    "0000181B-0000-1000-8000-00805F9B34FB": "Body Composition",
    "0000110B-0000-1000-8000-00805F9B34FB": "Audio Sink",
    "0000110E-0000-1000-8000-00805F9B34FB": "A/V Remote Control",
    "74EC2172-0BAD-4D01-8F77-997B2BE0722A": "Apple Continuity",
    "D0611E78-BBB4-4591-A5F8-487910AE4366": "Apple Nearby",
    "89D3502B-0F36-433A-8EF4-C502AD55F8DC": "Apple Nearby Action",
}