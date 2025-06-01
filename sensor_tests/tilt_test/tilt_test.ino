const int tiltPin = 6;

void setup() {
  pinMode(tiltPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  int state = digitalRead(tiltPin);
  if (state == LOW) {
    Serial.println("Tilt Detected");
  } else {
    Serial.println("Not Tilted");
  }
  delay(500);
}
