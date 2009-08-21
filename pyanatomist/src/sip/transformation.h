#ifndef PYANATOMIST_TRANSFORMATION_H
#define PYANATOMIST_TRANSFORMATION_H

#include <anatomist/reference/Transformation.h>

inline PyObject* pyanatomistConvertFrom_anatomist_TransformationP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_Transformation, 0 );
}


inline void* pyanatomistConvertTo_anatomist_TransformationP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_Transformation, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistTransformationP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_Transformation,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

