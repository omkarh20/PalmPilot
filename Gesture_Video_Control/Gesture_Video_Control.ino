// === Pin Configuration ===
const int trigger1 = 8;     // Ultrasonic sensor 1 (left) trigger pin
const int echo1 = 9;        // Ultrasonic sensor 1 (left) echo pin
const int trigger2 = 3;     // Ultrasonic sensor 2 (right) trigger pin
const int echo2 = 4;        // Ultrasonic sensor 2 (right) echo pin
const int irSensor = 10;    // IR sensor pin
const int toggleButton = 2; // Push button pin to toggle gesture control

// === State Variables ===
bool gestureEnabled = false;           // Keeps track of whether gesture mode is ON
bool buttonState;                      // Stores the current button state
bool lastReading = HIGH;               // Last read value from button (for debouncing)
unsigned long lastDebounceTime = 0;    // Time of last button state change
const unsigned long debounceDelay = 50; // Debounce time in ms

// === Distance Measurement ===
long time_taken;
int dist, distL, distR; // Distance: temp, left, right

// === Swipe Detection Variables ===
unsigned long lastSwipeTime = 0;              // Time of last swipe detection
const int swipeDistanceThresholdMin = 33;     // Minimum distance for swipe to be valid
const int swipeDistanceThresholdMax = 48;     // Maximum distance for swipe
const int swipeTimeout = 1000;                // Max time allowed between left and right triggers (ms)
bool leftTriggered = false;
bool rightTriggered = false;

void setup() {
  Serial.begin(9600);                         // Initialize serial communication
  pinMode(toggleButton, INPUT_PULLUP);       // Button uses internal pull-up resistor
  pinMode(trigger1, OUTPUT);
  pinMode(echo1, INPUT);
  pinMode(trigger2, OUTPUT);
  pinMode(echo2, INPUT);
  pinMode(irSensor, INPUT);
}

// Calculates distance using ultrasonic sensor
void calculate_distance(int trigger, int echo) {
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
  time_taken = pulseIn(echo, HIGH);         // Measure echo duration
  dist = time_taken * 0.034 / 2;            // Convert time to distance in cm
  if (dist > 60) dist = 60;                 // Cap max distance to 60 cm
}

void loop() {
  // === Toggle Gesture Control On/Off ===
  int reading = digitalRead(toggleButton);
  if (reading != lastReading) {
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == LOW) {
        gestureEnabled = !gestureEnabled;
        Serial.print("Gesture control ");
        Serial.println(gestureEnabled ? "ENABLED" : "DISABLED");
      }
    }
  }
  lastReading = reading;

  // If gesture control is off, skip loop
  if (!gestureEnabled) {
    delay(50);
    return;
  }

  // === IR Sensor: Momentary vs LongHold ===
  if (digitalRead(irSensor) == LOW) {
    unsigned long startTime = millis();
    while (digitalRead(irSensor) == LOW && (millis() - startTime) < 3000) {
      delay(10);
    }
    unsigned long duration = millis() - startTime;
    if (duration < 400) {
      Serial.println("Momentary");
    } else {
      Serial.println("LongHold");
    }
    delay(300);
  }

  // === Distance Measurement (Left & Right) ===
  calculate_distance(trigger1, echo1);
  distL = dist;
  calculate_distance(trigger2, echo2);
  distR = dist;
  Serial.print("L=");
  Serial.println(distL);
  Serial.print("R=");
  Serial.println(distR);

  // === LEFT HAND PUSH/PULL DETECTION ===
  if (distL >= 15 && distL <= 35) {
    delay(100);
    calculate_distance(trigger1, echo1);
    distL = dist;
    if (distL >= 15 && distL <= 35) {
      Serial.println("Left Locked");
      while (distL <= 50) {
        calculate_distance(trigger1, echo1);
        distL = dist;
        if (distL < 12) {
          Serial.println("Lpush");
          delay(300);
        }
        if (distL > 32) {
          Serial.println("Lpull");
          delay(300);
        }
      }
    }
  }

  // === RIGHT HAND PUSH/PULL DETECTION ===
  if (distR >= 15 && distR <= 35) {
    delay(100);
    calculate_distance(trigger2, echo2);
    distR = dist;
    if (distR >= 15 && distR <= 35) {
      Serial.println("Right Locked");
      while (distR <= 50) {
        calculate_distance(trigger2, echo2);
        distR = dist;
        if (distR < 12) {
          Serial.println("Rpush");
          delay(300);
        }
        if (distR > 32) {
          Serial.println("Rpull");
          delay(300);
        }
      }
    }
  }

  // === SWIPE LEFT-RIGHT AND RIGHT-LEFT DETECTION ===
  unsigned long currentTime = millis();

  // Step 1: Left Trigger Detected
  if (distL >= swipeDistanceThresholdMin && distL <= swipeDistanceThresholdMax && !leftTriggered) {
    Serial.println("Left detected");
    leftTriggered = true;
    lastSwipeTime = currentTime;
  }

  // Step 2: Followed by Right Trigger = LEFT TO RIGHT SWIPE
  if (leftTriggered && distR >= swipeDistanceThresholdMin && distR <= swipeDistanceThresholdMax && (currentTime - lastSwipeTime < swipeTimeout)) {
    Serial.println("Swipe_Left_Right");
    leftTriggered = false;
    rightTriggered = false;
    delay(700);
    return;
  }

  // Step 3: Right Trigger Detected First
  if (distR >= swipeDistanceThresholdMin && distR <= swipeDistanceThresholdMax && !rightTriggered) {
    Serial.println("Right detected");
    rightTriggered = true;
    lastSwipeTime = currentTime;
  }

  // Step 4: Followed by Left Trigger = RIGHT TO LEFT SWIPE
  if (rightTriggered && distL >= swipeDistanceThresholdMin && distL <= swipeDistanceThresholdMax && (currentTime - lastSwipeTime < swipeTimeout)) {
    Serial.println("Swipe_Right_Left");
    rightTriggered = false;
    leftTriggered = false;
    delay(700);
  }

  // Reset swipe flags if timeout exceeded
  if (currentTime - lastSwipeTime > swipeTimeout) {
    leftTriggered = false;
    rightTriggered = false;
  }

  delay(50); // Slight delay to smooth sensor polling
}
