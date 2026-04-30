## 

## 17 Apr

### First, a 'philosophical' problem:

How to define an "annoying" or "unacceptable" sound level e.g.
- If a sound exceeded 80 decibels for more than 5 seconds at any frequency
	 - warning light should go on?

Frequency is important - not all sounds are equally annoying at each frequency

Q: Is a very short very annoying sound acceptable? What if it repeats?

Probably there has been AI models trained on cheap mics that can still classify sound well in a human perceptive way

In general, research shows that the suddenness of a sound (the "attack") and its contrast against the background noise floor are better predictors of annoyance than the absolute level.

### Microphone choice:

Idea:Let's go from KY-037 to the SPH0645LM4H (Mems microphone). To use this microphone you'll need to learn a bit around the I2S protocol for digital audio and how to receive audio from the microphone using it. 

Then you could try to implement something like:

- The "Traffic Light" Approach (Safe)
Instead of displaying raw decibels, use categories: Quiet, Normal, Distracting, and Harmful
Because the SPH0645 is very consistent unit-to-unit, you can hardcode these thresholds
Even if the mic is off by 2dB, it won't matter to the user if the "Distracting" light comes on

### Microcontroller Choice

As we will need bluetooth which RP2040 doesn't have, it's better to switch to ESP32-C3 now rather than later

It can still run micropython, just need to flash it first with the right firmware

# I2S code example (Arduino-style, you'll need something MicroPython specific)

Example code using ESP32 I2S Library
```
#include "driver/i2s.h"

#define I2S_WS 3
#define I2S_SD 4
#define I2S_SCK 2
#define I2S_PORT I2S_NUM_0

// Buffer to store incoming audio samples
#define BUFFER_LEN 64
int32_t samples[BUFFER_LEN]; 

void setup() {
  Serial.begin(115200);

  // 1. I2S Configuration for Microphone
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX), // Master Receiver
    .sample_rate = 16000,                               // 16kHz is great for voice
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,       // Most I2S mics output 24/32-bit
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,        // Use the channel set by L/R pin
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = BUFFER_LEN,
    .use_apll = false
  };

  // 2. Pin Configuration
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE, 
    .data_in_num = I2S_SD               // Use the Data In pin
  };

  // 3. Start I2S
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}

void loop() {
  size_t bytes_read;
  
  // 4. Read from the microphone buffer
  // This blocks until the buffer is full
  esp_err_t result = i2s_read(I2S_PORT, &samples, sizeof(samples), &bytes_read, portMAX_DELAY);

  if (result == ESP_OK && bytes_read > 0) {
    int read_len = bytes_read / sizeof(int32_t);
    
    for (int i = 0; i < read_len; i++) {
      // The raw data from I2S mics is often very large; 
      // we can shift or scale it to visualize better
      printf("%ld\n", samples[i]); 
    }
  }
}
```
