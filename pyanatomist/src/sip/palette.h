#ifndef PYANATOMIST_PALETTE_H
#define PYANATOMIST_PALETTE_H

#include <anatomist/color/palette.h>

inline PyObject* pyanatomistConvertFrom_anatomist_APalette( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_APalette, 0 );
}


inline void* pyanatomistConvertTo_anatomist_APalette( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_APalette, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistAPalette_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_APalette,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

// --

inline PyObject* pyanatomistConvertFrom_anatomist_APaletteP( void * a )
{
  return sipConvertFromInstance( a, sipClass_anatomist_APalette, 0 );
}


inline void* pyanatomistConvertTo_anatomist_APaletteP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_anatomist_APalette, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistAPaletteP_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_anatomist_APalette,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

// --

inline PyObject* pyanatomistConvertFrom_anatomist_APaletteR( void * a )
{
  return sipConvertFromInstance( a, sipClass_rc_ptr_APalette, 0 );
}


inline void* pyanatomistConvertTo_anatomist_APaletteR( PyObject * o )
{
  int isErr = 0;
  return sipConvertToInstance( o, sipClass_rc_ptr_APalette, 0, 0, 0,
                               &isErr );
}


inline int pyanatomistAPaletteR_Check( PyObject* o )
{
  return sipCanConvertToInstance( o, sipClass_rc_ptr_APalette,
                                  SIP_NOT_NONE | SIP_NO_CONVERTORS );
}


#endif

