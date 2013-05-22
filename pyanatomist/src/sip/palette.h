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
#ifndef PYANATOMIST_PALETTE_H
#define PYANATOMIST_PALETTE_H

#include <anatomist/color/palette.h>
#include <cartobase/smart/rcptr.h>

typedef carto::rc_ptr<anatomist::APalette> rc_ptr_APalette;


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

