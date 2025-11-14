"""
Display utilities for BLE sniffer output and device merging logic.
"""

import time
from config import settings
from config.settings import WINDOW_SEC
from utils.ble_analyzer import get_signal_quality


def merge_related_devices(device_manager):
    """
    Fusionner les appareils liés (iPhone + services, AirPods + case).
    
    Args:
        device_manager: DeviceManager instance
        
    Returns:
        dict: Merged devices dictionary
    """
    active_devices = device_manager.get_active_devices()
    
    if settings.DEBUG_MODE:
        return active_devices  # Mode debug: afficher tout séparément
    
    merged = {}
    iphone_devices = []
    airpods_groups = {}
    
    for dev_id, info in active_devices.items():
        # Identifier les iPhones et services associés
        if info['manufacturer'] == 'Apple':
            # Check for AirPods (case-insensitive)
            device_name_lower = info['name'].lower()
            if 'airpod' in device_name_lower or 'beats' in device_name_lower:
                # Grouper les AirPods par nom
                airpods_name = info['name']
                if airpods_name not in airpods_groups:
                    airpods_groups[airpods_name] = []
                airpods_groups[airpods_name].append((dev_id, info))
            elif info['name'] != 'Unknown Device' and 'iPhone' not in info['name']:
                # iPhone avec nom personnalisé
                iphone_devices.append((dev_id, info))
            elif info['name'] == 'Unknown Device':
                # Service iPhone anonyme
                iphone_devices.append((dev_id, info))
            else:
                # Autre appareil Apple
                merged[dev_id] = info
        else:
            # Appareil non-Apple
            merged[dev_id] = info
    
    # Fusionner les appareils iPhone
    if iphone_devices:
        main_iphone = None
        services_count = 0
        current_best_rssi = -100
        
        for dev_id, info in iphone_devices:
            if info['name'] != 'Unknown Device':
                main_iphone = (dev_id, info)
            services_count += 1
            current_rssi = info['last_rssi']
            if current_rssi > current_best_rssi:
                current_best_rssi = current_rssi
        
        if main_iphone:
            dev_id, info = main_iphone
            merged_info = info.copy()
            merged_info['services_count'] = services_count
            merged_info['last_rssi'] = current_best_rssi
            merged[dev_id] = merged_info
        else:
            # Tous sont "Unknown Device", prendre le premier
            dev_id, info = iphone_devices[0]
            merged_info = info.copy()
            merged_info['services_count'] = services_count
            merged_info['name'] = 'iPhone (services only)'
            merged_info['last_rssi'] = current_best_rssi
            merged[dev_id] = merged_info
    
    # Fusionner les groupes AirPods
    for airpods_name, devices in airpods_groups.items():
        if devices:
            main_dev_id, main_info = devices[0]
            current_best_rssi = -100
            
            for dev_id, info in devices:
                current_rssi = info['last_rssi']
                if current_rssi > current_best_rssi:
                    current_best_rssi = current_rssi
            
            # Identifier les composants
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
            merged_info['last_rssi'] = current_best_rssi
            merged[main_dev_id] = merged_info
    
    return merged


def display_devices(device_manager):
    """
    Display detected devices with appropriate formatting.
    
    Args:
        device_manager: DeviceManager instance
    """
    merged_devices = merge_related_devices(device_manager)
    c = len(merged_devices)
    total_tracked = device_manager.get_total_tracked_count()
    
    mode_indicator = " [DEBUG MODE]" if settings.DEBUG_MODE else " [MERGED MODE]"
    print(f"\n[{time.strftime('%H:%M:%S')}] Count (fenêtre {WINDOW_SEC}s) = {c}  | total tracked ids = {total_tracked}{mode_indicator}")
    
    if merged_devices:
        print("Devices detected:")
        for dev_id, info in merged_devices.items():
            signal_quality = get_signal_quality(info['last_rssi'])
            print(f"  • {info['name']} (RSSI: {info['last_rssi']} dBm) {signal_quality}")
            print(f"    └─ Manufacturer: {info['manufacturer']}")
            
            if settings.DEBUG_MODE:
                _display_debug_info(dev_id, info)
            else:
                _display_merged_info(dev_id, info)
            print()
    else:
        print("No devices detected in range")


def _display_debug_info(dev_id, info):
    """Display detailed debug information for a device."""
    print(f"    └─ Services: {info['services']}")
    if info.get('tx_power') is not None:
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


def _display_merged_info(dev_id, info):
    """Display merged information for a device."""
    if 'services_count' in info:
        print(f"    └─ BLE Services: {info['services_count']} active")
    if 'components' in info:
        components_str = " + ".join(info['components'])
        print(f"    └─ Components: {components_str}")
    print(f"    └─ ID: {dev_id[:8]}...")