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

#include <iostream>
#include "pyanatomist.h"
#include <anatomist/processor/Processor.h>
#include <exception>
#include <anatomist/commands/cCreateWindow.h>
#include <anatomist/processor/Processor.h>
#include <anatomist/window/qwindow.h>
#include <anatomist/application/settings.h>
#include <anatomist/control/wControl.h>
#include <anatomist/volume/Volume.h>
#include <anatomist/bucket/Bucket.h>
#include <anatomist/graph/Graph.h>
#include <anatomist/object/objectConverter.h>
#include <anatomist/reference/transfSet.h>
#include <anatomist/surface/texture.h>
#include <anatomist/hierarchy/hierarchy.h>
#include <anatomist/sparsematrix/sparsematrix.h>
#include <aims/sparsematrix/sparseordensematrix.h>
#include <aims/def/path.h>
#include <cartobase/smart/rcptrtrick.h>
#include <qapplication.h>

using namespace anatomist;
using namespace aims;
using namespace carto;
using namespace std;

void unexpectedExceptionHandler()
{
  cerr << "PyAnatomist fatal error" << endl;
}


AnatomistSip::AnatomistSip( const vector<string> & argv )
{
  // cout << "AnatomistSip::AnatomistSip\n";
  set_unexpected( unexpectedExceptionHandler );
  try
    {
      if( !anatomist::theProcessor )
      {
        // cerr << "PyAnatomist: new anatomist::Processor;" << endl;
        new anatomist::Processor;
      }
      if( !theAnatomist )
      {
        // cerr << "PyAnatomist: new anatomist::Anatomist" << endl;

        static int   falseargc = argv.empty() ? 1 : argv.size();
        static char **falseArgv = (char **) malloc( ( falseargc + 1 )
          * sizeof( char * ) );

        if( argv.empty() )
        {
          falseArgv[0] = const_cast<char *>( "anatomist" );
          falseArgv[1] = 0;
        }
        else
        {
          unsigned i, n = argv.size();
          // WARNING: all these duplicated strings will leak.
          for( i=0; i<n; ++i )
            falseArgv[i] = strdup( argv[i].c_str() );
          falseArgv[n] = 0;
        }

        if( !QApplication::instance()
            || !dynamic_cast<QApplication *>( QApplication::instance() ) )
        {
          cerr << "existing QApplication: " << QApplication::instance() << endl;
          if( QApplication::instance() )
            cout << ": "  << typeid( *QApplication::instance() ).name() << endl;
          // cerr << "build a QApplication" << endl;
          // cout << "argc: " << falseargc << endl;
          // needed in WebEngine helps and other extensions in python
          if( !QApplication::instance() )
            QCoreApplication::setAttribute( Qt::AA_ShareOpenGLContexts );
          cout << "create qapp\n";
          new QApplication( falseargc, falseArgv );
          cout << "done\n";
        }
        new anatomist::Anatomist( falseargc, (const char **) falseArgv,
                                  "PyAnatomist GUI" );
        theAnatomist->initialize();
        new QSelectFactory;
      }
    }
  catch( exception &e )
    {
      cerr << "PyAnatomist error: " << e.what() << endl;
    }
  catch( ... )
    {
      cerr << "PyAnatomist unknown error" << endl;
    }
}


void AnatomistSip::quit()
{
  delete theAnatomist;
}


QWidget *AnatomistSip::createWindow( const QString &type, QWidget *parent )
{
  anatomist::CreateWindowCommand *c 
    = new anatomist::CreateWindowCommand( type.toStdString() );

  anatomist::theProcessor->execute( c );
  QWidget	*w = dynamic_cast<QWidget *>( c->createdWindow() );
  if( w && parent )
    w->setParent( parent );

  return w;
}


void AnatomistSip::releaseWindow( AWindow* win )
{
  theAnatomist->releaseWindow( win );
}


void AnatomistSip::releaseObject( AObject* obj )
{
  theAnatomist->releaseObject( obj );
}


QString AnatomistSip::anatomistSharedPath()
{
  return anatomist::Settings::globalPath().c_str();
}


QString AnatomistSip::anatomistHomePath()
{
  return anatomist::Settings::localPath().c_str();
}


ControlWindow* AnatomistSip::getControlWindow()
{
  return theAnatomist->getControlWindow();
}

QWidget* AnatomistSip::getQWidgetAncestor() const
{
  return theAnatomist->getQWidgetAncestor();
}

