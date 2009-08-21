

#ifndef PYANATOMIST_OBJECTMENU_H
#define PYANATOMIST_OBJECTMENU_H

#include <anatomist/object/Object.h>

inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenu( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_ObjectMenu, 0 );
}


inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenuP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_ObjectMenu, 0 );
}


inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenuR( void * a )
{
  return sipConvertFromInstance( a, sipClass_rc_ptr_ObjectMenu, 0 );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenu( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_ObjectMenu, 0, 0, 0,
                               &isErr );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenuP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_ObjectMenu, 0, 0, 0,
                               &isErr );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenuR( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_rc_ptr_ObjectMenu, 0, 0,
                               0, &isErr );
}


inline int pyanatomistObjectMenu_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_ObjectMenu,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}


inline int pyanatomistObjectMenuP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_ObjectMenu,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}


inline int pyanatomistObjectMenuR_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_rc_ptr_ObjectMenu,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

