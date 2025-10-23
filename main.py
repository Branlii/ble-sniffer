#!/usr/bin/env python3
"""
BLE Sniffer - Bluetooth Low Energy Device Detection and Counting
==============================================================

A sophisticated BLE scanner that detects nearby Bluetooth devices, tracks them
in a sliding time window, and intelligently merges related devices (like iPhone
services and AirPods components) for cleaner output.

Features:
- Real-time BLE device detection with RSSI filtering
- Sliding time window for device presence tracking
- Smart device merging (iPhone + background services, AirPods components)
- Manufacturer and service identification
- Debug mode for detailed analysis
- Signal quality indicators

Usage:
    python3 main.py

Configuration:
    Edit config/settings.py to adjust scanning parameters, RSSI threshold,
    debug mode, and other settings.

Author: BLE Sniffer Team
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ble_scanner import BLEScanner
from config import settings


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="BLE Sniffer - Bluetooth Low Energy Device Detection and Counting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Coverage Distance Ranges:
  1m   : RSSI threshold -60 dBm (very close range)
  5m   : RSSI threshold -70 dBm (close range)
  10m  : RSSI threshold -80 dBm (medium range)
  20m  : RSSI threshold -90 dBm (far range)
  50m  : RSSI threshold -100 dBm (very far range)

Examples:
  python3 main.py --coverage 1m
  python3 main.py --coverage 10m --debug
  python3 main.py --debug
  python3 main.py
        """
    )
    
    parser.add_argument(
        '--coverage',
        type=str,
        choices=['1m', '5m', '10m', '20m', '50m'],
        help='Set coverage distance (1m, 5m, 10m, 20m, or 50m)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (show all BLE signals separately instead of merging related devices)'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point for the BLE sniffer application."""
    args = parse_arguments()
    
    # Update RSSI threshold based on coverage parameter
    if args.coverage:
        settings.RSSI_THRESHOLD = settings.COVERAGE_RANGES[args.coverage]
        print(f"📡 Coverage set to {args.coverage} (RSSI threshold: {settings.RSSI_THRESHOLD} dBm)")
    else:
        print(f"📡 Using default RSSI threshold: {settings.RSSI_THRESHOLD} dBm")
    
    # Update debug mode based on parameter
    if args.debug:
        settings.DEBUG_MODE = True
        print("🐛 Debug mode enabled - showing all BLE signals separately")
    else:
        print(f"🔍 Debug mode: {'enabled' if settings.DEBUG_MODE else 'disabled'}")
    
    scanner = BLEScanner()
    await scanner.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

import asyncio
import time
from collections import defaultdict, deque
from bleak import BleakScanner

# CONFIG
WINDOW_SEC = 10           # fenêtre glissante en secondes pour compter "présents"
PRINT_INTERVAL = 2        # intervalle d'affichage en secondes
RSSI_THRESHOLD = -40      # ignorer paquets dont RSSI < seuil (trop faibles / hors zone)
MIN_SAMPLES_PER_DEVICE = 1  # nombre minimum de détections d'un device dans la fenêtre pour le compter
DEBUG_MODE = False        # True = afficher tous les signaux BLE séparément, False = fusionner les appareils liés

# stockage: pour chaque device_id on garde timestamps des derniers sightings
sightings = defaultdict(deque)  # device_id -> deque([timestamps])
device_info = {}  # device_id -> {name, last_seen}

def now():
    return time.time()

def prune_old():
    cutoff = now() - WINDOW_SEC
    to_delete = []
    for dev, dq in list(sightings.items()):
        while dq and dq[0] < cutoff:
            dq.popleft()
        if not dq:
            to_delete.append(dev)
    for dev in to_delete:
        del sightings[dev]
        if dev in device_info:
            del device_info[dev]

def current_count():
    prune_old()
    # compter devices ayant au moins MIN_SAMPLES_PER_DEVICE dans la fenêtre
    return sum(1 for dq in sightings.values() if len(dq) >= MIN_SAMPLES_PER_DEVICE)

def get_manufacturer_name(manufacturer_data):
    """Identifier le fabricant à partir des données manufacturer"""
    if not manufacturer_data:
        return "Unknown"
    
    # Les ID de fabricants BLE les plus courants
    manufacturer_ids = {
        76: "Apple",           # 0x004C
        6: "Microsoft",        # 0x0006
        117: "Samsung",        # 0x0075
        224: "Google",         # 0x00E0
        89: "Qualcomm",        # 0x0059
        15: "Broadcom",        # 0x000F
        13: "Texas Instruments", # 0x000D
        25: "Nordic Semiconductor", # 0x0019
    }
    
    # Prendre le premier ID de fabricant trouvé
    first_id = next(iter(manufacturer_data.keys()))
    return manufacturer_ids.get(first_id, f"Unknown (ID: {first_id})")

def merge_related_devices():
    """Fusionner les appareils liés (iPhone + services, AirPods + case)"""
    if DEBUG_MODE:
        return device_info  # Mode debug: afficher tout séparément
    
    merged = {}
    iphone_devices = []
    airpods_groups = {}
    
    # Recalculer les RSSI actuels depuis les device_info actifs
    active_devices = {}
    for dev_id, info in device_info.items():
        if dev_id in sightings and len(sightings[dev_id]) >= MIN_SAMPLES_PER_DEVICE:
            active_devices[dev_id] = info
    
    for dev_id, info in active_devices.items():
        # Identifier les iPhones et services associés
        if info['manufacturer'] == 'Apple':
            if info['name'] != 'Unknown Device' and 'iPhone' not in info['name'] and 'AirPods' not in info['name']:
                # iPhone avec nom personnalisé
                iphone_devices.append((dev_id, info))
            elif info['name'] == 'Unknown Device':
                # Service iPhone anonyme
                iphone_devices.append((dev_id, info))
            elif 'AirPods' in info['name']:
                # Grouper les AirPods par nom
                airpods_name = info['name']
                if airpods_name not in airpods_groups:
                    airpods_groups[airpods_name] = []
                airpods_groups[airpods_name].append((dev_id, info))
            else:
                # Autre appareil Apple
                merged[dev_id] = info
        else:
            # Appareil non-Apple
            merged[dev_id] = info
    
    # Fusionner les appareils iPhone
    if iphone_devices:
        # Prendre l'iPhone avec un nom (pas "Unknown Device") comme principal
        main_iphone = None
        services_count = 0
        current_best_rssi = -100
        
        for dev_id, info in iphone_devices:
            if info['name'] != 'Unknown Device':
                main_iphone = (dev_id, info)
            services_count += 1
            # Utiliser le RSSI actuel, pas celui en cache
            current_rssi = info['last_rssi']
            if current_rssi > current_best_rssi:
                current_best_rssi = current_rssi
        
        if main_iphone:
            dev_id, info = main_iphone
            # Créer une entrée fusionnée pour l'iPhone
            merged_info = info.copy()
            merged_info['services_count'] = services_count
            merged_info['last_rssi'] = current_best_rssi  # RSSI mis à jour
            merged[dev_id] = merged_info
        else:
            # Tous sont "Unknown Device", prendre le premier
            dev_id, info = iphone_devices[0]
            merged_info = info.copy()
            merged_info['services_count'] = services_count
            merged_info['name'] = 'iPhone (services only)'
            merged_info['last_rssi'] = current_best_rssi  # RSSI mis à jour
            merged[dev_id] = merged_info
    
    # Fusionner les groupes AirPods
    for airpods_name, devices in airpods_groups.items():
        if devices:
            # Prendre le premier comme représentant du groupe
            main_dev_id, main_info = devices[0]
            components = []
            current_best_rssi = -100
            
            # Recalculer le meilleur RSSI actuel
            for dev_id, info in devices:
                current_rssi = info['last_rssi']
                if current_rssi > current_best_rssi:
                    current_best_rssi = current_rssi
            
            # Identifier les composants (case vs earbuds basé sur RSSI/pattern)
            if len(devices) == 1:
                components = ["Case"]
            elif len(devices) == 2:
                components = ["Case", "1 earbud"]
            elif len(devices) == 3:
                components = ["Case", "Left earbud", "Right earbud"]
            else:
                components = [f"{len(devices)} components"]
            
            merged_info = main_info.copy()
            merged_info['components'] = components
            merged_info['components_count'] = len(devices)
            merged_info['last_rssi'] = current_best_rssi  # RSSI mis à jour
            merged[main_dev_id] = merged_info
    
    return merged

def analyze_services(service_uuids):
    """Analyser les services BLE pour identifier le type d'appareil"""
    if not service_uuids:
        return "No services"
    
    # Services BLE standards
    known_services = {
        "0000180F-0000-1000-8000-00805F9B34FB": "Battery Service",
        "0000180A-0000-1000-8000-00805F9B34FB": "Device Information",
        "0000181B-0000-1000-8000-00805F9B34FB": "Body Composition",
        "0000110B-0000-1000-8000-00805F9B34FB": "Audio Sink",
        "0000110E-0000-1000-8000-00805F9B34FB": "A/V Remote Control",
        "74EC2172-0BAD-4D01-8F77-997B2BE0722A": "Apple Continuity",
        "D0611E78-BBB4-4591-A5F8-487910AE4366": "Apple Nearby",
        "89D3502B-0F36-433A-8EF4-C502AD55F8DC": "Apple Nearby Action",
    }
    
    services = []
    for uuid in service_uuids:
        uuid_str = str(uuid).upper()
        if uuid_str in known_services:
            services.append(known_services[uuid_str])
        else:
            services.append(f"Custom ({uuid_str[:8]}...)")
    
    return ", ".join(services)

def detection_callback(device, advertisement_data):
    # device.address or device.metadata may contain the id (mac or uuid-like)
    dev_id = device.address  # sur macOS, ce peut être un uuid fourni par CoreBluetooth
    rssi = advertisement_data.rssi
    if rssi is None:
        return
    if rssi < RSSI_THRESHOLD:
        # trop faible -> probablement hors zone
        return
    
    # Analyser les données détaillées
    device_name = device.name or "Unknown Device"
    manufacturer = get_manufacturer_name(advertisement_data.manufacturer_data)
    services = analyze_services(advertisement_data.service_uuids)
    
    # stocker les infos du device
    device_info[dev_id] = {
        'name': device_name,
        'last_rssi': rssi,
        'last_seen': now(),
        'manufacturer': manufacturer,
        'services': services,
        'tx_power': advertisement_data.tx_power,
        'connectable': getattr(advertisement_data, 'connectable', None)
    }
    
    # ajouter timestamp
    sightings[dev_id].append(now())

async def main():
    scanner = BleakScanner(detection_callback)
    print("Démarrage du scan BLE... (autoriser Bluetooth si demandé)")
    await scanner.start()
    try:
        last_print = 0
        while True:
            await asyncio.sleep(0.2)
            t = time.time()
            if t - last_print >= PRINT_INTERVAL:
                merged_devices = merge_related_devices()
                c = len(merged_devices)
                
                mode_indicator = " [DEBUG MODE]" if DEBUG_MODE else " [MERGED MODE]"
                print(f"\n[{time.strftime('%H:%M:%S')}] Count (fenêtre {WINDOW_SEC}s) = {c}  | total tracked ids = {len(sightings)}{mode_indicator}")
                
                # Afficher les devices détectés
                if merged_devices:
                    print("Devices detected:")
                    for dev_id, info in merged_devices.items():
                        print(f"  • {info['name']} (RSSI: {info['last_rssi']} dBm)")
                        print(f"    └─ Manufacturer: {info['manufacturer']}")
                        
                        if DEBUG_MODE:
                            # Mode debug: afficher tous les détails
                            print(f"    └─ Services: {info['services']}")
                            if info['tx_power'] is not None:
                                print(f"    └─ TX Power: {info['tx_power']} dBm")
                            print(f"    └─ ID: {dev_id[:8]}...")
                            
                            # Explication pour les appareils inconnus
                            if info['name'] == "Unknown Device":
                                if info['manufacturer'] == "Apple":
                                    print(f"    └─ 💡 Likely: iPhone/iPad background service or secondary BLE identity")
                                elif "Apple" in info['services']:
                                    print(f"    └─ 💡 Likely: Apple ecosystem feature (Handoff, AirDrop, etc.)")
                                else:
                                    print(f"    └─ 💡 Likely: Nearby smart device or wearable")
                        else:
                            # Mode fusionné: afficher les informations agrégées
                            if 'services_count' in info:
                                print(f"    └─ BLE Services: {info['services_count']} active")
                            if 'components' in info:
                                components_str = " + ".join(info['components'])
                                print(f"    └─ Components: {components_str}")
                            if not DEBUG_MODE:
                                print(f"    └─ ID: {dev_id[:8]}...")
                        print()
                else:
                    print("No devices detected in range")
                    
                last_print = t
    finally:
        await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