std::set<anatomist::AWindow*> AnatomistSip::getWindowsInGroup( int group )
{
  return theAnatomist->getWindowsInGroup( group );
}

void AnatomistSip::setObjectName( anatomist::AObject* obj,
                                  const std::string & name )
{
  obj->setName( name );
}

anatomist::Processor* AnatomistSip::theProcessor()
{
  return anatomist::theProcessor;
}

std::set<anatomist::AObject *> AnatomistSip::getObjects () const
{
	return theAnatomist->getObjects();
}

std::set<anatomist::AWindow *> AnatomistSip::getWindows () const
{
	return theAnatomist->getWindows();
}


std::set<anatomist::Referential *> AnatomistSip::getReferentials() const
{
  return theAnatomist->getReferentials();
}


std::set<anatomist::Transformation *> AnatomistSip::getTransformations() const
{
  return ATransformSet::instance()->allTransformations();
}


anatomist::PaletteList & AnatomistSip::palettes()
{
  return theAnatomist->palettes();
}


Point3df AnatomistSip::lastPosition(
  const anatomist::Referential *toref ) const
{
  return theAnatomist->lastPosition( toref );
}


int AnatomistSip::userLevel() const
{
  return theAnatomist->userLevel();
}


void AnatomistSip::setUserLevel( int x )
{
  theAnatomist->setUserLevel( x );
}

GlobalConfiguration* AnatomistSip::config()
{
  return theAnatomist->config();
}

// ------------------------

