// Robot Template app
//
// Framework for creating applications that control the Kobuki robot

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "app_error.h"
#include "app_timer.h"
#include "nrf.h"
#include "nrf_delay.h"
#include "nrf_gpio.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"
#include "nrf_pwr_mgmt.h"
#include "nrf_drv_spi.h"

#include "buckler.h"
#include "display.h"
#include "kobukiActuator.h"
#include "kobukiSensorPoll.h"
#include "kobukiSensorTypes.h"
#include "kobukiUtilities.h"
#include "lsm9ds1.h"
#include "simple_ble.h"

#include "states.h"

#include "app_util.h"
#include "nrf_twi_mngr.h"

// #include "max44009.h"

// I2C manager
NRF_TWI_MNGR_DEF(twi_mngr_instance, 5, 0);

// global variables
KobukiSensors_t sensors = {0};
states state = OFF;

// Intervals for advertising and connections
static simple_ble_config_t ble_config = {
        // c0:98:e5:49:xx:xx
        .platform_id       = 0x49,    // used as 4th octect in device BLE address
        .device_id         = 0x0000, // TODO: replace with your lab bench number
        .adv_name          = "ROMI", // used in advertisements if there is room
        .adv_interval      = MSEC_TO_UNITS(1000, UNIT_0_625_MS),
        .min_conn_interval = MSEC_TO_UNITS(100, UNIT_1_25_MS),
        .max_conn_interval = MSEC_TO_UNITS(200, UNIT_1_25_MS),
};

// 32e61089-2b22-4db5-a914-43ce41986c70
static simple_ble_service_t robot_service = {{
    .uuid128 = {0x70,0x6C,0x98,0x41,0xCE,0x43,0x14,0xA9,
                0xB5,0x4D,0x22,0x2B,0x8b,0x10,0xE6,0x32}
}};

// TODO: Declare characteristics and variables for your service
static simple_ble_char_t current_pos_char = {.uuid16 = 0x108a};
static simple_ble_char_t target_pos_char = {.uuid16 = 0x108b};
static simple_ble_char_t current_orient_char = {.uuid16 = 0x108c};

static float current_pos[2];
// static float current_pos;
static float target_pos[2];
static float current_orient;
static bool display_state = true;
static char buf[16];

// void print_state(states current_state){
//  switch(current_state){
//  case OFF:
//    display_write("OFF", DISPLAY_LINE_0);
//    break;
//     }
// }

static float measure_distance(uint16_t current_encoder, uint16_t previous_encoder) {
  // conversion from encoder ticks to meters
  const float CONVERSION = 0.0006108;
  // calculate result here and return
  float distance = 0;
  uint16_t diff = 0;
  if (current_encoder < previous_encoder) {
    diff = 65535 - previous_encoder + current_encoder;
  } else {
    diff = current_encoder - previous_encoder;
  }
  distance = diff * CONVERSION;
  return distance;
}

/*******************************************************************************
 *   State for BLE application
 ******************************************************************************/
// Main application state
simple_ble_app_t* simple_ble_app;

void ble_evt_write(ble_evt_t const* p_ble_evt) {
    if (simple_ble_is_char_event(p_ble_evt, &current_pos_char)) {
      printf("Got current position!\n");
      // printf("X: %f, Y: %f\n", current_pos[0], current_pos[1]);
      snprintf(buf, 16, "%f", current_pos[0]);
      // snprintf(buf, 16, "%f", current_pos);
      display_write(buf, DISPLAY_LINE_0);
      snprintf(buf, 16, "%f", current_pos[1]);
      display_write(buf, DISPLAY_LINE_1);
    } else if (simple_ble_is_char_event(p_ble_evt, &target_pos_char)) {
      printf("Got target position!\n");
      snprintf(buf, 16, "%f", target_pos[0]);
      display_write(buf, DISPLAY_LINE_0);
      snprintf(buf, 16, "%f", target_pos[1]);
      display_write(buf, DISPLAY_LINE_1);
      // printf("X: %f, Y: %f\n", target_pos[0], target_pos[1]);
    } else if (simple_ble_is_char_event(p_ble_evt, &current_orient_char)) {
      printf("Got current orientation!\n");
      // printf("Orientation: %f\n", current_orient, current_orient);
      snprintf(buf, 16, "%f", current_orient);
      display_write(buf, DISPLAY_LINE_0);
    }
}

