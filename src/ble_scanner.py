"""
Main BLE scanner class with detection logic.
"""

import asyncio
import time
from bleak import BleakScanner

from config.settings import RSSI_THRESHOLD, PRINT_INTERVAL
from models.device_manager import DeviceManager
from utils.ble_analyzer import get_manufacturer_name, analyze_services
from utils.display import display_devices


class BLEScanner:
    """Main BLE scanner class that coordinates device detection and display."""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.scanner = None
        self.last_print = 0
    
    def detection_callback(self, device, advertisement_data):
        """
        Callback function called when a BLE device is detected.
        
        Args:
            device: BLE device object from bleak
            advertisement_data: Advertisement data from the device
        """
        # Extract device information
        dev_id = device.address
        rssi = advertisement_data.rssi
        
        # Filter by RSSI threshold
        if rssi is None or rssi < RSSI_THRESHOLD:
            return
        
        # Analyze device data
        device_name = device.name or "Unknown Device"
        manufacturer = get_manufacturer_name(advertisement_data.manufacturer_data)
        services = analyze_services(advertisement_data.service_uuids)
        
        # Create device info dictionary
        device_info = {
            'name': device_name,
            'last_rssi': rssi,
            'last_seen': self.device_manager.now(),
            'manufacturer': manufacturer,
            'services': services,
            'tx_power': advertisement_data.tx_power,
            'connectable': getattr(advertisement_data, 'connectable', None)
        }
        
        # Add sighting to device manager
        self.device_manager.add_sighting(dev_id, device_info)
    
    async def start_scanning(self):
        """Start the BLE scanning process."""
        self.scanner = BleakScanner(self.detection_callback)
        print("🔍 Démarrage du scan BLE... (autoriser Bluetooth si demandé)")
        await self.scanner.start()
    
    async def stop_scanning(self):
        """Stop the BLE scanning process."""
        if self.scanner:
            await self.scanner.stop()
            print("🛑 Scan BLE arrêté")
    
    def should_display_update(self):
        """Check if it's time to display an update."""
        current_time = time.time()
        if current_time - self.last_print >= PRINT_INTERVAL:
            self.last_print = current_time
            return True
        return False
    
    async def run(self):
        """
        Main run loop for the BLE scanner.
        Starts scanning and displays periodic updates.
        """
        await self.start_scanning()
        
        try:
            while True:
                await asyncio.sleep(0.2)
                
                if self.should_display_update():
                    display_devices(self.device_manager)
                    
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt demandé par l'utilisateur")
        finally:
            await self.stop_scanning()
    
    def get_device_count(self):
        """Get current device count."""
        return self.device_manager.get_current_count()
    
    def get_total_tracked(self):
        """Get total tracked device count."""
        return self.device_manager.get_total_tracked_count()
    
    def clear_devices(self):
        """Clear all tracked devices."""
        self.device_manager.clear()