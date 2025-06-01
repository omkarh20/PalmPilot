const int tiltPin = 6; // Tilt sensor connected to digital pin 6

void setup() {
  pinMode(tiltPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  int tiltState = digitalRead(tiltPin);

  if (tiltState == LOW) {
    Serial.println("Tilted");
  } else {
    Serial.println("Not tilted");
  }

  delay(200);
}
