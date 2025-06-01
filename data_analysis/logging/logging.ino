// Sensor pins
const int trigger1 = 8;
const int echo1 = 9;
const int trigger2 = 3;
const int echo2 = 4;
const int irSensor = 10;
const int toggleButton = 2;

// System states
char gesture[30];
char buf[64];
int irTriggered = 1;
bool gestureEnabled = false;
bool buttonState;
bool lastReading = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

long time_taken;
int dist, distL, distR;

unsigned long lastSwipeTime = 0;
const int swipeDistanceThresholdMin = 38;
const int swipeDistanceThresholdMax = 48;
const int swipeTimeout = 1000;
bool leftTriggered = false;
bool rightTriggered = false;

void setup() {
  Serial.begin(9600);
  pinMode(toggleButton, INPUT_PULLUP);
  pinMode(trigger1, OUTPUT);
  pinMode(echo1, INPUT);
  pinMode(trigger2, OUTPUT);
  pinMode(echo2, INPUT);
  pinMode(irSensor, INPUT);
}

void calculate_distance(int trigger, int echo) {
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
  time_taken = pulseIn(echo, HIGH);
  dist = time_taken * 0.034 / 2;
  if (dist > 60) dist = 60;
}

void loop() {
  //Toggle Button
  int reading = digitalRead(toggleButton);
  if (reading != lastReading) {
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == LOW) {
        gestureEnabled = !gestureEnabled;
        //Serial.print("Gesture control ");
        //Serial.println(gestureEnabled ? "ENABLED" : "DISABLED");
      }
    }
  }
  lastReading = reading;

  if (!gestureEnabled) {
    delay(50);
    return;
  }

  //Infrared 
  if (digitalRead(irSensor) == LOW) {
    
    unsigned long startTime = millis();

    while (digitalRead(irSensor) == LOW && (millis() - startTime) < 3000) {
      delay(10);
    }

    unsigned long duration = millis() - startTime;

    if (duration < 400) {
      strcpy(gesture, "Momentary");
      //Serial.println("Momentary");
    } else {
      strcpy(gesture, "LongHold");
      //Serial.println("LongHold");
    }
    calculate_distance(trigger1, echo1);
    distL = dist;
    calculate_distance(trigger2, echo2);
    distR = dist;
    irTriggered = 0;
    snprintf(buf, sizeof(buf), "%s,%d,%d,%d",
      gesture,
      distL,
      distR,
      irTriggered);
    Serial.println(buf);
    irTriggered = 1;
    delay(700);
  }


  calculate_distance(trigger1, echo1);
  distL = dist;
  calculate_distance(trigger2, echo2);
  distR = dist;

  /*Serial.print("L=");
  Serial.println(distL);
  Serial.print("R=");
  Serial.println(distR);
  */

  // ==== LEFT HAND LOCK GESTURES ====
  if (distL >= 15 && distL <= 35) {
    delay(100);
    calculate_distance(trigger1, echo1);
    distL = dist;

    if (distL >= 15 && distL <= 35) {
      //Serial.println("Left Locked");
      while (distL <= 50) {
        calculate_distance(trigger1, echo1);
        distL = dist;
        if (distL < 12) {
          strcpy(gesture, "Lpush");
          //Serial.println("Lpush");
          delay(300);
        }
        if (distL > 32) {
          strcpy(gesture, "Lpull");
          //Serial.println("Lpull");
          delay(300);
        }

        snprintf(buf, sizeof(buf), "%s,%d,%d,%d",
          gesture,
          distL,
          distR,
          irTriggered);
        Serial.println(buf);
      }
    }
  }

  // ==== RIGHT HAND LOCK GESTURES ====
  if (distR >= 15 && distR <= 35) {
    delay(100);
    calculate_distance(trigger2, echo2);
    distR = dist;

    if (distR >= 15 && distR <= 35) {
      //Serial.println("Right Locked");
      while (distR <= 50) {
        calculate_distance(trigger2, echo2);
        distR = dist;
        if (distR < 12) {
          strcpy(gesture, "Rpush");
          //Serial.println("Rpush");
          delay(300);
        }
        if (distR > 32) {
          strcpy(gesture, "Rpull");
          delay(300);
        }
        snprintf(buf, sizeof(buf), "%s,%d,%d,%d",
          gesture,
          distL,
          distR,
          irTriggered);
        Serial.println(buf);
      }
    }
  }

  // ==== SWIPE DETECTION ====
  unsigned long currentTime = millis();

  if (distL >= swipeDistanceThresholdMin && distL <=swipeDistanceThresholdMax && !leftTriggered) {
    //Serial.println("Left detected");
    leftTriggered = true;
    lastSwipeTime = currentTime;
  }

  if (leftTriggered && distR >= swipeDistanceThresholdMin  && distR <=swipeDistanceThresholdMax && (currentTime - lastSwipeTime < swipeTimeout)) {
    strcpy(gesture, "Swipe_Left_Right");
    snprintf(buf, sizeof(buf), "%s,%d,%d,%d",
      gesture,
      distL,
      distR,
      irTriggered);
    Serial.println(buf);
    //Serial.println("Swipe_Left_Right");
    leftTriggered = false;
    rightTriggered = false;
    delay(700);
    return;
  }

  if (distR >= swipeDistanceThresholdMin && distR <=swipeDistanceThresholdMax && !rightTriggered) {
    //Serial.println("Right detected");
    rightTriggered = true;
    lastSwipeTime = currentTime;
  }

  if (rightTriggered && distL >= swipeDistanceThresholdMin && distL <=swipeDistanceThresholdMax && (currentTime - lastSwipeTime < swipeTimeout)) {
    strcpy(gesture, "Swipe_Right_Left");
    snprintf(buf, sizeof(buf), "%s,%d,%d,%d",
      gesture,
      distL,
      distR,
      irTriggered);
    Serial.println(buf);
    //Serial.println("Swipe_Right_Left");
    rightTriggered = false;
    leftTriggered = false;
    delay(700);
  }

  // Reset if timeout passed
  if (currentTime - lastSwipeTime > swipeTimeout) {
    leftTriggered = false;
    rightTriggered = false;
  }

  delay(50);
}
