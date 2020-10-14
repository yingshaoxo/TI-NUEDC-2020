#include <SoftwareSerial.h>   //Software Serial Port
#include <OS_SerialTFT.h>   //Software Serial Port

#define TFT_RX 4//RX of Serial TFT module connect to D4 of Arduino / OPEN-SMART UNO
#define TFT_TX 2//TX of Serial TFT to D2
SerialTFT myTFT(TFT_RX, TFT_TX);

void setup() {
  
  
	myTFT.begin(9600);
	myTFT.reset();
	myTFT.setBacklight(150);//0~255
	delay(2000);
	testText();
	delay(2000);
    testRects(GREEN);
	delay(2000);
 	testLines(CYAN);
 	delay(2000);
 	testFastLines(RED, BLUE);
	delay(2000);
	testFilledRects(YELLOW, MAGENTA);
	delay(2000);
	testFilledCircles(10, MAGENTA);
	delay(2000);
	testCircles(10, WHITE);
	delay(2000);
	testTriangles();
	delay(2000);
	testFilledTriangles();
	delay(2000);
	testRoundRects();
	delay(2000);
	testFilledRoundRects();
}

void loop() {
 
}


void testLines(uint16_t color) {
  unsigned long start, t;
  int           x1, y1, x2, y2,
                w = 320,
                h = 240;

  myTFT.fillScreen(BLACK);
  

  x1 = y1 = 0;
  y2    = h - 1;
  
  for(x2=0; x2<w; x2+=6) myTFT.drawLine(x1, y1, x2, y2, color);
  x2    = w - 1;
  for(y2=0; y2<h; y2+=6) myTFT.drawLine(x1, y1, x2, y2, color);


  myTFT.fillScreen(BLACK);

  x1    = w - 1;
  y1    = 0;
  y2    = h - 1;

  for(x2=0; x2<w; x2+=6) myTFT.drawLine(x1, y1, x2, y2, color);
  x2    = 0;
  for(y2=0; y2<h; y2+=6) myTFT.drawLine(x1, y1, x2, y2, color);


  myTFT.fillScreen(BLACK);

  x1    = 0;
  y1    = h - 1;
  y2    = 0;
  for(x2=0; x2<w; x2+=6) myTFT.drawLine(x1, y1, x2, y2, color);
  x2    = w - 1;
  for(y2=0; y2<h; y2+=6) myTFT.drawLine(x1, y1, x2, y2, color);


  myTFT.fillScreen(BLACK);

  x1    = w - 1;
  y1    = h - 1;
  y2    = 0;

  for(x2=0; x2<w; x2+=6) myTFT.drawLine(x1, y1, x2, y2, color);
  x2    = 0;
  for(y2=0; y2<h; y2+=6) myTFT.drawLine(x1, y1, x2, y2, color);

}
void testFastLines(uint16_t color1, uint16_t color2) {

  int           x, y, w = 320, h = 240;
  myTFT.fillScreen(BLACK);
  for(y=0; y<h; y+=5) myTFT.drawFastHLine(0, y, w, color1);
  for(x=0; x<w; x+=5) myTFT.drawFastVLine(x, 0, h, color2);

}

void testFilledRects(uint16_t color1, uint16_t color2) {
  int           n, i, i2,
                cx = 320  / 2 - 1,
                cy = 240 / 2 - 1;

  myTFT.fillScreen(BLACK);
  n = 240;
  for(i=n; i>0; i-=6) {
    i2    = i / 2;

    myTFT.fillRect(cx-i2, cy-i2, i, i, color1);
    // Outlines are not included in timing results
    myTFT.drawRect(cx-i2, cy-i2, i, i, color2);
  }
}

void testFilledCircles(uint8_t radius, uint16_t color) {
  int x, y, w = 320, h = 240, r2 = radius * 2;

  myTFT.fillScreen(BLACK);
  for(x=radius; x<w; x+=r2) {
    for(y=radius; y<h; y+=r2) {
      myTFT.fillCircle(x, y, radius, color);
    }
  }
}

void testCircles(uint8_t radius, uint16_t color) {
  int           x, y, r2 = radius * 2,
                w = 320  + radius,
                h = 240 + radius;

  // Screen is not cleared for this one -- this is
  // intentional and does not affect the reported time.
  for(x=0; x<w; x+=r2) {
    for(y=0; y<h; y+=r2) {
      myTFT.drawCircle(x, y, radius, color);
    }
  }
}

void testText() {
	myTFT.fillScreen(BLACK);
  myTFT.setCursor(0, 0);
  myTFT.setTextColor(YELLOW); 
	myTFT.setTextSize(2);
  myTFT.print("1234.56");
	myTFT.println();
	myTFT.print("1 + 1 = 2");
	myTFT.println();
  myTFT.setTextColor(RED);    
	myTFT.setTextSize(3);
  uint16_t a = 0xABCD;
  myTFT.print(a,HEX);
  myTFT.println();
  myTFT.setTextColor(GREEN);
  myTFT.print("OPEN-SMART TFT");
	myTFT.println();
}

void testRects(uint16_t color) {
  int           n, i, i2,
                cx = 320 / 2,
                cy = 240 / 2;

  myTFT.fillScreen(BLACK);
  n     = min(320, 240);
  for(i=2; i<n; i+=6) {
    i2 = i / 2;
    myTFT.drawRect(cx-i2, cy-i2, i, i, color);
  }

}
void testTriangles() {

  int           n, i, cx = 320  / 2 - 1,
                      cy = 240 / 2 - 1;

  myTFT.fillScreen(BLACK);
  n     = min(cx, cy);

  for(i=0; i<n; i+=5) {
    myTFT.drawTriangle(
      cx    , cy - i, // peak
      cx - i, cy + i, // bottom left
      cx + i, cy + i, // bottom right
      myTFT.color565(0, 0, i));
  }

}

void testFilledTriangles() {
  int           i, cx = 320  / 2 - 1,
                   cy = 240 / 2 - 1;

  myTFT.fillScreen(BLACK);
  for(i=min(cx,cy); i>10; i-=5) {
    myTFT.fillTriangle(cx, cy - i, cx - i, cy + i, cx + i, cy + i,
      myTFT.color565(0, i, i));
    myTFT.drawTriangle(cx, cy - i, cx - i, cy + i, cx + i, cy + i,
      myTFT.color565(i, i, 0));
  }

}

void testRoundRects() {
  int           w, i, i2,
                cx = 320 / 2 - 1,
                cy = 240 / 2 - 1;

  myTFT.fillScreen(BLACK);
  w     = 240;

  for(i=0; i<w; i+=6) {
    i2 = i / 2;
    myTFT.drawRoundRect(cx-i2, cy-i2, i, i, i/8, myTFT.color565(i, 0, 0));
  }

}

void testFilledRoundRects() {
  int           i, i2,
                cx = 320 / 2 - 1,
                cy = 240 / 2 - 1;

  myTFT.fillScreen(BLACK);
  for(i=240; i>20; i-=6) {
    i2 = i / 2;
    myTFT.fillRoundRect(cx-i2, cy-i2, i, i, i/8, myTFT.color565(0, i, 0));
  }

}

