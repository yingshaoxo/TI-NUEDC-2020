#ifndef _OS_SERIALTFT_H__
#define _OS_SERIALTFT_H__

#include <SoftwareSerial.h>
#include <Arduino.h>

#define	BLACK   0x0000
#define	BLUE    0x001F
#define	RED     0xF800
#define	GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF
////////////////////////////////////
#define TEST_CMD 0X00
#define SET_READ_CURSOR 0X01
#define SET_TEXTCOLOR 0X02
#define SET_TEXTSIZE 0X03
#define SET_ROTATION 0X04
#define RESET 0X05
#define SET_BACKLIGHT 0X06
#define READ_TOUCH 0X07

#define PRINTLN 0x10
#define PRINT_CHAR_ARRAY 0X11
#define PRINT_INT_8 0X12
#define PRINT_INT_16 0X13
#define PRINT_INT_32 0X14


#define FILL_SREEN 0X20
#define DRAW_PIXEL 0X21
#define DRAW_FASTVLINE 0X22
#define DRAW_FASTHLINE 0X23
#define DRAW_LINE 0X24
#define DRAW_RECT 0X25
#define FILL_RECT 0X26
#define DRAW_CIRCLE 0X27
#define FILL_CIRCLE 0X28
#define DRAW_TRIANGLE 0X29
#define FILL_TRIANGLE 0X2A
#define DRAW_ROUNDRECT 0X2B
#define FILL_ROUNDRECT 0X2C

#define DRAW_BMP 0X30

#define WRITE_READ_BAUD 0X40
#define READ_VERSION 0X41
#define READ_DRIVER_ID 0X42
#define READ_RESOLUTION 0X43

////////////////////////////////////////////

#define FEEDBACK_OK 0x6F
#define FEEDBACK_E1 0x65
#define FEEDBACK_E2 0x66

#define SIGNED 1
#define UNSIGNED 0



class SerialTFT
{
public:
	SerialTFT(uint8_t rxd, uint8_t txd);
	void begin(long speed);
	uint8_t checkFeedback();
	uint8_t findStartByte();
	void sendCommand(char cmd[], uint8_t length);
	inline void sendByte(uint8_t dat);
	void test();
	void setCursor(int16_t x, int16_t y);
	void readCursor(int16_t &x, int16_t &y);
	void setTextColor(uint16_t color);
	void setTextSize(uint8_t size) ;
	void setRotation(uint8_t rota); //rota = 0, 1, 2, 3
	void reset();
	void setBacklight(uint8_t bightness);
	void println();
	void print(const char str[]);
	void print(int8_t c);
	void print(uint8_t b, uint8_t base = DEC);
	void print(int16_t n);
	void print(uint16_t n, uint8_t base = DEC);
	void print(int32_t n);
	void print(uint32_t n, uint8_t base = DEC);
	
	void println(const char str[]);
	void println(int8_t c);
	void println(uint8_t b, uint8_t base = DEC);
	void println(int16_t n);
	void println(uint16_t n, uint8_t base = DEC);
	void println(int32_t n);
	void println(uint32_t n, uint8_t base = DEC);
	
	void fillScreen(uint16_t color);
	void drawPixel(int16_t x, int16_t y, uint16_t color);
	void drawFastHLine(int16_t x0, int16_t y0, int16_t w, uint16_t color);
	void drawFastVLine(int16_t x0, int16_t y0, int16_t h, uint16_t color);
	void drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
			uint16_t color);
	void drawRect(int16_t x, int16_t y, int16_t w, int16_t h,
			uint16_t color);
	void fillRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color);
	void drawCircle(int16_t x0, int16_t y0, int16_t r, uint16_t color);
	void fillCircle(int16_t x0, int16_t y0, int16_t r, uint16_t color);
	void drawTriangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
		  int16_t x2, int16_t y2, uint16_t color);
	void fillTriangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
		  int16_t x2, int16_t y2, uint16_t color);
	void drawRoundRect(int16_t x0, int16_t y0, int16_t w, int16_t h,
		  int16_t r, uint16_t color);
	void fillRoundRect(int16_t x0, int16_t y0, int16_t w, int16_t h,
		  int16_t r, uint16_t color);
	void bmpDraw(char *filename);
	uint16_t color565(uint8_t r, uint8_t g, uint8_t b);
	uint8_t touch();
	uint16_t touchX, touchY;
private:
	SoftwareSerial myTFT;
	char feedbackBuf[6];
	
};

#endif
