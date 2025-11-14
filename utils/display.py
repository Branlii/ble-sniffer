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
    Groups by device NAME to keep different devices separate.
    "Unknown Device" entries are merged together as background services.
    
    Args:
        device_manager: DeviceManager instance
        
    Returns:
        dict: Merged devices dictionary
    """
    active_devices = device_manager.get_active_devices()
    
    if settings.DEBUG_MODE:
        return active_devices  # Mode debug: afficher tout séparément
    
    merged = {}
    device_groups = {}  # Group devices by name
    unknown_devices = []  # Collect all "Unknown Device" entries
    
    for dev_id, info in active_devices.items():
        if info['manufacturer'] == 'Apple':
            device_name_lower = info['name'].lower()
            
            if info['name'] == 'Unknown Device':
                # Collect all unknown devices - we'll merge them later
                unknown_devices.append((dev_id, info))
            elif 'airpod' in device_name_lower or 'beats' in device_name_lower:
                # Grouper les AirPods par nom (e.g., "Airpod à moi")
                device_name = info['name']
                if device_name not in device_groups:
                    device_groups[device_name] = []
                device_groups[device_name].append((dev_id, info))
            else:
                # Named Apple device (iPhone, iPad, etc.) - group by exact name
                device_name = info['name']
                if device_name not in device_groups:
                    device_groups[device_name] = []
                device_groups[device_name].append((dev_id, info))
        else:
            # Appareil non-Apple - add directly without merging
            merged[dev_id] = info
    
    # Merge all "Unknown Device" entries into a single group
    # These are background services from various Apple devices
    if unknown_devices:
        # Use the first one as the main entry
        main_dev_id, main_info = unknown_devices[0]
        current_best_rssi = -100
        
        # Find best RSSI among all unknown devices
        for dev_id, info in unknown_devices:
            current_rssi = info['last_rssi']
            if current_rssi > current_best_rssi:
                current_best_rssi = current_rssi
        
        merged_info = main_info.copy()
        merged_info['services_count'] = len(unknown_devices)
        merged_info['last_rssi'] = current_best_rssi
        merged[main_dev_id] = merged_info
    
    # Process each named device group
    for device_name, devices in device_groups.items():
        if not devices:
            continue
        
        # For named devices, we expect one main device
        # All others are services/components
        current_best_rssi = -100
        main_device = devices[0] if devices else None
        
        # Find best RSSI
        for dev_id, info in devices:
            current_rssi = info['last_rssi']
            if current_rssi > current_best_rssi:
                current_best_rssi = current_rssi
        
        if main_device:
            dev_id, info = main_device
            merged_info = info.copy()
            merged_info['services_count'] = len(devices)
            merged_info['last_rssi'] = current_best_rssi
            
            # Check if this is AirPods to show components
            if 'airpod' in device_name.lower() or 'beats' in device_name.lower():
                num_components = len(devices)
                if num_components == 1:
                    merged_info['components'] = ["Case"]
                elif num_components == 2:
                    merged_info['components'] = ["Case", "1 earbud"]
                elif num_components == 3:
                    merged_info['components'] = ["Case", "Left earbud", "Right earbud"]
                else:
                    merged_info['components'] = [f"{num_components} components"]
                merged_info['components_count'] = num_components
            
            merged[dev_id] = merged_info
    
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