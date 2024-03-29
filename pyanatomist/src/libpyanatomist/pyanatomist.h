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

#ifndef PYANATOMIST_PYANATOMIST_H
#define PYANATOMIST_PYANATOMIST_H

#include <anatomist/selection/qSelectFactory.h>
#include <anatomist/application/Anatomist.h>
#include <anatomist/surface/surface.h>
#include <aims/plugin/aimsguiplugin.h>
#include <aims/bucket/bucket.h>
#include <aims/mesh/texture.h>
#include <pyaims/data/data.h>
#include <aims/vector/vector.h>
#include <qwidget.h>

class ControlWindow;

namespace aims
{
  class SparseOrDenseMatrix;
}

namespace anatomist
{
  class Processor;
  class AWindow;
}

/** I had to rename this class from Anatomist to AnatimistSip 
    because SIP generated two files only differing by the case (one 
    for the namespace anatomist, and one for this class Anatomist), and 
    some systems (Mac, Windows) don't support case-sensitive filesystems.
*/
class AnatomistSip
{
public:

  AnatomistSip( const std::vector<std::string> & argv
                = std::vector<std::string>() );

  QWidget *createWindow( const QString &, QWidget * );
  void releaseWindow( anatomist::AWindow* );
  void releaseObject( anatomist::AObject* );
  QString anatomistSharedPath();
  QString anatomistHomePath();
  ControlWindow *getControlWindow();
  QWidget* getQWidgetAncestor() const;
  std::set<anatomist::AWindow*> getWindowsInGroup( int );
  void setObjectName( anatomist::AObject* obj, const std::string & name );
  anatomist::Processor *theProcessor();
  std::set<anatomist::AObject *> getObjects() const;
  std::set<anatomist::AWindow *> getWindows () const;
  std::set<anatomist::Referential*> getReferentials() const;
  std::set<anatomist::Transformation *> getTransformations() const;
  anatomist::PaletteList & palettes();
  Point3df lastPosition( const anatomist::Referential *toref=0 ) const;
  int userLevel() const;
  void setUserLevel( int );
  anatomist::GlobalConfiguration* config();
  void quit();
  bool exitOnQuit() const;
  void setExitOnQuit( bool x );
};


class AObjectConverter
{
public:
  static carto::rc_ptr<Volume_U8> volume_U8( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_S16> volume_S16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_U16> volume_U16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_S32> volume_S32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_U32> volume_U32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_FLOAT> volume_FLOAT( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_DOUBLE> volume_DOUBLE( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_RGB> volume_RGB( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<Volume_RGBA> volume_RGBA( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static carto::rc_ptr<AimsSurfaceTriangle>
      aimsSurface3( anatomist::AObject*,
                    carto::Object options = carto::Object() );
  static carto::rc_ptr<AimsTimeSurface<2,Void> >
      aimsSurface2( anatomist::AObject*,
                    carto::Object options = carto::Object() );
  static carto::rc_ptr<AimsTimeSurface<4,Void> >
      aimsSurface4( anatomist::AObject*,
                    carto::Object options = carto::Object() );
  static carto::rc_ptr<aims::BucketMap<Void> >
      aimsBucketMap_VOID( anatomist::AObject* obj,
                          carto::Object options = carto::Object() );
  static carto::rc_ptr<TimeTexture<float> >
      aimsTexture_FLOAT( anatomist::AObject* obj,
                         carto::Object options = carto::Object() );
  static carto::rc_ptr<TimeTexture<short> >
      aimsTexture_S16( anatomist::AObject* obj,
                       carto::Object options = carto::Object() );
  static carto::rc_ptr<TimeTexture<int> >
      aimsTexture_S32( anatomist::AObject* obj,
                       carto::Object options = carto::Object() );
  static carto::rc_ptr<TimeTexture<unsigned> >
      aimsTexture_U32( anatomist::AObject* obj,
                       carto::Object options = carto::Object() );
  // static TimeTexture<Point2d>* aimsTexture_POINT2D( anatomist::AObject* obj );
  static carto::rc_ptr<TimeTexture<Point2df> >
      aimsTexture_POINT2DF( anatomist::AObject* obj,
                            carto::Object options = carto::Object() );
  static carto::rc_ptr<Graph>
      aimsGraph( anatomist::AObject* obj,
                 carto::Object options = carto::Object() );
  static carto::rc_ptr<Tree>
      aimsTree( anatomist::AObject* obj,
                carto::Object options = carto::Object() );
  static carto::rc_ptr<aims::SparseOrDenseMatrix>
      aimsSparseOrDenseMatrix( anatomist::AObject* obj,
                carto::Object options = carto::Object() );

  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_U8> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_S16> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_U16> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_S32> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_U32> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_FLOAT> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_DOUBLE> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_RGB> );
  static anatomist::AObject* anatomist( carto::rc_ptr<Volume_RGBA> );
  static anatomist::AObject* anatomist( carto::rc_ptr<AimsSurfaceTriangle> );
  static anatomist::AObject* anatomist( carto::rc_ptr<AimsTimeSurface<2,Void> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<AimsTimeSurface<4,Void> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<aims::BucketMap<Void> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<Graph> );
  static anatomist::AObject* anatomist( carto::rc_ptr<TimeTexture<float> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<TimeTexture<short> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<TimeTexture<int> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<TimeTexture<unsigned> > );
  // static anatomist::AObject* anatomist( TimeTexture<Point2d> * );
  static anatomist::AObject* anatomist( carto::rc_ptr<TimeTexture<Point2df> > );
  static anatomist::AObject* anatomist( carto::rc_ptr<Tree> );
  static anatomist::AObject* anatomist( carto::rc_ptr<aims::SparseOrDenseMatrix> );
};

#endif

