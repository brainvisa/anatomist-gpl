

/* This software and supporting documentation are distributed by
 *     Institut Federatif de Recherche 49
 *     CEA/NeuroSpin, Batiment 145,
 *     91191 Gif-sur-Yvette cedex
 *     France
 *
 * This software is governed by the CeCILL license version 2 under
 * French law and abiding by the rules of distribution of free software.
 * You can  use, modify and/or redistribute the software under the
 * terms of the CeCILL license version 2 as circulated by CEA, CNRS
 * and INRIA at the following URL "http://www.cecill.info".
 *
 * As a counterpart to the access to the source code and  rights to copy,
 * modify and redistribute granted by the license, users are provided only
 * with a limited warranty  and the software's author,  the holder of the
 * economic rights,  and the successive licensors  have only  limited
 * liability.
 *
 * In this respect, the user's attention is drawn to the risks associated
 * with loading,  using,  modifying and/or developing or reproducing the
 * software by the user in light of its specific status of free software,
 * that may mean  that it is complicated to manipulate,  and  that  also
 * therefore means  that it is reserved for developers  and  experienced
 * professionals having in-depth computer knowledge. Users are therefore
 * encouraged to load and test the software's suitability as regards their
 * requirements in conditions enabling the security of their systems and/or
 * data to be ensured and,  more generally, to use and operate it in the
 * same conditions as regards security.
 *
 * The fact that you are presently reading this means that you have had
 * knowledge of the CeCILL license version 2 and that you accept its terms.
 */
#ifndef PYANATOMIST_OBJECTMENU_H
#define PYANATOMIST_OBJECTMENU_H

#include <anatomist/object/Object.h>

inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenu( void * a )
{
  return sipConvertFromType( a, sipType_anatomist_ObjectMenu, 0 );
}


inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenuP( void * a )
{
  return sipConvertFromType( a, sipType_anatomist_ObjectMenu, 0 );
}


inline PyObject* pyanatomistConvertFrom_anatomist_ObjectMenuR( void * a )
{
  return sipConvertFromType( a, sipType_rc_ptr_ObjectMenu, 0 );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenu( PyObject * o )
{
  int isErr = 0;
  return sipConvertToType( o, sipType_anatomist_ObjectMenu, 0, 0, 0,
                           &isErr );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenuP( PyObject * o )
{
  int isErr = 0;
  return sipConvertToType( o, sipType_anatomist_ObjectMenu, 0, 0, 0,
                           &isErr );
}


inline void* pyanatomistConvertTo_anatomist_ObjectMenuR( PyObject * o )
{
  int isErr = 0;
  return sipConvertToType( o, sipType_rc_ptr_ObjectMenu, 0, 0,
                           0, &isErr );
}


inline int pyanatomistObjectMenu_Check( PyObject* o )
{
  return sipCanConvertToType( o, sipType_anatomist_ObjectMenu,
                              SIP_NOT_NONE | SIP_NO_CONVERTORS );
}


inline int pyanatomistObjectMenuP_Check( PyObject* o )
{
  return sipCanConvertToType( o, sipType_anatomist_ObjectMenu,
                              SIP_NOT_NONE | SIP_NO_CONVERTORS );
}


inline int pyanatomistObjectMenuR_Check( PyObject* o )
{
  return sipCanConvertToType( o, sipType_rc_ptr_ObjectMenu,
                              SIP_NOT_NONE | SIP_NO_CONVERTORS );
}

#endif

