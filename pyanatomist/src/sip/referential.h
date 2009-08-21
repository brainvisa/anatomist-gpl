#ifndef PYANATOMIST_REFERENTIAL_H
#define PYANATOMIST_REFERENTIAL_H

#include <anatomist/reference/Referential.h>

inline PyObject* pyanatomistConvertFrom_anatomist_ReferentialP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_Referential, 0 );
}


inline void* pyanatomistConvertTo_anatomist_ReferentialP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_Referential, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistReferentialP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_Referential,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

