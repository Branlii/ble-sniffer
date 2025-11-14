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
    
    parser.add_argument(
        '--interval',
        type=float,
        default=None,
        help='Set display update interval in seconds (default: 2 seconds)'
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
    
    # Update print interval based on parameter
    if args.interval is not None:
        print(f"⏱️  Display interval set to {args.interval} seconds")
        print_interval = args.interval
    else:
        print(f"⏱️  Using default display interval: {settings.PRINT_INTERVAL} seconds")
        print_interval = settings.PRINT_INTERVAL
    
    # Update debug mode based on parameter
    if args.debug:
        settings.DEBUG_MODE = True
        print("🐛 Debug mode enabled - showing all BLE signals separately")
    else:
        print(f"🔍 Debug mode: {'enabled' if settings.DEBUG_MODE else 'disabled'}")
    
    scanner = BLEScanner(print_interval=print_interval)
    await scanner.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
