

#ifndef PYANATOMIST_AOBJECT_H
#define PYANATOMIST_AOBJECT_H

#include <anatomist/object/Object.h>

inline PyObject* pyanatomistConvertFrom_anatomist_AObjectP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_AObject, 0 );
}


inline void* pyanatomistConvertTo_anatomist_AObjectP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_AObject, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistAObjectP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_AObject,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

