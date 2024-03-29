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

extern "C"
{
#include <Python.h>
}
#include <pyanatomist/module/pythonlauncher.h>
#include <anatomist/application/settings.h>
#include <aims/def/path.h>
#include <cartobase/stream/fileutil.h>
#include <iostream>

#ifdef __linux__
#ifndef _GNU_SOURCE
#define _GNU_SOURCE 1
#endif
#include <link.h>
#include <dlfcn.h>
#endif

using namespace anatomist;
using namespace aims;
using namespace carto;
using namespace std;

PythonLauncher::PythonLauncher() : QObject()
{
}


PythonLauncher::~PythonLauncher()
{
}


void PythonLauncher::runModules()
{
  cout << "PythonLauncher::runModules()\n";

#ifdef __linux__
  /* avoids missing symbols (why ??) see
     https://stackoverflow.com/questions/29880931/importerror-and-pyexc-systemerror-while-embedding-python-script-within-c-for-pam

     without this libpython reload, importing the sip module results in an
     error: undefined symbol: PyExc_SystemError
  */
  void *self = dlopen(0, RTLD_LAZY | RTLD_GLOBAL);
  struct link_map *info;

  if( dlinfo( self, RTLD_DI_LINKMAP, &info ) == 0 )
  {
    struct link_map *next = info->l_next;
    string bname;
    while( next )
    {
      bname = FileUtil::basename( next->l_name );
      if( bname.length() > 9 && bname.substr( 0, 9 ) == "libpython" )
      {
        // force reopening libpython in RT_GLOBAL mode
        dlopen( next->l_name, RTLD_NOW | RTLD_GLOBAL );
      }
      next = next->l_next;
    }
  }
#endif

  static bool modules_initialized = false;

  if( !Py_IsInitialized() )
    Py_Initialize();
//   else
//   {
//     cout << "Python is already running." << endl;
//     cout << "I don't run anatomist python plugins to avoid conflicts"
//          << endl;
// //     modules_initialized = true;
//   }

  if( modules_initialized )
    return;

  char		sep = FileUtil::separator();
  string	shared2 = Settings::globalPath() + sep + "python_plugins";

  modules_initialized = true;

  // cout << "pythonpath 2: " << shared2 << endl;

  PyRun_SimpleString( "import sys" );

  PyRun_SimpleString( (char *) ( string( "sys.path.insert( 1, '" ) + shared2
                                 + "' )" ).c_str() );
  PyRun_SimpleString( "import anatomist.cpp; anatomist.cpp.Anatomist()" );
}


