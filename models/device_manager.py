"""
Device manager for tracking BLE device sightings and information.
"""

import time
from collections import defaultdict, deque
from config.settings import WINDOW_SEC, MIN_SAMPLES_PER_DEVICE


class DeviceManager:
    """Manages BLE device sightings and device information."""
    
    def __init__(self):
        # stockage: pour chaque device_id on garde timestamps des derniers sightings
        self.sightings = defaultdict(deque)  # device_id -> deque([timestamps])
        self.device_info = {}  # device_id -> {name, last_seen, manufacturer, etc.}
    
    def now(self):
        """Get current timestamp."""
        return time.time()
    
    def add_sighting(self, device_id, device_info):
        """
        Add a new device sighting.
        
        Args:
            device_id: Unique device identifier
            device_info: Dictionary containing device information
        """
        current_time = self.now()
        
        # Store device information
        self.device_info[device_id] = device_info
        
        # Add timestamp to sightings
        self.sightings[device_id].append(current_time)
    
    def prune_old(self):
        """Remove old sightings outside the time window."""
        cutoff = self.now() - WINDOW_SEC
        to_delete = []
        
        for dev, dq in list(self.sightings.items()):
            while dq and dq[0] < cutoff:
                dq.popleft()
            if not dq:
                to_delete.append(dev)
        
        for dev in to_delete:
            del self.sightings[dev]
            if dev in self.device_info:
                del self.device_info[dev]
    
    def get_current_count(self):
        """
        Get count of devices with minimum required samples.
        
        Returns:
            int: Number of active devices
        """
        self.prune_old()
        return sum(1 for dq in self.sightings.values() if len(dq) >= MIN_SAMPLES_PER_DEVICE)
    
    def get_active_devices(self):
        """
        Get dictionary of currently active devices.
        
        Returns:
            dict: Dictionary of active devices {device_id: device_info}
        """
        self.prune_old()
        active_devices = {}
        
        for dev_id, info in self.device_info.items():
            if dev_id in self.sightings and len(self.sightings[dev_id]) >= MIN_SAMPLES_PER_DEVICE:
                active_devices[dev_id] = info
        
        return active_devices
    
    def get_total_tracked_count(self):
        """
        Get total number of tracked device IDs.
        
        Returns:
            int: Total number of device IDs being tracked
        """
        return len(self.sightings)
    
    def clear(self):
        """Clear all sightings and device information."""
        self.sightings.clear()
        self.device_info.clear()