#include <SoftwareSerial.h>
#include "OS_SerialTFT.h"

SerialTFT::SerialTFT(uint8_t rxd, uint8_t txd):myTFT(txd, rxd)
{
  
}
void SerialTFT::begin(long speed)
{
  myTFT.begin(speed);
}
uint8_t SerialTFT::checkFeedback()
{
	uint16_t timeout = 318;//318*15.72=5000us = 5ms
	while(!myTFT.available())//one loop is about 15.72us
	{
		timeout--;
		if(!timeout) return 0;
	}
	
	char len;
	if(findStartByte())
	{
	  len = myTFT.read();
	}
	else return 0;//
	
    
	for(uint8_t i = 0;i < len;i++)
	{
		feedbackBuf[i] = myTFT.read();
		delay(2);
	}
	if(feedbackBuf[len-1] == (char)0xEF)
	{
		if((feedbackBuf[0] == 'o')&&(feedbackBuf[1] == 'k'))
			return FEEDBACK_OK;
		else if((feedbackBuf[0] == 'e')&&(feedbackBuf[1] == '1'))
			return FEEDBACK_E1;
		else if((feedbackBuf[0] == 'e')&&(feedbackBuf[1] == '2'))
			return FEEDBACK_E2;
		else return feedbackBuf[0];
	}
	else return 0;
	
}
uint8_t SerialTFT::findStartByte()
{
	char StartByte = 0;//
	while(myTFT.available())
	{
	  char dat;
	  dat = myTFT.read();
	  delay(2);
	  if(dat == 0x7E)
	  {
		StartByte = dat;
		break;//find the Start Byte;
	  }
	}
	if(StartByte == 0x7E) return 1;
	else return 0;
}
/**********************************************/
void SerialTFT::sendCommand(char cmd[], uint8_t length)
{
  char dat[length+3];
  dat[0] = 0x7e;
  dat[1] = length+1;
  for(uint8_t i = 0; i< length; i++)
  {
    dat[i+2] = cmd[i];
  }
  dat[length+2] = 0xef;
  for(uint8_t i = 0; i< length+3; i++)
  {
    sendByte(dat[i]);
  }
}

/**************************************/
//this is the line you should modify to match you MCU system.
inline void SerialTFT::sendByte(uint8_t dat)
{
	myTFT.write(dat);
}
/*************************************/

