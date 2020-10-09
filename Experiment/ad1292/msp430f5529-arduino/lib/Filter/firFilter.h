// Arduino Signal Filtering Library
// Copyright 2012-2015 Jeroen Doggen (jeroendoggen@gmail.com)

#ifndef firFilter_h
#define firFilter_h
#include <Arduino.h>
#include <Filter.h>

class firFilter : public Filter
{
  public:
    firFilter();
    void begin();
    
    long int run(long int data);
    void printSamples();
  private:
    long int _x[3];
};
#endif
