
#ifndef PYANATOMIST_AWINDOW_H
#define PYANATOMIST_AWINDOW_H

#include <anatomist/window/Window.h>

inline PyObject* pyanatomistConvertFrom_anatomist_AWindowP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_AWindow, 0 );
}


inline void* pyanatomistConvertTo_anatomist_AWindowP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_AWindow, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistAWindowP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_AWindow,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

