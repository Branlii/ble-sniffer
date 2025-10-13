"""
BLE analysis utilities for device identification and service analysis.
"""

from config.settings import MANUFACTURER_IDS, KNOWN_SERVICES


def get_manufacturer_name(manufacturer_data):
    """
    Identifier le fabricant à partir des données manufacturer.
    
    Args:
        manufacturer_data: Dictionary containing manufacturer data from BLE advertisement
        
    Returns:
        str: Manufacturer name or "Unknown" if not found
    """
    if not manufacturer_data:
        return "Unknown"
    
    # Prendre le premier ID de fabricant trouvé
    first_id = next(iter(manufacturer_data.keys()))
    return MANUFACTURER_IDS.get(first_id, f"Unknown (ID: {first_id})")


def analyze_services(service_uuids):
    """
    Analyser les services BLE pour identifier le type d'appareil.
    
    Args:
        service_uuids: List of service UUIDs from BLE advertisement
        
    Returns:
        str: Comma-separated list of service names
    """
    if not service_uuids:
        return "No services"
    
    services = []
    for uuid in service_uuids:
        uuid_str = str(uuid).upper()
        if uuid_str in KNOWN_SERVICES:
            services.append(KNOWN_SERVICES[uuid_str])
        else:
            services.append(f"Custom ({uuid_str[:8]}...)")
    
    return ", ".join(services)


def identify_device_type(device_name, manufacturer, services):
    """
    Identify device type based on name, manufacturer, and services.
    
    Args:
        device_name: Device name from BLE advertisement
        manufacturer: Manufacturer name
        services: Services string from analyze_services
        
    Returns:
        str: Device type description
    """
    if manufacturer == "Apple":
        if "AirPods" in device_name:
            return "Apple AirPods"
        elif device_name == "Unknown Device":
            if "Apple Continuity" in services or "Apple Nearby" in services:
                return "Apple Background Service"
            else:
                return "Apple Device (Hidden)"
        elif "iPhone" in device_name or "iPad" in device_name:
            return f"Apple {device_name}"
        else:
            return f"Apple Device ({device_name})"
    
    elif manufacturer == "Samsung":
        return f"Samsung Device ({device_name})"
    
    elif manufacturer == "Google":
        return f"Google Device ({device_name})"
    
    else:
        return f"{manufacturer} Device ({device_name})"


def get_signal_quality(rssi):
    """
    Get signal quality description based on RSSI value.
    
    Args:
        rssi: RSSI value in dBm
        
    Returns:
        str: Signal quality description with emoji
    """
    if rssi >= -30:
        return "📶 Excellent"
    elif rssi >= -50:
        return "📶 Very Good"
    elif rssi >= -60:
        return "📶 Good"
    elif rssi >= -70:
        return "📶 Fair"
    elif rssi >= -80:
        return "📶 Weak"
    else:
        return "📶 Very Weak"