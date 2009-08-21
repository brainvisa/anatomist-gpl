#ifndef PYANATOMIST_MAPINTQWIDGET_H
#define PYANATOMIST_MAPINTQWIDGET_H

#include <qwidget.h>


inline PyObject* pyanatomistConvertFrom_qpixmap( void * a )
{
  return sipConvertFromInstance( a, sipClass_QPixmap, 0 );
}


inline void* pyanatomistConvertTo_qpixmap( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_QPixmap, 0, 0, 0,
                               &isErr );
}


inline int pyanatomist_qpixmap( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_QPixmap,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

