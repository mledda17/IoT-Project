// Libraries required
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include "TickTwo.h"

// WiFi Credentials
#define SSID "Sam"
#define PASSWORD "12345678"

// MQTT Setup
const char* mqtt_server = "test.mosquitto.org";
//const char* mqtt_server = "broker.mqttdashboard.com";
const int mqtt_port = 1883;
#define SECRET_STRING "smartpot_9459019280"

// Serial number kit
#define SERIAL_NUMBER "ABCDEF1234567890"

// Client setup
WiFiClient espClient;
PubSubClient client(espClient);

// Server Setup
String server_url = "http://192.168.52.14:8080";

// Callback functions
void irrigate_plant();
void publish_measures();
void reset_timer();

#define debug 1
#define production 0

#define MODE 1

#if MODE == debug
#define millis_in_a_day 24000
#define measure_millis_interval 10000
#elif MODE == production
#define millis_in_a_day 86400000
#define measure_millis_interval 900000
#endif

bool time_settings_imposed = false;
int day_counter;
TickTwo hour_of_day(reset_timer, millis_in_a_day, 0, MILLIS);
TickTwo measurements_timer(publish_measures, measure_millis_interval, 0, MILLIS);
TickTwo watering_timer(irrigate_plant, millis_in_a_day/2, 0, MILLIS);

// Parameters
int watering_frequency;
float desired_soil_humidity;

#define watering_auth_max_attempt 5
#define threshold_h 30

// HTTP outcomes
#define SUCCESSFUL 0
#define FAILURE -1
#define DISCONNECTED -2
// HTTP Watering authorization
#define AUTHORIZED 1
#define UNAUTHORIZED 2

// PINS
#define DHT_PIN D2
#define DHT_TYPE DHT11
#define LIGHT_PIN A0
#define SOIL_PIN A0
#define RELAY_PIN D4

// Calibration values
const int MIN_VALUE = 300; // Replace with your minimum value (dry)
const int MAX_VALUE = 700; // Replace with your maximum value (wet)

// Sensors setup
DHT dht(DHT_PIN, DHT_TYPE);

// HTTP Requests
int authorize_watering() {
  if (WiFi.status() == WL_CONNECTED) {
    String url = server_url + "/authorize_watering/" + SERIAL_NUMBER;
    HTTPClient http;
    http.begin(espClient, url);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      #if MODE == debug
      Serial.println("Received payload: " + payload);
      #endif
      if (payload == "Unauthorized") {
        return UNAUTHORIZED;
      }
      return AUTHORIZED;
    } else {
      #if MODE == debug
      Serial.println("GET request failed");
      #endif
      return FAILURE;
    }
    http.end();
  } else {
    #if MODE == debug
    Serial.println("Not connected to WiFi");
    #endif
    return DISCONNECTED;
  }
}

int get_parameters() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = server_url + "/get_settings/" + SERIAL_NUMBER;
    http.begin(espClient, url);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      #if MODE == debug
      Serial.println("Received payload: " + payload);
      #endif
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, payload);
      watering_frequency = doc["watering_frequency"];
      desired_soil_humidity = doc["desired_humidity"];
      int hour = doc["hour"].as<String>().toInt();
      int minute = doc["minute"].as<String>().toInt();
      set_time(hour, minute);
      return SUCCESSFUL;
    } else {
      #if MODE == debug
      Serial.println("GET request failed");
      #endif
      return FAILURE;
    }
    http.end();
  } else {
    #if MODE == debug
    Serial.println("Not connected to WiFi");
    #endif
    return DISCONNECTED;
  }  
}

void publish_measures(){
  String message;
  message = readSensors();

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);

  float current_humidity = doc["soil_humidity"].as<String>().toFloat();

  if(desired_soil_humidity - current_humidity > threshold_h){ // IMPORTANT
    do_watering();
  }

  String dummy = "";
  String topic = dummy + SECRET_STRING + "/measurements";
  #if MODE == debug
  Serial.println(message);
  #endif
  client.publish(topic.c_str(), message.c_str());
}


void publish_watering(bool watering){
  String message;
  DynamicJsonDocument doc(1024);
  doc["serial_number"] = SERIAL_NUMBER;
  if(watering){
    doc["watering"] = "true";
  }
  else{
    doc["watering"] = "false";
  }
  serializeJson(doc, message);

  String dummy = "";
  String topic = dummy + SECRET_STRING + "/watering";
  #if MODE == debug
  Serial.println(message);
  #endif
  client.publish(topic.c_str(), message.c_str());
}

void do_watering(){
  #if MODE == debug
  Serial.println("I'm watering.");
  digitalWrite(RELAY_PIN, HIGH);
  delay(1000);
  digitalWrite(RELAY_PIN, LOW);
  #endif
  return;
}

