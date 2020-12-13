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

static float current_pos[3];
static uint16_t num_targets = 80;
static float target_pos[80] = {0};
static float current_orient;
// static char buf[16];
// static char buf2[16];
static bool ready = false;
static bool ready2 = false;
static uint32_t num_pause = 0;
static bool avg_flag = false;
static float avg_orient = 0;
static float avg_orient_360 = 0;
static bool timing = false;
static uint32_t num_drive = 0;
/*******************************************************************************
 *   State for BLE application
 ******************************************************************************/
// Main application state
simple_ble_app_t* simple_ble_app;

void ble_evt_write(ble_evt_t const* p_ble_evt) {
    if (simple_ble_is_char_event(p_ble_evt, &current_pos_char)) {
      printf("Got current position!\n");
      ready2 = true;
      if (avg_flag) {
        if (current_pos[2] > 350) {
          avg_orient_360 += current_pos[2];
          avg_orient += current_pos[2] - 360;
        } else if (current_pos[2] < 10) {
          avg_orient += current_pos[2];
          avg_orient_360 += current_pos[2] + 360;
        } else {
          avg_orient += current_pos[2];
          avg_orient_360 += current_pos[2];
        }
        num_pause += 1;
      }

      if (timing) {
        num_drive += 1;
      }
      // snprintf(buf, 16, "%f", current_pos[0]);
      // display_write(buf, DISPLAY_LINE_0);
      // snprintf(buf, 16, "%f", current_pos[2]);
      // display_write(buf, DISPLAY_LINE_1);
    } else if (simple_ble_is_char_event(p_ble_evt, &target_pos_char)) {
      printf("Got target position!\n");
      ready = true;
      // snprintf(buf, 16, "%u", ready);
      // display_write(buf, DISPLAY_LINE_0);
      // snprintf(buf, 16, "%f", target_pos[3]);
      // display_write(buf, DISPLAY_LINE_1);
      // printf("X: %f, Y: %f\n", target_pos[0], target_pos[1]);
    }
}

