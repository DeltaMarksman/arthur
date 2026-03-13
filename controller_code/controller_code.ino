#define RIGHT_STICK_X   2
#define RIGHT_STICK_Y   3
#define MOTOR_B_P       4
#define MOTOR_B_N       7
#define MOTOR_A_N       9
#define MOTOR_A_P       8
#define MOTOR_B_EN      10
#define MOTOR_A_EN      11
#define LED             13

// Serial Protocol
#define SERIAL_INACTIVE   0b11110000
#define LED               0b00000000
#define LED_ON            0b00001111
#define LED_OFF           0b00000001
#define THROTTLE          0b00100000
#define STEERING          0b01000000


// Variables
bool motor_A_forwards   = true;
bool motor_B_forwards   = true;
int motor_A_out         = 0;  // Right motor output
int motor_B_out         = 0;  // Left motor output
int steering            = 0;  // Steering input
int throttle            = 0;  // Throttle input

void setup() {
  // Begin serial
  Serial.begin(9600);
  Serial.println("Arduino Hello!");

  // Initialize controls
  pinMode(  RIGHT_STICK_X ,   INPUT   );
  pinMode(  RIGHT_STICK_Y ,   INPUT   );

  // Motor
  pinMode(  MOTOR_B_P     ,   OUTPUT  );
  pinMode(  MOTOR_B_N     ,   OUTPUT  );
  pinMode(  MOTOR_A_P     ,   OUTPUT  );
  pinMode(  MOTOR_A_N     ,   OUTPUT  );
  pinMode(  MOTOR_B_EN    ,   OUTPUT  );
  pinMode(  MOTOR_A_EN    ,   OUTPUT  );
  pinMode(  LED           ,   OUTPUT  );

}

void setDirection(int MOTOR_P, int MOTOR_N, bool forwards) {
  digitalWrite(MOTOR_P, forwards ? HIGH : LOW);
  digitalWrite(MOTOR_N, forwards ? LOW : HIGH);
}

/*
Formula is outlined in 
https://www.desmos.com/calculator/0yqgsdipvz
*/
const int boost_to_level = 70;
const int low_level_threshold = 20;
const float linearity = 35.0;
int low_level_booster(int input) {

  // Flips input if it is negative, calculates for positve, then flips result.
  bool was_negative = false;
  if (input < 0) {
    was_negative = true;
    input *= -1;
  }

  int output = 0;

  // Linearity
  int linearity_term = -(pow((float) input-(float)low_level_threshold, 2) / (10.0*linearity)) + (2.55-(low_level_threshold)/100) * (100/(10 * linearity)) * (input-low_level_threshold);


  if (abs(input) < low_level_threshold) {
    
    output = input * (boost_to_level/low_level_threshold);
  } else {
    float output_slope = (255.0 - boost_to_level) / (255.0 - low_level_threshold);
    printf("output slope%f\n", output_slope);

    output = ((output_slope * input) + boost_to_level - (low_level_threshold * output_slope)) - linearity_term;
  }

  return was_negative ? output * -1 : output;
}

void led_on() {
  digitalWrite(LED, HIGH);
}

void led_off() {
  digitalWrite(LED, LOW);
}


void serial_control_loop() {
  if (Serial.available() <= 0) 
    return;

  uint8_t incomingByte = Serial.read();
  Serial.println(incomingByte);

  // Extract fields
  uint8_t   peripheral    = incomingByte & 0b11100000;  // PPPS ----
  uint8_t   magnitude     = incomingByte & 0b00001111;  // ---- XXXX
  bool      isNegative    = incomingByte & 0b00010000;  // ---- S---

  int value = magnitude * (isNegative ? -1 : 1);

  switch (peripheral) {

    // -------------------------
    // LED CONTROL
    // -------------------------
    case LED:
      switch (magnitude) {
        case LED_ON:   // LED_ON
          Serial.println("Received LED_ON");
          led_on();
          break;

        case LED_OFF:   // LED_OFF
          Serial.println("Received LED_OFF");
          led_off();
          break;

        default:
          Serial.print("Unknown LED command: ");
          Serial.println(magnitude, BIN);
          break;
      }
      break;

    // -------------------------
    // THROTTLE CONTROL
    // -------------------------
    case THROTTLE:   // 001S XXXX
      throttle = map(value, -16, 16, -255, 255);
      Serial.print("Throttle set to: ");
      Serial.println(throttle);
      break;

    // -------------------------
    // STEERING CONTROL
    // -------------------------
    case STEERING:   // 010S XXXX
      steering = map(value, -16, 16, -255, 255);
      Serial.print("Steering set to: ");
      Serial.println(steering);
      break;

    // -------------------------
    // UNKNOWN / UNUSED
    // -------------------------
    default:
      Serial.print("Unknown peripheral: ");
      Serial.println(peripheral, BIN);
      break;
  }
}


bool controlled_by_serial = false;
void loop() {
  if (controlled_by_serial) {
      serial_control_loop();
  } else {
    // Get control values
    steering = low_level_booster(map(pulseIn(RIGHT_STICK_X, HIGH), 1000, 1989, -255, 255));
    throttle = low_level_booster(map(pulseIn(RIGHT_STICK_Y, HIGH), 995, 1989, -255, 255));
  }


  Serial.print("Steering: " + String(steering));
  Serial.println("\t\tThrottle: " + String(throttle));
  
  // Create deadzones if rc controlled
  if (!controlled_by_serial) {
    if (abs(steering) <= boost_to_level * 0.9)
      steering = 0;

    if (abs(throttle) <= boost_to_level * 0.9)
      throttle = 0;
  }

  // If remote is off, take control using serial
  if (abs(throttle) > 260) {
    Serial.println("Long PWM, remote may be off.");
    Serial.write(SERIAL_INACTIVE);
    Serial.println();
    if (Serial.available() > 0 && controlled_by_serial == false) {
      controlled_by_serial = 1;
      Serial.println("Serial control activated.");
      throttle = 0;
      steering = 0;
    }
    return;
  }
  
  // Assign motor speeds
  motor_A_out = constrain(throttle - steering, -255, 255);
  motor_B_out = constrain(throttle + steering, -255, 255);


  Serial.println(motor_A_out);
  Serial.println(motor_B_out);
  Serial.println();


  // Write to motors
  if (motor_A_out > 0 && !motor_A_forwards) {
    motor_A_forwards = true;
    setDirection(MOTOR_A_P, MOTOR_A_N, true);
  }

  if (motor_A_out < 0 && motor_A_forwards) {
    motor_A_forwards = false;
    setDirection(MOTOR_A_P, MOTOR_A_N, false);
  }
    if (motor_B_out > 0 && !motor_B_forwards) {
    motor_B_forwards = true;
    setDirection(MOTOR_B_P, MOTOR_B_N, true);
  }

  if (motor_B_out < 0 && motor_B_forwards) {
    motor_B_forwards = false;
    setDirection(MOTOR_B_P, MOTOR_B_N, false);
  }
  analogWrite(MOTOR_A_EN, abs(motor_A_out));
  analogWrite(MOTOR_B_EN, abs(motor_B_out));
}
