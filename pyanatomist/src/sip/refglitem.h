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

#ifndef PYANATOMIST_REFGLITEM_H
#define PYANATOMIST_REFGLITEM_H

#include <sip.h>
#ifndef PYAIMSSIP_LIST_RefGLItem_DEFINED
#define PYAIMSSIP_LIST_RefGLItem_DEFINED
#include <list>
typedef std::list<anatomist::RefGLItem> list_RefGLItem;
#endif

inline void* pyanatomistConvertTo_RefGLItem( PyObject* obj )
{
  int sipIsErr = 0;
  void *ptr = sipForceConvertToType( obj, sipType_rc_ptr_GLItem,
    0, 0, 0, &sipIsErr );
  if( sipIsErr )
    return 0;
  return ptr;
}

inline PyObject* pyanatomistConvertFrom_RefGLItem( void* obj )
{
  carto::rc_ptr<anatomist::GLItem>  * robj
      = (carto::rc_ptr<anatomist::GLItem> *) obj;
  PyObject *ptr
      = sipConvertFromType( new carto::rc_ptr<anatomist::GLItem>( *robj ),
                            sipType_rc_ptr_GLItem,
                            Py_None );
  return ptr;
}

inline int pyanatomistObjectRefGLItem_Check( PyObject* o )
{
   return sipCanConvertToType( o, sipType_rc_ptr_GLItem,
                               SIP_NOT_NONE | SIP_NO_CONVERTORS );
}
#endif