int main(void) {
  ret_code_t error_code = NRF_SUCCESS;

  // initialize RTT library
  error_code = NRF_LOG_INIT(NULL);
  APP_ERROR_CHECK(error_code);
  NRF_LOG_DEFAULT_BACKENDS_INIT();
  printf("Log initialized!\n");

  // Setup BLE
  simple_ble_app = simple_ble_init(&ble_config);

  simple_ble_add_service(&robot_service);

  // TODO: Register your characteristics
  simple_ble_add_characteristic(1, 1, 0, 0, 8, (uint32_t *)&current_pos, &robot_service, &current_pos_char);
  simple_ble_add_characteristic(1, 1, 0, 0, 8, (uint32_t *)&target_pos, &robot_service, &target_pos_char);
  simple_ble_add_characteristic(1, 1, 0, 0, 4, (uint32_t *)&current_orient, &robot_service, &current_orient_char);

  // Start Advertising
  simple_ble_adv_only_name();

  // initialize LEDs
  nrf_gpio_pin_dir_set(23, NRF_GPIO_PIN_DIR_OUTPUT);
  nrf_gpio_pin_dir_set(24, NRF_GPIO_PIN_DIR_OUTPUT);
  nrf_gpio_pin_dir_set(25, NRF_GPIO_PIN_DIR_OUTPUT);

  // initialize display
  nrf_drv_spi_t spi_instance = NRF_DRV_SPI_INSTANCE(1);
  nrf_drv_spi_config_t spi_config = {
    .sck_pin = BUCKLER_LCD_SCLK,
    .mosi_pin = BUCKLER_LCD_MOSI,
    .miso_pin = BUCKLER_LCD_MISO,
    .ss_pin = BUCKLER_LCD_CS,
    .irq_priority = NRFX_SPI_DEFAULT_CONFIG_IRQ_PRIORITY,
    .orc = 0,
    .frequency = NRF_DRV_SPI_FREQ_4M,
    .mode = NRF_DRV_SPI_MODE_2,
    .bit_order = NRF_DRV_SPI_BIT_ORDER_MSB_FIRST
  };
  error_code = nrf_drv_spi_init(&spi_instance, &spi_config, NULL, NULL);
  APP_ERROR_CHECK(error_code);
  display_init(&spi_instance);
  display_write("Hello, Human!", DISPLAY_LINE_0);
  printf("Display initialized!\n");

  // initialize i2c master (two wire interface)
  nrf_drv_twi_config_t i2c_config = NRF_DRV_TWI_DEFAULT_CONFIG;
  i2c_config.scl = BUCKLER_SENSORS_SCL;
  i2c_config.sda = BUCKLER_SENSORS_SDA;
  i2c_config.frequency = NRF_TWIM_FREQ_100K;
  error_code = nrf_twi_mngr_init(&twi_mngr_instance, &i2c_config);
  APP_ERROR_CHECK(error_code);
  lsm9ds1_init(&twi_mngr_instance);
  printf("IMU initialized!\n");

  // initialize Kobuki
  kobukiInit();
  printf("Kobuki initialized!\n");

  KobukiSensors_t sensors = {0};
  
  uint16_t position = 0;
  int16_t l_fwd = 50;
  int16_t r_fwd = 50;
  int16_t turn = 35;
  uint16_t counter = 0;
  float current_x = 0;
  float current_y = 0;
  float subtarget_x = 0;
  float subtarget_y = 0;
  // float current_orient = 0;
  float target_orient = 90;
  bool at_subtarget = 0;
  float UP = 0;
  float DOWN = 180;
  float LEFT = 270;
  float RIGHT = 90;

  // For testing without BLE input
  float subtarget_pos[6][2] = {{0, 0.3}, {0.10, 0.3}, {0.3, 0.3}, {0.3, 0.5}, {0.18, 0.5}, {0.18, 0.4}};
  float subtarget_ang[6] = {UP, RIGHT, RIGHT, UP, LEFT, DOWN};
  uint32_t subtarget_ind = 0;

  // loop forever, running state machine
  while (1) {
    // read sensors from robot
    kobukiSensorPoll(&sensors);
    subtarget_x = subtarget_pos[subtarget_ind][0];
    subtarget_y = subtarget_pos[subtarget_ind][1];
    target_orient = atan2(subtarget_y - current_y, subtarget_x - current_x);
    // target_orient = subtarget_ang[subtarget_ind];

    // delay before continuing
    // Note: removing this delay will make responses quicker, but will result
    //  in printf's in this loop breaking JTAG
    nrf_delay_ms(1);
    //kobukiDriveDirect(0, 0);

    // handle states
    switch(state) {
      case OFF: {
        // transition logic
        if (is_button_pressed(&sensors)) {
          state = DRIVING;
          position = sensors.leftWheelEncoder;
        } else if (is_button_pressed(&sensors) && (current_orient != target_orient)) { //-> TURN_RIGHT currently not used since not getting current_orient from ble
          state = TURN_RIGHT;
        } else {
          // perform state-specific actions here
          // display_write("OFF", DISPLAY_LINE_0);
          kobukiDriveDirect(0, 0);
          state = OFF;
        }
        break; // each case needs to end with break!
      }

      case DRIVING: {
        float dist = measure_distance(sensors.leftWheelEncoder, position);
        char buf[16];
        snprintf(buf, 16, "%f", dist);
        //display_write(buf, DISPLAY_LINE_1);
        // transition logic
        if (is_button_pressed(&sensors)) {
          position = sensors.leftWheelEncoder;
          state = OFF;
        } else if (dist >= subtarget_y) { //TODO: Need to compare x and y here... seems like there isn't a good way to do so with just encoder measurement
          state = SUBTARGET_REACHED;
          subtarget_ind += 1;
        } else {
          // perform state-specific actions here
          display_write("DRIVING", DISPLAY_LINE_0);
          kobukiDriveDirect(75, 75);
          state = DRIVING;
        }
        break; // each case needs to end with break!
      }

      case TURN_RIGHT: {
        lsm9ds1_measurement_t orients = lsm9ds1_read_gyro_integration();
        // float current_orient = fabs(orients.z_axis);
        char buf_ang[16];
        snprintf(buf_ang, 16, "%f", current_orient);
        //display_write(buf_ang, DISPLAY_LINE_1);

        if (is_button_pressed(&sensors)) { // -> OFF
          state = OFF;
          lsm9ds1_stop_gyro_integration();
        } else if (current_orient < (target_orient + 5) & current_orient > (target_orient - 5)) { // -> DRIVING
          state = DRIVING;
          position = sensors.leftWheelEncoder;
          lsm9ds1_stop_gyro_integration();
        } else {
          state = TURN_RIGHT;
          kobukiDriveDirect(turn, -turn);
          printf("TURN_RIGHT\t%f\n", target_orient);
          display_write("TURN_RIGHT", DISPLAY_LINE_0);
        }
        break;
      }

      case SUBTARGET_REACHED: {
        uint32_t prev_ind = subtarget_ind - 1;
        if (is_button_pressed(&sensors))  { // -> OFF
          state = OFF;
        //} else if (target_orient == current_orient) {
        } else if (current_orient == subtarget_ang[prev_ind]) {
          at_subtarget = 0;
          state = DRIVING;
          position = sensors.leftWheelEncoder;
        } else if (target_orient == LEFT) {
          at_subtarget = 0;
          state = TURN_LEFT;
          lsm9ds1_start_gyro_integration();
        } else if (target_orient == RIGHT) {
          at_subtarget = 0;
          state = TURN_RIGHT;
          lsm9ds1_start_gyro_integration();
        } else {
          printf("SUBTARGET_REACHED\t%f\n");
          display_write("SUBTARGET_REACHED", DISPLAY_LINE_0);
          kobukiDriveDirect(0, 0);
          at_subtarget = 1;
          state = SUBTARGET_REACHED;

          // determining which direction to turn
          // if (subtarget_x > current_x) {
          //     if (current_orient == UP) {
          //        target_orient = RIGHT;
          //     } else if (current_orient == DOWN) {
          //        target_orient = LEFT;
          //     }
          // } else if (subtarget_x < current_x) {
          //     if (current_orient == UP) {
          //        target_orient = LEFT;
          //     } else if (current_orient == DOWN) {
          //        target_orient = RIGHT;
          //     }
          // } else if (subtarget_y > current_y) {
          //     if (current_orient == LEFT) {
          //        target_orient = RIGHT;
          //     } else if (current_orient == RIGHT) {
          //        target_orient = LEFT;
          //     }
          // } else if (subtarget_y < current_y) {
          //     if (current_orient == LEFT) {
          //        target_orient = LEFT;
          //     } else if (current_orient == RIGHT) {
          //        target_orient = RIGHT;
          //     }
          // } else {
          //     target_orient = current_orient;
          // }

        }
        break;
      }

      case TURN_LEFT: {
        lsm9ds1_measurement_t orients = lsm9ds1_read_gyro_integration();
        // float current_orient = fabs(orients.z_axis);
        char buf_ang[16];
        snprintf(buf_ang, 16, "%f", current_orient);
        //display_write(buf_ang, DISPLAY_LINE_1);
        if (is_button_pressed(&sensors)) { // -> OFF
          state = OFF;
        } else if (current_orient < (target_orient + 5) & current_orient > (target_orient - 5)) { // -> DRIVE_STRAIGHT
          state = DRIVING;
          position = sensors.leftWheelEncoder;
          lsm9ds1_stop_gyro_integration();
        } else {
          state = TURN_LEFT;
          kobukiDriveDirect(-turn, turn);
          printf("TURN_LEFT\t%f\n", target_orient);
          display_write("TURN_LEFT", DISPLAY_LINE_0);
        }
        break;
      }

    }
  }
}