static uint16_t get_delta(uint16_t current_encoder, uint16_t previous_encoder) {
  // calculate result here and return it
  if (current_encoder >= previous_encoder) {
    return (current_encoder - previous_encoder);
  } else {
    return ((65536 - previous_encoder) + current_encoder);
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
  simple_ble_add_characteristic(1, 1, 0, 0, 12, (uint8_t *)&current_pos, &robot_service, &current_pos_char);
  simple_ble_add_characteristic(1, 1, 0, 0, 320, (uint8_t *)&target_pos, &robot_service, &target_pos_char);

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

  //uint16_t position = 0;
  int16_t l_fwd = 35;
  int16_t r_fwd = 35;
  int16_t turn = 35;
  int16_t turn_correction = 30;
  float current_x = 0;
  float current_y = 0;
  float subtarget_x = 0;
  float subtarget_y = 0;
  float target_orient = 0;
  
  float angle_tolerance = 2.5;
  float dist_tolerance = 7.5;
  uint32_t subtarget_ind = 0;
  float angle_to_travel = 0;
  // float start_x = 0;
  // float start_y = 0;
  uint16_t l_pos = 0;
  uint16_t r_pos = 0;
  uint16_t prev_l_pos = 0;
  uint16_t prev_r_pos = 0;
  int delta = 0;
  uint16_t l_delta = 0;
  uint16_t r_delta = 0;
  float scale = .1;
  float curr_dist = 0;
  float prev_dist = 0;
  bool to_pause = false;
  uint32_t num_pause_init = 0;
  int delta_correction = 0;
  float angle_scale = 9.2;
  bool orient_correction = false;

  // loop forever, running state machine
  while (1) {

    // read sensors from robot
    kobukiSensorPoll(&sensors);

    subtarget_x = target_pos[subtarget_ind];
    subtarget_y = target_pos[subtarget_ind+1];

    // if (subtarget_x == 0 || subtarget_y == 0) {
    //   subtarget_x = start_x;
    //   subtarget_y = start_y;
    // }

    current_x = current_pos[0];
    current_y = current_pos[1]; 
    current_orient = current_pos[2];

    target_orient = atan2(subtarget_y - current_y, subtarget_x - current_x) * 180 / M_PI;
    if (target_orient <= 0) {
      target_orient += 360;
    }

    // delay before continuing
    // nrf_delay_ms(1);

    // handle states
    switch(state) {
      case OFF: {
        // transition logic
        if (ready && ready2 && ((current_orient > target_orient + angle_tolerance) || (current_orient < target_orient - angle_tolerance))) { //-> TURN_RIGHT currently not used since not getting current_orient from ble
          // start_x = current_pos[0];
          // start_y = current_pos[1];
          if (target_orient <= current_orient) {
              if (current_orient - target_orient <= 180) {
                state = TURN_LEFT;
                orient_correction = false;
                angle_to_travel = current_orient - target_orient;
              } else {
                state = TURN_RIGHT;
                orient_correction = false;
                angle_to_travel = 360 - current_orient + target_orient;
              }
          } else {
            if (target_orient - current_orient <= 180) {
              state = TURN_RIGHT;
              orient_correction = false;
              angle_to_travel = target_orient - current_orient;
            } else {
              state = TURN_LEFT;
              orient_correction = false;
              angle_to_travel = 360 - target_orient + current_orient;
            }
          }
          lsm9ds1_start_gyro_integration();
        } else if (ready && ready2) {
          num_drive = 0;
          state = DRIVING;
          orient_correction = false;
          subtarget_ind = 0;
          prev_l_pos = sensors.leftWheelEncoder;
          prev_r_pos = sensors.rightWheelEncoder;
          timing = true;
          prev_dist = (current_x - subtarget_x) * (current_x - subtarget_x) + (current_y - subtarget_y) * (current_y - subtarget_y);
        } else {
          display_write("OFF", DISPLAY_LINE_0);
          kobukiDriveDirect(0, 0);
          state = OFF;
        }
        break; // each case needs to end with break!
      }

      case DRIVING: {
        l_pos = sensors.leftWheelEncoder;
        r_pos = sensors.rightWheelEncoder;
        l_delta = get_delta(l_pos, prev_l_pos);
        r_delta = get_delta(r_pos, prev_r_pos);

        if (current_orient - target_orient > 90) {
          delta_correction = (int) (angle_scale * (360 + target_orient - current_orient));
        } else if (target_orient - current_orient > 90) {
          delta_correction = (int) (angle_scale * -(360 - target_orient + current_orient));
        } else {
          delta_correction = (int) (angle_scale * (target_orient - current_orient));
        }

        delta = l_delta - r_delta - delta_correction;

        r_fwd = 35 + (int) (scale * delta);
        l_fwd = 35 - (int) (scale * delta);

        if (num_drive % 5 == 0) {
          curr_dist = ((current_x - subtarget_x) * (current_x - subtarget_x)) + ((current_y - subtarget_y) * (current_y - subtarget_y));
          if (curr_dist > prev_dist) {
            to_pause = true;
          }

          prev_dist = curr_dist;
        }
        
        if (((current_x >= subtarget_x - dist_tolerance) && (current_x <= subtarget_x + dist_tolerance)) && ((current_y >= subtarget_y - dist_tolerance) && (current_y <= subtarget_y + dist_tolerance))) {
          state = SUBTARGET_REACHED;
          timing = false;
          orient_correction = false;
          subtarget_ind += 2;
        } else if (to_pause) {
            state = PAUSE;
            to_pause = false; 
            timing = false;
            orient_correction = false;
            num_pause = 0;
            num_pause_init = num_pause;
            avg_orient = 0;
            avg_orient_360 = 0;
            avg_flag = true;
        } else {
          // perform state-specific actions here
          display_write("DRIVING", DISPLAY_LINE_0);
          prev_dist = curr_dist;
          kobukiDriveDirect(l_fwd, r_fwd);
          state = DRIVING;
        }

        break; // each case needs to end with break!
      }

      case TURN_RIGHT: {
        lsm9ds1_measurement_t orients = lsm9ds1_read_gyro_integration();
        float gyro_orient = fabs(orients.z_axis);

        char buf_ang[16];
        snprintf(buf_ang, 16, "%f", gyro_orient);
        display_write(buf_ang, DISPLAY_LINE_1);

        if ((gyro_orient <= (angle_to_travel + 2)) && (gyro_orient >= (angle_to_travel - 2))) {
          state = PAUSE;
          num_pause = 0;
          num_pause_init = num_pause;
          avg_orient = 0;
          avg_orient_360 = 0;
          avg_flag = true;
          orient_correction = true;
          lsm9ds1_stop_gyro_integration();
        } else {
          state = TURN_RIGHT;
          if (orient_correction) {
            kobukiDriveDirect(turn_correction, -turn_correction);
          } else {
            kobukiDriveDirect(turn, -turn);
          }
          printf("TURN_RIGHT\t%f\n", target_orient);
          display_write("TURN_RIGHT", DISPLAY_LINE_0);
        }
        break;
      }
        
      case PAUSE: {
        if (num_pause - num_pause_init >= 10) {
          avg_flag = false;
          avg_orient = avg_orient / (num_pause - num_pause_init);
          avg_orient_360 = avg_orient_360 / (num_pause - num_pause_init);
          if (((avg_orient <= (target_orient + angle_tolerance)) && (avg_orient >= (target_orient - angle_tolerance))) || ((avg_orient_360 <= (target_orient + angle_tolerance)) && (avg_orient_360 >= (target_orient - angle_tolerance)))) {
            state = DRIVING;
            prev_l_pos = sensors.leftWheelEncoder;
            prev_r_pos = sensors.rightWheelEncoder;
            num_drive = 0;
            timing = true;
            orient_correction = false;
            prev_dist = (current_x - subtarget_x) * (current_x - subtarget_x) + (current_y - subtarget_y) * (current_y - subtarget_y);
          } else {
            if (target_orient <= current_orient) {
              if (current_orient - target_orient <= 180) {
                state = TURN_LEFT;
                angle_to_travel = current_orient - target_orient;
              } else {
                state = TURN_RIGHT;
                angle_to_travel = 360 - current_orient + target_orient;
              }
            } else {
              if (target_orient - current_orient <= 180) {
                state = TURN_RIGHT;
                angle_to_travel = target_orient - current_orient;
              } else {
                state = TURN_LEFT;
                angle_to_travel = 360 - target_orient + current_orient;
              }
            }
            lsm9ds1_start_gyro_integration();
          }
        } else {
          display_write("Pause", DISPLAY_LINE_0);
          state = PAUSE;
          kobukiDriveDirect(0, 0);
        }
        break;
      }

      case SUBTARGET_REACHED: {
        // if ((subtarget_ind >= num_targets) || ((current_x >= start_x - dist_tolerance) && (current_x <= start_x + dist_tolerance)) && ((current_y >= start_y - dist_tolerance) && (current_y <= start_y + dist_tolerance)))  { // -> OFF
        if (subtarget_ind >= num_targets || subtarget_y == 0 || subtarget_x == 0) {  
          state = OFF;
          ready = false;
          ready2 = false;
        } else {
          printf("SUBTARGET_REACHED\n");
          display_write("SUBTARGET_REACHED", DISPLAY_LINE_0);
          state = PAUSE;
          num_pause = 0;
          num_pause_init = num_pause;
          avg_orient = 0;
          avg_orient_360 = 0;
          avg_flag = true;
          orient_correction = false;
        }
        break;
      }

      case TURN_LEFT: {
        lsm9ds1_measurement_t orients = lsm9ds1_read_gyro_integration();
        float gyro_orient = fabs(orients.z_axis);

        char buf_ang[16];
        snprintf(buf_ang, 16, "%f", gyro_orient);
        display_write(buf_ang, DISPLAY_LINE_1);

        if ((gyro_orient <= (angle_to_travel + 2)) && (gyro_orient >= (angle_to_travel - 2))) {
          state = PAUSE;
          num_pause = 0;
          num_pause_init = num_pause;
          avg_orient = 0;
          avg_orient_360 = 0;
          avg_flag = true;
          orient_correction = true;
          lsm9ds1_stop_gyro_integration();
        } else {
          state = TURN_LEFT;
          if (orient_correction) {
            kobukiDriveDirect(-turn_correction, turn_correction);
          } else {
            kobukiDriveDirect(-turn, turn);
          }
          printf("TURN_LEFT\t%f\n", target_orient);
          display_write("TURN_LEFT", DISPLAY_LINE_0);
        }
        break;
      }

    }
  }
}
