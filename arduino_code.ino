#define RELAY_PIN       4
#define ACCESS_DELAY    10000 // Keep lock unlocked for 10 seconds 

//ldr and bulb control pins
const int ledPin=13;
const int ldrPin=A5; //analog input

unsigned long previousMillis = 0;  // variable to store the previous time
const long interval = 1000;  // interval to wait for (in milliseconds)

void setup()
{
  Serial.begin(9600);
  
  pinMode(ledPin,OUTPUT);
  pinMode(ldrPin,INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);
}
void loop()
{
   unsigned long currentMillis = millis();  // get the current time
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;  // save the current time for the next interval
    //Control Bulb based on LDR
  int ldrStatus=analogRead(ldrPin);
  Serial.println(ldrStatus);
  if(ldrStatus<=100)   //when it's dark less conductivity(low voltage)
  {
    digitalWrite(ledPin,1);
    Serial.println("Dark outside, Bulb is ON");
  }
  else
  {
    digitalWrite(ledPin,0);
    Serial.println("Bright outside");
  }
  }
    //Unlock and lock door(servo motor mechanism) based on Face Recognition
  if(Serial.available())
  {
    char char_data=Serial.read(); //read one byte from serial buffer and save it to the variable
    if(char_data=='o')
    {
      openlock();
    }
    else if(char_data=='c')
    {
      closelock();
    }
    delay(1);
  }  
}

void openlock()
{
  if(digitalRead(RELAY_PIN)==LOW)
  {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("DOOR OPEN");
    delay(ACCESS_DELAY);
    digitalWrite(RELAY_PIN, LOW);
  }
  else
  {
    Serial.println("DOOR ALREADY OPEN");
  }
}

void closelock()
{
  if(digitalRead(RELAY_PIN)==HIGH)
  {
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Door CLOSED");
  }
  else
  {
    Serial.println("DOOR ALREADY CLOSED");
  }
}