void irrigate_plant(){
  int outcome;
  for(int i = 0; i < watering_auth_max_attempt; i++){
    outcome = authorize_watering();
    if(outcome != FAILURE) break;
  }

  switch(outcome){
    case AUTHORIZED:
      publish_watering(true);
      do_watering();
      break;
    case UNAUTHORIZED:
      #if MODE == debug
      Serial.println("Unauthorize watering");
      #endif
      publish_watering(false);
      break;
    case DISCONNECTED:
      check_wifi();
      irrigate_plant();
      break;
    case FAILURE:
      #if MODE == debug
      Serial.println("Authorize watering failure");
      #endif
      publish_watering(true);
      do_watering();
      break;
    default:
      return;
  }
}

void reset_timer(){
  day_counter++;
  #if MODE == debug
  Serial.println("New Day");
  Serial.println(day_counter);
  #endif

  if(time_settings_imposed){
    hour_of_day.stop();
    hour_of_day.interval(millis_in_a_day);
    hour_of_day.start();
    time_settings_imposed = false;
  }
  
  if(day_counter >= watering_frequency){
    watering_timer.stop();
    watering_timer.interval(millis_in_a_day/2);
    watering_timer.start();
    day_counter = 0;
  }else{
    watering_timer.stop();
  }
}

void set_time(int hour, int minute){
  time_settings_imposed = true;
  hour_of_day.stop();
  watering_timer.stop();
  #if MODE == debug
  Serial.println("Setting time");
  int current_timer_millis = hour * 1000;
  #elif MODE == production
  int current_time_millis = (hour * 3600 * 1000) + (minute * 60 * 1000);
  #endif
  int timer_millis = millis_in_a_day - current_timer_millis;
  hour_of_day.interval(timer_millis);
  hour_of_day.start();
  if(day_counter >= watering_frequency){
    if(current_timer_millis - (millis_in_a_day/2) > 0){
      // resuming watering timer to his previous state, such that it'll water at the scheduled hour (at around 12)
      watering_timer.interval(current_timer_millis - (millis_in_a_day/2));
      watering_timer.start();
    }
    day_counter = 0;
  }
}

void MQTT_callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) { 
    message += (char)payload[i]; 
  }
  
  #if MODE == debug
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.println("]");
  Serial.println(message);
  #endif

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  watering_frequency = doc["watering_frequency"];
  desired_soil_humidity = doc["desired_humidity"];
  int hour = doc["hour"].as<String>().toInt();
  int minute = doc["minute"].as<String>().toInt();
  set_time(hour, minute);
}

void setup_wifi() {
  #if MODE == debug
  Serial.println();
  Serial.print("Connecting to");
  Serial.print(SSID);
  #endif
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    #if MODE == debug
    Serial.print(".");
    #endif
  }
  #if MODE == debug
  Serial.println("");
  Serial.println("WiFi Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  #endif

  int outcome = get_parameters();
  if(outcome == FAILURE){
    do{
      outcome = get_parameters();
    }while(outcome == FAILURE);
  }else if(outcome == DISCONNECTED){
    check_wifi();
  }
}

void check_wifi() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }
}

void setup_MQTT() {
  while (!client.connected()) {
    #if MODE == debug
    Serial.println("Attempting MQTT connection...");
    #endif
    String clientId = "ESP8266-";
    clientId += String(random(0xffff), HEX);

    
    if (client.connect(clientId.c_str())) {
      #if MODE == debug
      Serial.println("Connected");
      #endif
    } else {
      #if MODE == debug
      Serial.print("Failed, rc=");
      Serial.println(client.state());
      Serial.println("Try again now");
      #endif
    }
   
  }

  String dummy = "";
  String topic = dummy + SECRET_STRING + "/update_pot_setting/" + SERIAL_NUMBER;
  client.subscribe(topic.c_str());
}

void check_MQTT(){
  if(!client.connected()){
    setup_MQTT();
  }
}

String readSensors() {
  String message;

  float air_humidity = dht.readHumidity();
  float air_temperature = dht.readTemperature();
  int light = analogRead(LIGHT_PIN);
  int soil_humidity = analogRead(SOIL_PIN);

  // Map the analog value between 0 and 100 %
  soil_humidity = map(soil_humidity, MIN_VALUE, MAX_VALUE, 0, 100);
  soil_humidity = constrain(soil_humidity, 0, 100);

  // Map the value of light between 0 and 100 %
  light = 100 - map(light, 0, 1023, 0, 100);

  DynamicJsonDocument doc(1024);
  doc["air_humidity"] = air_humidity;
  doc["air_temperature"] = air_temperature;
  doc["light"] = light;
  doc["soil_humidity"] = soil_humidity;
  doc["serial_number"] = SERIAL_NUMBER;
  serializeJson(doc, message);
  return message;
}

void setup() {
  #if MODE == debug
  Serial.begin(9600);
  #endif
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(MQTT_callback);
  setup_MQTT();
  hour_of_day.start();
  measurements_timer.start();
  watering_timer.start();
}

void loop() {
  check_wifi();
  check_MQTT();
  client.loop();
  client.loop();
  //publish_watering(false);
  hour_of_day.update();
  measurements_timer.update();
  watering_timer.update();
}
