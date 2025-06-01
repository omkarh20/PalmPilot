int irPin = 7;

void setup() {
  pinMode(irPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  int irValue = digitalRead(irPin);
  Serial.println(irValue);
  delay(200);
}
