// Arduino Signal Filtering Library
// Copyright 2012-2015 Jeroen Doggen (jeroendoggen@gmail.com)

#ifndef iirFilter_h
#define iirFilter_h
#include <Arduino.h>
#include <Filter.h>

class iirFilter : public Filter
{
  public:
    iirFilter();
    void begin();

    long int run(long int data);

  private:
    long int _x[3];
    long int _y[3];
};
#endif
