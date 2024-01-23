#include <Wire.h> // I2C comm to camera
#include "Adafruit_OV7670.h" // Camera library
#include <Adafruit_GFX.h> // Core graphics library
#include <TFT_eSPI.h> // TFT_eSPI library for ILI9341
#include <SPI.h>

// CAMERA CONFIG -----------------------------------------------------------

OV7670_arch arch;
OV7670_pins pins = {
    .enable = -1, // Also called PWDN, or set to -1 and tie to GND
    .reset = 18,  // Cam reset, or set to -1 and tie to 3.3V
    .xclk = 9,    // MCU clock out / cam clock in
    .pclk = 8,    // Cam clock out / MCU clock in
    .vsync = 28,  // Also called DEN1
    .hsync = 16,  // Also called DEN2
    .data = {26, 27, 2, 3, 1, 0, 6, 7}, // Camera parallel data out
    .sda = 20,                          // I2C data
    .scl = 21,                          // I2C clock
};

#define CAM_I2C Wire

#define CAM_SIZE OV7670_SIZE_DIV4 // QQVGA (160x120 pixels)
#define CAM_MODE OV7670_COLOR_RGB // RGB plz

Adafruit_OV7670 cam(OV7670_ADDR, &pins, &CAM_I2C, &arch);

// DISPLAY CONFIG ----------------------------------------------------------

TFT_eSPI tft = TFT_eSPI();
#define KEYFRAME 30
uint16_t frame = KEYFRAME;

// SETUP - RUNS ONCE ON STARTUP --------------------------------------------

void setup(void)
{
    Serial.begin(115200);
    delay(5000);
    Serial.println(F("Hello! Camera Test"));

    pinMode(25, OUTPUT);
    digitalWrite(25, HIGH);

    tft.begin();
    //tft.setRotation(3); // Adjust rotation as needed
    tft.fillScreen(TFT_BLACK);
    tft.println("hello");

    OV7670_status status = cam.begin(CAM_MODE, CAM_SIZE, 30.0);
    if (status != OV7670_STATUS_OK)
    {
        Serial.println("Camera begin fail");
        for (;;);
    }
    Serial.println("Camera initialized successfully.");

    uint8_t pid = cam.readRegister(OV7670_REG_PID);
    uint8_t ver = cam.readRegister(OV7670_REG_VER);
    Serial.println(pid, HEX);
    Serial.println(ver, HEX);
    delay(5000);
}

// MAIN LOOP - RUNS REPEATEDLY UNTIL RESET OR POWER OFF --------------------

void loop()
{
    gpio_xor_mask(1 << 25); // Toggle LED each frame

    if (++frame >= KEYFRAME)
    { // Time to sync up a fresh address window?
        frame = 0;
        tft.setAddrWindow((tft.width() - cam.width()) / 2,
                          (tft.height() - cam.height()) / 2,
                          cam.width(), cam.height());
    }

    tft.startWrite(); // Start a fresh transfer
    cam.capture();    // Capture a frame
    tft.pushColors(cam.getBuffer(), cam.width() * cam.height(), false);
    tft.endWrite();
    delay(5000);  

    //printCameraBuffer();
}

/*void printCameraBuffer() {
  uint16_t* buffer = cam.getBuffer();
  uint32_t bufferSize = cam.width() * cam.height();

  for (uint32_t i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i]);
    Serial.print(" ");

    // Print a new line after every row
    if ((i + 1) % cam.width() == 0) {
      Serial.println();
    }
  }
}*/