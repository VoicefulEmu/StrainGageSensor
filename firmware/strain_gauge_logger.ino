/*
 * Strain Gauge Data Logger using ESP32 and HX711
 * 
 * Reads strain gauge data from HX711 load cell amplifier
 * and sends it via serial to a computer for logging
 * 
 * Connections:
 * HX711 DT pin  -> ESP32 GPIO 25
 * HX711 SCK pin -> ESP32 GPIO 26
 * HX711 GND     -> ESP32 GND
 * HX711 VCC     -> ESP32 3.3V
 */

#include <HX711.h>
#include <SD.h>          // SD card library (SPI)
#include <SPI.h>

// HX711 pins
const int LOADCELL_DOUT_PIN = 25;
const int LOADCELL_SCK_PIN = 26;

// SD card pins (adjust if using different pins)
// Connect CS to pin 5 (or change to your preferred GPIO)
const int SD_CS_PIN = 5;

// HX711 object
HX711 scale;

// File handle for SD logging
File dataFile;

// Configuration
const long CALIBRATION_FACTOR = 420.0;  // Adjust based on your calibration
const int SAMPLE_RATE_MS = 100;        // 10 Hz sampling (100ms per sample)
const int NUM_AVERAGES = 5;             // Average across 5 readings

// Timing
unsigned long lastSampleTime = 0;
unsigned long sampleCount = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n========================================");
  Serial.println("Strain Gauge Data Logger - ESP32 + HX711");
  Serial.println("========================================");
  Serial.println();
  
  // Initialize HX711
  Serial.println("Initializing HX711...");
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  
  // Set calibration factor
  scale.set_scale(CALIBRATION_FACTOR);
  
  // Zero the scale
  Serial.println("Zeroing scale... Please ensure no weight is on the sensor.");
  delay(2000);
  scale.tare();
  
  Serial.println("HX711 initialized and zeroed.");
  Serial.println();

  // --- initialize SD card ---
  Serial.print("Initializing SD card on CS pin ");
  Serial.println(SD_CS_PIN);
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD initialization failed! Data will only be sent over serial.");
  } else {
    Serial.println("SD card initialized.");
    // create a new file name based on millis to avoid overwriting
    String filename = "/log_" + String(millis()) + ".csv";
    dataFile = SD.open(filename, FILE_WRITE);
    if (dataFile) {
      // write header
      dataFile.println("Timestamp_ms,Weight_g,RawValue");
      dataFile.flush();
      Serial.print("Logging to SD file: ");
      Serial.println(filename);
    } else {
      Serial.println("Failed to open file on SD card.");
    }
  }
  Serial.println("Format: Timestamp(ms),Weight(g),RawValue");
  Serial.println("----------------------------------------");
  
  lastSampleTime = millis();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time to take a sample
  if (currentTime - lastSampleTime >= SAMPLE_RATE_MS) {
    lastSampleTime = currentTime;
    
    // Check if HX711 is ready
    if (scale.is_ready()) {
      // Take multiple readings and average them
      float totalWeight = 0;
      long totalRaw = 0;
      
      for (int i = 0; i < NUM_AVERAGES; i++) {
        if (scale.is_ready()) {
          long rawValue = scale.read();
          float weight = scale.get_units(1);  // Get 1 reading
          
          totalRaw += rawValue;
          totalWeight += weight;
          
          // Small delay between readings
          delayMicroseconds(100);
        }
      }
      
      // Calculate averages
      float avgWeight = totalWeight / NUM_AVERAGES;
      long avgRaw = totalRaw / NUM_AVERAGES;
      
      // Send data to serial (timestamp, weight, raw value)
      Serial.print(currentTime);
      Serial.print(",");
      Serial.print(avgWeight, 3);  // 3 decimal places
      Serial.print(",");
      Serial.println(avgRaw);
      
      // also append to SD card if available
      if (dataFile) {
        dataFile.print(currentTime);
        dataFile.print(",");
        dataFile.print(avgWeight, 3);
        dataFile.print(",");
        dataFile.println(avgRaw);
        dataFile.flush(); // ensure it's written
      }
      
      sampleCount++;
      
    } else {
      Serial.println("HX711 not ready!");
    }
  }
  
  // Optional: Print status periodically (every 10 seconds)
  static unsigned long lastStatusTime = 0;
  if (currentTime - lastStatusTime > 10000) {
    lastStatusTime = currentTime;
    Serial.print("// Status: ");
    Serial.print(sampleCount);
    Serial.println(" samples collected");
    if (dataFile) {
      Serial.print("// SD file size: ");
      Serial.println(dataFile.size());
    }
  }
}
