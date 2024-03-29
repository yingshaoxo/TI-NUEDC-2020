// Arduino Signal Filtering Library
// Copyright 2012-2015 Jeroen Doggen (jeroendoggen@gmail.com)

#ifndef newFilter_h
#define newFilter_h
#include <Arduino.h>
#include <Filter.h>

class newFilter : public Filter
{
  public:
    newFilter();
    void begin();

    long int run(long int data);

  private:
    long int _y[3];
};
#endif