carto::rc_ptr<Volume_U8>
AObjectConverter::volume_U8( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_U8>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_S16>
AObjectConverter::volume_S16( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_S16>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_U16>
AObjectConverter::volume_U16( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_U16>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_S32>
AObjectConverter::volume_S32( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_S32>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_U32>
AObjectConverter::volume_U32( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_U32>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_FLOAT>
AObjectConverter::volume_FLOAT( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_FLOAT>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_DOUBLE>
AObjectConverter::volume_DOUBLE( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_DOUBLE>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_RGB>
AObjectConverter::volume_RGB( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_RGB>::ana2aims( obj, options );
}


carto::rc_ptr<Volume_RGBA>
AObjectConverter::volume_RGBA( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<Volume_RGBA>::ana2aims( obj, options );
}


carto::rc_ptr<AimsTimeSurface<2,Void> >
AObjectConverter::aimsSurface2( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<AimsTimeSurface<2,Void> >::ana2aims( obj, options );
}


carto::rc_ptr<AimsTimeSurface<3,Void> >
AObjectConverter::aimsSurface3( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<AimsTimeSurface<3,Void> >::ana2aims( obj, options );
}


carto::rc_ptr<AimsTimeSurface<4,Void> >
AObjectConverter::aimsSurface4( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<AimsTimeSurface<4,Void> >::ana2aims( obj, options );
}


carto::rc_ptr<BucketMap<Void> >
AObjectConverter::aimsBucketMap_VOID( anatomist::AObject* obj, Object options )
{
  return ObjectConverter<BucketMap<Void> >::ana2aims( obj, options );
}


carto::rc_ptr<TimeTexture<float> >
AObjectConverter::aimsTexture_FLOAT( anatomist::AObject * obj, Object options )
{
  return ObjectConverter<TimeTexture<float> >::ana2aims( obj, options );
}


carto::rc_ptr<TimeTexture<short> >
AObjectConverter::aimsTexture_S16( anatomist::AObject * obj, Object options )
{
  return ObjectConverter<TimeTexture<short> >::ana2aims( obj, options );
}


rc_ptr<TimeTexture<int> >
AObjectConverter::aimsTexture_S32( anatomist::AObject * obj, Object options )
{
  return ObjectConverter<TimeTexture<int> >::ana2aims( obj, options );
}


rc_ptr<TimeTexture<unsigned> >
AObjectConverter::aimsTexture_U32( anatomist::AObject * obj, Object options )
{
  return ObjectConverter<TimeTexture<unsigned> >::ana2aims( obj, options );
}


/*
TimeTexture<Point2d> *
AObjectConverter::aimsTexture_POINT2D( anatomist::AObject * obj )
{
  return ObjectConverter<TimeTexture<Point2d> >::ana2aims( obj );
}
*/


carto::rc_ptr<TimeTexture<Point2df> >
AObjectConverter::aimsTexture_POINT2DF( anatomist::AObject * obj,
                                        Object options )
{
  return ObjectConverter<TimeTexture<Point2df> >::ana2aims( obj, options );
}


carto::rc_ptr<Graph> AObjectConverter::aimsGraph( anatomist::AObject * obj,
    Object options )
{
  return ObjectConverter<Graph>::ana2aims( obj, options );
}


carto::rc_ptr<Tree> AObjectConverter::aimsTree( anatomist::AObject * obj,
    Object options )
{
  return ObjectConverter<Tree>::ana2aims( obj, options );
}


rc_ptr<SparseOrDenseMatrix>
AObjectConverter::aimsSparseOrDenseMatrix( AObject* obj, Object options )
{
  return ObjectConverter<SparseOrDenseMatrix>::ana2aims( obj, options );
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_U8> aims )
{
  AObject       *ao = new AVolume<uint8_t>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_U8" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_S16> aims )
{
  AObject       *ao = new AVolume<int16_t>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_S16" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_U16> aims )
{
  AObject       *ao = new AVolume<uint16_t>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_U16" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_S32> aims )
{
  AObject       *ao = new AVolume<int32_t>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_S32" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_U32> aims )
{
  AObject       *ao = new AVolume<uint32_t>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_U32" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_FLOAT> aims )
{
  AObject       *ao = new AVolume<float>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_FLOAT" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_DOUBLE> aims )
{
  AObject       *ao = new AVolume<double>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_DOUBLE" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_RGB> aims )
{
  AObject       *ao = new AVolume<AimsRGB>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_RGB" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Volume_RGBA> aims )
{
  AObject       *ao = new AVolume<AimsRGBA>( aims );
  ao->setName( theAnatomist->makeObjectName( "Volume_RGBA" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  ao->adjustPalette();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<AimsSurfaceTriangle> aims )
{
  ASurface<3>	*ao = new ASurface<3>;
  ao->setSurface( aims );
  ao->setHeaderOptions();
  ao->setName( theAnatomist->makeObjectName( "Mesh" ) );
  theAnatomist->registerObject( ao );
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<AimsTimeSurface<2, Void> > aims )
{
  ASurface<2>	*ao = new ASurface<2>;
  ao->setSurface( aims );
  ao->setHeaderOptions();
  ao->setName( theAnatomist->makeObjectName( "Segments" ) );
  theAnatomist->registerObject( ao );
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<AimsTimeSurface<4, Void> > aims )
{
  ASurface<4>	*ao = new ASurface<4>;
  ao->setSurface( aims );
  ao->setHeaderOptions();
  ao->setName( theAnatomist->makeObjectName( "Mesh4" ) );
  theAnatomist->registerObject( ao );
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<BucketMap<Void> > aims )
{
  Bucket *bck = new Bucket;
  bck->setBucket( aims );
  bck->setHeaderOptions();
  AObject	*ao = bck;
  ao->setName( theAnatomist->makeObjectName( "Bucket" ) );
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Graph> aims )
{
  AGraph	*ao = new AGraph( aims, "" );
  ao->setName( theAnatomist->makeObjectName( "Graph" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<TimeTexture<float> > aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture1d" ) );
  ao->setTexture( aims );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<TimeTexture<short> > aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture_S16" ) );
  ao->setTexture( aims );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<TimeTexture<int> > aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture_S32" ) );
  ao->setTexture( aims );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<TimeTexture<unsigned> > aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture_U32" ) );
  ao->setTexture( aims );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


/*
AObject* AObjectConverter::anatomist( TimeTexture<Point2d> *aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture_POINT2D" ) );
  ao->setTexture( rc_ptr<TimeTexture<Point2d> >( aims ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}
*/


AObject* AObjectConverter::anatomist( rc_ptr<TimeTexture<Point2df> > aims )
{
  ATexture        *ao = new ATexture;
  ao->setName( theAnatomist->makeObjectName( "Texture2d" ) );
  ao->setTexture( aims );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  ao->SetExtrema();
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<Tree> aims )
{
  anatomist::Hierarchy        *ao = new anatomist::Hierarchy( aims );
  ao->setName( theAnatomist->makeObjectName( "Nomenclature" ) );
  ao->setHeaderOptions();
  theAnatomist->registerObject( ao );
  return ao;
}


AObject* AObjectConverter::anatomist( rc_ptr<SparseOrDenseMatrix> aims )
{
  ASparseMatrix *ao = new ASparseMatrix;
  ao->setMatrix( aims );
  ao->setHeaderOptions();
  ao->setName( theAnatomist->makeObjectName( "SparseOrDenseMatrix" ) );
  theAnatomist->registerObject( ao );
  return ao;
}


