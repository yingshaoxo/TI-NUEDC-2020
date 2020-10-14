#include <SoftwareSerial.h>   //Software Serial Port
#include <OS_SerialTFT.h>   //Software Serial Port

#define TFT_RX 4//RX of Serial TFT module connect to D4 of Arduino / OPEN-SMART UNO
#define TFT_TX 2//TX of Serial TFT to D2
SerialTFT myTFT(TFT_RX, TFT_TX);

void setup() {
	myTFT.begin(9600);
	myTFT.reset();
	myTFT.setBacklight(200);//0~255
	delay(2000);
	
	myTFT.fillScreen(BLACK);
	myTFT.bmpDraw("Minions");
	myTFT.setTextSize(2);
	myTFT.setTextColor(YELLOW);
	myTFT.setCursor(140, 20);
	myTFT.print("Name: Bob");
	myTFT.setCursor(140, 40);
	myTFT.print("Height: 45cm");
	myTFT.setCursor(140, 60);
	myTFT.print("Weight: 9.8kg");
	myTFT.setCursor(140, 80);
	myTFT.print("Features: timid");
	
	delay(2000);
	
	myTFT.fillScreen(BLACK);
	myTFT.bmpDraw("Spiderma");//Only support 8 charactors for Spiderman
	myTFT.setCursor(140, 20);
	myTFT.print("Name: Spiderman");
	myTFT.setCursor(140, 40);
	myTFT.print("Height: 178cm");
	myTFT.setCursor(140, 60);
	myTFT.print("Weight: 76kg");
	myTFT.setCursor(140, 80);
	myTFT.print("Features: agile");
	delay(2000);
	
	myTFT.fillScreen(BLACK);
	myTFT.bmpDraw("003");//display 004.bmp in the TF card
	delay(2000);
	myTFT.fillScreen(BLACK);
	myTFT.bmpDraw("004");//display 005.bmp in the TF card
}

void loop() {
 
}