//----------------------------------------
void SerialTFT::test()
{
    char temp[1];
	temp[0] = TEST_CMD;
	sendCommand(temp,1);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::setCursor(int16_t x, int16_t y)
{
	char temp[5];
	temp[0] = SET_READ_CURSOR;
	temp[1] = x>>8;
	temp[2] = x;
	temp[3] = y>>8;
	temp[4] = y;
	sendCommand(temp,5);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::readCursor(int16_t &x, int16_t &y)
{
	char temp[1];
	temp[0] = SET_READ_CURSOR;
	sendCommand(temp,1);
	while(checkFeedback()!=SET_READ_CURSOR);
	x = ((uint8_t)feedbackBuf[1]<<8) + (uint8_t)feedbackBuf[2];
	y = ((uint8_t)feedbackBuf[3]<<8) + (uint8_t)feedbackBuf[4];
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::setTextColor(uint16_t color)
{
	char temp[3];
	temp[0] = SET_TEXTCOLOR;
	temp[1] = color>>8;
	temp[2] = color;
	sendCommand(temp,3);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::setTextSize(uint8_t size) 
{
    char temp[2];
	temp[0] = SET_TEXTSIZE;
	temp[1] = size;
	sendCommand(temp,2);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::setRotation(uint8_t rota) //rota = 0, 1, 2, 3
{
	char temp[2];
	temp[0] = SET_ROTATION;
	temp[1] = rota;
	sendCommand(temp,2);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::reset()
{
	char temp[1];
	temp[0] = RESET;
	sendCommand(temp,1);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::setBacklight(uint8_t bightness) 
{
	char temp[2];
	temp[0] = SET_BACKLIGHT;
	temp[1] = bightness;
	sendCommand(temp,2);
	while(checkFeedback()!=FEEDBACK_OK);
}


void SerialTFT::println()
{
    char temp[1];
	temp[0] = PRINTLN;
	sendCommand(temp,1);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::print(const char str[])
{
	char temp[61];//can not be more than 61bytes a time
	uint8_t i = 0;
	temp[0] = PRINT_CHAR_ARRAY;
	while(str[i] != '\0')
	{
		temp[i+1] = str[i];
		i++;
	}
	sendCommand(temp,i+1);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::print(int8_t c)
{
  	char temp[4];
	temp[0] = PRINT_INT_8;
	temp[1] = SIGNED;
	temp[2] = 0;//format, char have no format
	temp[3] = c;
	sendCommand(temp,4);
	while(checkFeedback()!=FEEDBACK_OK);
}

//base: 
//#define DEC 10
//#define HEX 16
//#define OCT 8
//#define BIN 2
void SerialTFT::print(uint8_t b, uint8_t base)
{
  	char temp[4];
	temp[0] = PRINT_INT_8;
	temp[1] = UNSIGNED;
	temp[2] = base;//
	temp[3] = b;
	sendCommand(temp,4);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::print(int16_t n)
{
  	char temp[5];
	temp[0] = PRINT_INT_16;
	temp[1] = SIGNED;
	temp[2] = 0;//format, char have no format
	temp[3] = n>>8;
	temp[4] = n;
	sendCommand(temp,5);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::print(uint16_t n, uint8_t base)
{
	char temp[5];
	temp[0] = PRINT_INT_16;
	temp[1] = UNSIGNED;
	temp[2] = base;//
	temp[3] = n>>8;
	temp[4] = n;

	sendCommand(temp,5);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::print(int32_t n)
{
  	char temp[7];
	temp[0] = PRINT_INT_32;
	temp[1] = SIGNED;
	temp[2] = 0;//format, char have no format
	temp[3] = n>>24;
	n <<= 8;
	temp[4] = n>>24;
	n <<= 8;
	temp[5] = n>>24;
	n <<= 8;
	temp[6] = n>>24;
	sendCommand(temp,7);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::print(uint32_t n, uint8_t base)
{
  	char temp[7];
	temp[0] = PRINT_INT_32;
	temp[1] = UNSIGNED;
	temp[2] = base;//
	temp[3] = n>>24;
	temp[4] = n>>16;
	temp[5] = n>>8;
	temp[6] = n;
	sendCommand(temp,7);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::println(const char str[])
{
	print(str);
	println();
}
void SerialTFT::println(int8_t c)
{
	print(c);
	println();
}

void SerialTFT::println(uint8_t b, uint8_t base)
{
	print(b, base);
	println(); 
}

void SerialTFT::println(int16_t n)
{
	print(n);
	println();	
}

void SerialTFT::println(uint16_t n, uint8_t base)
{
	print(n,base);
	println();
}
void SerialTFT::println(int32_t n)
{
	print(n);
	println();	

}

void SerialTFT::println(uint32_t n, uint8_t base)
{
	print(n,base);
	println();

}

void SerialTFT::fillScreen(uint16_t color)
{
	char temp[3];
	temp[0] = FILL_SREEN;
	temp[1] = color>>8;
	temp[2] = color;
	sendCommand(temp,3);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawPixel(int16_t x, int16_t y, uint16_t color)
{
	char temp[7];
	temp[0] = DRAW_PIXEL;
	temp[1] = x>>8;
	temp[2] = x;
	temp[3] = y>>8;
	temp[4] = y;
	temp[5] = color>>8;
	temp[6] = color;
	sendCommand(temp,7);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawFastHLine(int16_t x0, int16_t y0, int16_t w, uint16_t color)
{
	char temp[9];
	temp[0] = DRAW_FASTHLINE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = w>>8;
	temp[6] = w;
	temp[7] = color>>8;
	temp[8] = color;
	sendCommand(temp,9);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawFastVLine(int16_t x0, int16_t y0, int16_t h, uint16_t color)
{
	char temp[9];
	temp[0] = DRAW_FASTVLINE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = h>>8;
	temp[6] = h;
	temp[7] = color>>8;
	temp[8] = color;
	sendCommand(temp,9);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
        uint16_t color)
{
	char temp[11];
	temp[0] = DRAW_LINE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = x1>>8;
	temp[6] = x1;
	temp[7] = y1>>8;
	temp[8] = y1;
	temp[9] = color>>8;
	temp[10] = color;
	sendCommand(temp,11);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawRect(int16_t x, int16_t y, int16_t w, int16_t h,
        uint16_t color)
{
	char temp[11];
	temp[0] = DRAW_RECT;
	temp[1] = x>>8;
	temp[2] = x;
	temp[3] = y>>8;
	temp[4] = y;
	temp[5] = w>>8;
	temp[6] = w;
	temp[7] = h>>8;
	temp[8] = h;
	temp[9] = color>>8;
	temp[10] = color;
	sendCommand(temp,11);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::fillRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t color)
{
	char temp[11];
	temp[0] = FILL_RECT;
	temp[1] = x>>8;
	temp[2] = x;
	temp[3] = y>>8;
	temp[4] = y;
	temp[5] = w>>8;
	temp[6] = w;
	temp[7] = h>>8;
	temp[8] = h;
	temp[9] = color>>8;
	temp[10] = color;
	sendCommand(temp,11);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawCircle(int16_t x0, int16_t y0, int16_t r, uint16_t color)
{
	char temp[9];
	temp[0] = DRAW_CIRCLE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = r>>8;
	temp[6] = r;
	temp[7] = color>>8;
	temp[8] = color;
	sendCommand(temp,9);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::fillCircle(int16_t x0, int16_t y0, int16_t r, uint16_t color)
{
	char temp[9];
	temp[0] = FILL_CIRCLE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = r>>8;
	temp[6] = r;
	temp[7] = color>>8;
	temp[8] = color;
	sendCommand(temp,9);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawTriangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
      int16_t x2, int16_t y2, uint16_t color)
{
	char temp[15];
	temp[0] = DRAW_TRIANGLE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = x1>>8;
	temp[6] = x1;
	temp[7] = y1>>8;
	temp[8] = y1;
	temp[9] = x2>>8;
	temp[10] = x2;
	temp[11] = y2>>8;
	temp[12] = y2;
	temp[13] = color>>8;
	temp[14] = color;
	sendCommand(temp,15);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::fillTriangle(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
      int16_t x2, int16_t y2, uint16_t color)
{
	char temp[15];
	temp[0] = FILL_TRIANGLE;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = x1>>8;
	temp[6] = x1;
	temp[7] = y1>>8;
	temp[8] = y1;
	temp[9] = x2>>8;
	temp[10] = x2;
	temp[11] = y2>>8;
	temp[12] = y2;
	temp[13] = color>>8;
	temp[14] = color;
	sendCommand(temp,15);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::drawRoundRect(int16_t x0, int16_t y0, int16_t w, int16_t h,
      int16_t r, uint16_t color)
{
	char temp[13];
	temp[0] = DRAW_ROUNDRECT;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = w>>8;
	temp[6] = w;
	temp[7] = h>>8;
	temp[8] = h;
	temp[9] = r>>8;
	temp[10] = r;
	temp[11] = color>>8;
	temp[12] = color;
	sendCommand(temp,13);
	while(checkFeedback()!=FEEDBACK_OK);
}
void SerialTFT::fillRoundRect(int16_t x0, int16_t y0, int16_t w, int16_t h,
      int16_t r, uint16_t color)
{
	char temp[13];
	temp[0] = FILL_ROUNDRECT;
	temp[1] = x0>>8;
	temp[2] = x0;
	temp[3] = y0>>8;
	temp[4] = y0;
	temp[5] = w>>8;
	temp[6] = w;
	temp[7] = h>>8;
	temp[8] = h;
	temp[9] = r>>8;
	temp[10] = r;
	temp[11] = color>>8;
	temp[12] = color;
	sendCommand(temp,13);
	while(checkFeedback()!=FEEDBACK_OK);
}

void SerialTFT::bmpDraw(char *filename)
{
	char temp[9];//can not be more than 8 byte file name
	uint8_t i = 0;
	temp[0] = DRAW_BMP;
	while(*(filename+i)!='\0')
	{
		temp[i+1] = *(filename+i);
		i++;
	}
	sendCommand(temp,i+1);
	while(checkFeedback()!=FEEDBACK_OK);
}



uint16_t SerialTFT::color565(uint8_t r, uint8_t g, uint8_t b)
{
	return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}
/**************************/
//if someone touch, it will return 1. otherwise return 0;
uint8_t SerialTFT::touch()
{
	if(checkFeedback() == READ_TOUCH)
	{
	    
		touchX = ((uint8_t)feedbackBuf[1]<<8) + (uint8_t)feedbackBuf[2];
		touchY = ((uint8_t)feedbackBuf[3]<<8) + (uint8_t)feedbackBuf[4];
		return 1;
	}
	else return 0;
}

