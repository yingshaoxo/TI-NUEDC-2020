#include <SoftwareSerial.h>   //Software Serial Port
#include <OS_SerialTFT.h>   //Software Serial Port

#define TFT_RX 4//RX of Serial TFT module connect to D4 of Arduino / OPEN-SMART UNO
#define TFT_TX 2//TX of Serial TFT to D2
SerialTFT myTFT(TFT_RX, TFT_TX);

#define TS_MINX  140
#define TS_MINY  130
#define TS_MAXX  925
#define TS_MAXY  950

#define BOXSIZE   40
#define PENRADIUS  3
int oldcolor, currentcolor;

void setup(void) {
  Serial.begin(9600);
  myTFT.begin(9600);
  myTFT.reset();
  myTFT.fillScreen(BLACK);
  myTFT.fillRect(0, 0, BOXSIZE, BOXSIZE, RED);
  myTFT.fillRect(BOXSIZE, 0, BOXSIZE, BOXSIZE, YELLOW);
  myTFT.fillRect(BOXSIZE*2, 0, BOXSIZE, BOXSIZE, GREEN);
  myTFT.fillRect(BOXSIZE*3, 0, BOXSIZE, BOXSIZE, CYAN);
  myTFT.fillRect(BOXSIZE*4, 0, BOXSIZE, BOXSIZE, BLUE);
  myTFT.fillRect(BOXSIZE*5, 0, BOXSIZE, BOXSIZE, MAGENTA);
  myTFT.fillRect(BOXSIZE*6, 0, BOXSIZE, BOXSIZE, WHITE); 
  myTFT.drawLine(BOXSIZE*6, 0,BOXSIZE*6+39,39,BLACK);
  myTFT.drawLine(BOXSIZE*6, 39,BOXSIZE*6+39,0,BLACK);
  
  
  myTFT.drawRect(0, 0, BOXSIZE, BOXSIZE, WHITE);
  currentcolor = RED;
 
}


void loop()
{
  if (myTFT.touch()) 
  {
    Serial.print("X = "); Serial.print(myTFT.touchX);
    Serial.print("\tY = "); Serial.println(myTFT.touchY);
    
    if (myTFT.touchY < (TS_MINY-5)) {
      Serial.println("erase");
      // press the bottom of the screen to erase 
      myTFT.fillRect(0, BOXSIZE, 320, 320-BOXSIZE, BLACK);
    }
    // scale from 0->1023 to tft.width
    uint16_t temp = myTFT.touchX;
    myTFT.touchX = map(myTFT.touchY, TS_MINY, TS_MAXY, 320, 0);
    myTFT.touchY= map(temp, TS_MINX, TS_MAXX, 0, 240);
    /*
    Serial.print("("); Serial.print(p.x);
    Serial.print(", "); Serial.print(p.y);
    Serial.println(")");
    */
    if (myTFT.touchY < BOXSIZE) {
       oldcolor = currentcolor;

       if (myTFT.touchX < BOXSIZE) { 
         currentcolor = RED; 
         myTFT.drawRect(0, 0, BOXSIZE, BOXSIZE, WHITE);
       } else if (myTFT.touchX < BOXSIZE*2) {
         currentcolor = YELLOW;
         myTFT.drawRect(BOXSIZE, 0, BOXSIZE, BOXSIZE, WHITE);
       } else if (myTFT.touchX < BOXSIZE*3) {
         currentcolor = GREEN;
         myTFT.drawRect(BOXSIZE*2, 0, BOXSIZE, BOXSIZE, WHITE);
       } else if (myTFT.touchX < BOXSIZE*4) {
         currentcolor = CYAN;
         myTFT.drawRect(BOXSIZE*3, 0, BOXSIZE, BOXSIZE, WHITE);
       } else if (myTFT.touchX < BOXSIZE*5) {
         currentcolor = BLUE;
         myTFT.drawRect(BOXSIZE*4, 0, BOXSIZE, BOXSIZE, WHITE);
       } else if (myTFT.touchX < BOXSIZE*6) {
         currentcolor = MAGENTA;
         myTFT.drawRect(BOXSIZE*5, 0, BOXSIZE, BOXSIZE, WHITE);
       }
	   else if (myTFT.touchX < BOXSIZE*7) {
	   	myTFT.fillRect(0, BOXSIZE, 320, 320-BOXSIZE, BLACK);// press the bottom of the screen to erase 
	   	}

       if (oldcolor != currentcolor) {
          if (oldcolor == RED) myTFT.fillRect(0, 0, BOXSIZE, BOXSIZE, RED);
          if (oldcolor == YELLOW) myTFT.fillRect(BOXSIZE, 0, BOXSIZE, BOXSIZE, YELLOW);
          if (oldcolor == GREEN) myTFT.fillRect(BOXSIZE*2, 0, BOXSIZE, BOXSIZE, GREEN);
          if (oldcolor == CYAN) myTFT.fillRect(BOXSIZE*3, 0, BOXSIZE, BOXSIZE, CYAN);
          if (oldcolor == BLUE) myTFT.fillRect(BOXSIZE*4, 0, BOXSIZE, BOXSIZE, BLUE);
          if (oldcolor == MAGENTA) myTFT.fillRect(BOXSIZE*5, 0, BOXSIZE, BOXSIZE, MAGENTA);
       }
    }
    if (((myTFT.touchY-PENRADIUS) > BOXSIZE) && ((myTFT.touchY+PENRADIUS) < 240)) {
      myTFT.fillCircle(myTFT.touchX, myTFT.touchY, PENRADIUS, currentcolor);
    }
  }
}
