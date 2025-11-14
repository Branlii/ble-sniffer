"""
Main BLE scanner class with detection logic.
"""

import asyncio
import time
import signal
from bleak import BleakScanner

from config.settings import RSSI_THRESHOLD, PRINT_INTERVAL
from models.device_manager import DeviceManager
from utils.ble_analyzer import get_manufacturer_name, analyze_services
from utils.display import display_devices, merge_related_devices


class BLEScanner:
    """Main BLE scanner class that coordinates device detection and display."""
    
    def __init__(self, print_interval=None):
        self.device_manager = DeviceManager()
        self.scanner = None
        self.last_print = 0
        # Use provided interval or fall back to config setting
        self.print_interval = print_interval if print_interval is not None else PRINT_INTERVAL
        # Import and initialize the transaction DB
        from utils.transaction_db import TransactionDB
        self.transaction_db = TransactionDB()
    
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

        # Add transaction to SQLite DB
        import json
        timestamp = device_info['last_seen']
        # Serialize device_info as JSON for the 'data' field
        self.transaction_db.add_transaction(
            str(timestamp),
            dev_id,
            json.dumps(device_info)
        )
    
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
        # Close the transaction DB connection
        self.transaction_db.close()
    
    def should_display_update(self):
        """Check if it's time to display an update."""
        current_time = time.time()
        if current_time - self.last_print >= self.print_interval:
            self.last_print = current_time
            return True
        return False
    
    async def run(self):
        """
        Main run loop for the BLE scanner.
        Starts scanning and displays periodic updates.
        """
        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        
        def signal_handler():
            print("\n⏹️  Signal received - shutting down gracefully...")
            # Cancel the main task to trigger exception
            for task in asyncio.all_tasks(loop):
                task.cancel()
        
        # Handle SIGINT (Ctrl+C) and SIGTERM
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
        
        await self.start_scanning()
        
        try:
            while True:
                await asyncio.sleep(0.2)
                
                if self.should_display_update():
                    display_devices(self.device_manager)
                    # Add scan report to database with merged device count
                    merged_devices = merge_related_devices(self.device_manager)
                    device_count = len(merged_devices)
                    self.transaction_db.add_scan_report(
                        scan_timestamp=self.device_manager.now(),
                        device_count=device_count
                    )
                    
        except KeyboardInterrupt:
            print("\n⏹️  Arrêt demandé par l'utilisateur")
        except asyncio.CancelledError:
            print("\n⏹️  Arrêt en cours...")
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