#!/usr/bin/env python3
"""
Strain Gauge Data Logger
Receives data from ESP32 via serial and logs to CSV file
"""

import serial
import csv
import sys
from datetime import datetime
import time
from pathlib import Path

class StrainGaugeLogger:
    def __init__(self, port='COM3', baudrate=115200, output_dir='../data'):
        """
        Initialize the logger
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Serial communication speed
            output_dir: Directory to save CSV files
        """
        self.port = port
        self.baudrate = baudrate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.serial_conn = None
        self.csv_file = None
        self.csv_writer = None
        self.sample_count = 0
        self.start_time = None
        
    def connect(self):
        """Establish serial connection"""
        try:
            print(f"Connecting to {self.port} at {self.baudrate} baud...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            time.sleep(2)  # Wait for ESP32 to reset
            print("✓ Connected!")
            return True
        except serial.SerialException as e:
            print(f"✗ Error connecting to serial port: {e}")
            return False
    
    def start_logging(self):
        """Initialize CSV file and start logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = self.output_dir / f"strain_gauge_{timestamp}.csv"
        
        try:
            self.csv_file = open(self.csv_filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write header
            self.csv_writer.writerow(['Timestamp_ms', 'Weight_g', 'RawValue', 'DateTime'])
            self.csv_file.flush()
            
            self.start_time = datetime.now()
            print(f"✓ Logging to: {self.csv_filename}")
            print("\nWaiting for data from ESP32...")
            print("-" * 50)
            
        except IOError as e:
            print(f"✗ Error creating CSV file: {e}")
            return False
        
        return True
    
    def read_and_log(self):
        """Read from serial and log to CSV"""
        try:
            while True:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    # Skip comment lines and non-data lines
                    if line.startswith('//') or line.startswith('='):
                        print(f"  {line}")
                        continue
                    
                    # Parse data line (format: timestamp,weight,rawvalue)
                    try:
                        parts = line.split(',')
                        if len(parts) == 3:
                            timestamp_ms = int(parts[0])
                            weight = float(parts[1])
                            raw_value = int(parts[2])
                            
                            # Get current datetime
                            current_time = datetime.now().isoformat()
                            
                            # Write to CSV
                            self.csv_writer.writerow([
                                timestamp_ms,
                                f"{weight:.3f}",
                                raw_value,
                                current_time
                            ])
                            self.csv_file.flush()
                            
                            self.sample_count += 1
                            
                            # Print progress every 10 samples
                            if self.sample_count % 10 == 0:
                                elapsed = (datetime.now() - self.start_time).total_seconds()
                                print(f"  Samples: {self.sample_count} | "
                                      f"Weight: {weight:7.3f}g | "
                                      f"Raw: {raw_value:8d} | "
                                      f"Elapsed: {elapsed:.1f}s")
                    
                    except (ValueError, IndexError) as e:
                        print(f"  [Parse error] {line}")
        
        except KeyboardInterrupt:
            print("\n" + "-" * 50)
            print("Logging stopped by user")
        except Exception as e:
            print(f"Error during logging: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close connections and finalize"""
        if self.csv_file:
            self.csv_file.close()
        
        if self.serial_conn:
            self.serial_conn.close()
        
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        print(f"\nLogging Summary:")
        print(f"  Total samples: {self.sample_count}")
        print(f"  Duration: {elapsed:.1f} seconds")
        print(f"  File saved: {self.csv_filename}")
        print(f"  Average rate: {self.sample_count/elapsed:.1f} Hz")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Strain Gauge Data Logger for ESP32 + HX711'
    )
    parser.add_argument('--port', default='COM3',
                       help='Serial port (default: COM3)')
    parser.add_argument('--baud', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    parser.add_argument('--output', default='../data',
                       help='Output directory (default: ../data)')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available serial ports')
    
    args = parser.parse_args()
    
    # List available ports if requested
    if args.list_ports:
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            if ports:
                print("Available serial ports:")
                for port in ports:
                    print(f"  {port.device}: {port.description}")
            else:
                print("No serial ports found")
        except Exception as e:
            print(f"Error listing ports: {e}")
        return
    
    # Create logger and start logging
    logger = StrainGaugeLogger(
        port=args.port,
        baudrate=args.baud,
        output_dir=args.output
    )
    
    if not logger.connect():
        sys.exit(1)
    
    if not logger.start_logging():
        sys.exit(1)
    
    logger.read_and_log()


if __name__ == '__main__':
    main()
