
%Include controlwindow.sip
%Include glComponent.sip
%Include referential.sip
%Include palette.sip
%Include map_STRING_rc_ptr_ObjectMenu.sip
%Include object.sip
%Include slice.sip
%Include objectmenu.sip
%Include mobject.sip
%Include window.sip
%Include controlledWindow.sip
%Include asurface_3.sip
%Include asurface_2.sip
%Include objectlist.sip
%Include graph.sip
%Include map_S32_QPixmap.sip
%Include qobjecttree.sip
%Include unserializer.sip
%Include rcptr_Unserializer.sip
%Include rcptr_ObjectMenu.sip
%Include command.sip
%Include event.sip
%Include rcptr_EventHandler.sip
%Include module.sip
%Include control_VOID.sip
%Include set_AObjectPtr.sip
%Include set_AWindowPtr.sip
%Include set_ReferentialPtr.sip
%Include set_TransformationPtr.sip
%Include vector_AObjectPtr.sip
//%Include map_U32_set_AObjectPtr.sip
//%Include map_U32_set_AWindowPtr.sip
%Include selector.sip
%Include observer.sip
%Include fusion.sip
%Include material.sip
%Include primitive.sip
%Include rcptr_GLItem.sip
%Include list_RefGLItem.sip
%Include list_TransformationPtr.sip
%Include list_AObjectPtr.sip
//%Include list_QString.sip
%Include geometry.sip
%Include viewstate.sip
%Include rcptr_AObject.sip
%Include rcptr_AWindow.sip
%Include sharedptr_AObject.sip
%Include sharedptr_AWindow.sip
%Include control3d.sip
%Include rcptr_APalette.sip
%Include list_rc_ptr_APalette.sip
%Include objectparamselect.sip
%Include objectreader.sip
%Include globalconfig.sip
%Include awindowfactory.sip
%Include objectdrag.sip
%Include transformedobject.sip
%Include textobject.sip
%Include colordialog.sip
%Include choosereferential.sip
%Include texture.sip
%Include qapalettewin.sip
%Include gradwidget.sip
%Include mobjectio.sip

%Include volumeview_U8.sip
%Include volumeview_S16.sip
%Include volumeview_U16.sip
%Include volumeview_S32.sip
%Include volumeview_U32.sip
%Include volumeview_FLOAT.sip
%Include volumeview_DOUBLE.sip
%Include volumeview_RGB.sip
%Include volumeview_RGBA.sip


class AnatomistSip
{
%TypeHeaderCode
#include <pyanatomist/pyanatomist.h>
#include <pyanatomist/setaobject.h>
#include <pyanatomist/setawindow.h>
#include <cartobase/config/verbose.h>
%End

public:

  AnatomistSip( const vector_STRING & = vector_STRING() );
  QWidget *createWindow( const QString &, QWidget * = 0 ) /Factory/;
  void releaseWindow( anatomist::AWindow * );
  void takeWindowRef( anatomist::AWindow * );
%MethodCode
  theAnatomist->takeWindowRef( a0 );
%End
  void releaseObject( anatomist::AObject * );
  void takeObjectRef( anatomist::AObject * );
%MethodCode
  theAnatomist->takeObjectRef( a0 );
%End
  QString anatomistSharedPath();
  QString anatomistHomePath();
  ControlWindow *getControlWindow();
  QWidget* getQWidgetAncestor() const;
  set_AWindowPtr getWindowsInGroup( int = 0 );
  void setObjectName( anatomist::AObject*, const std::string & );
  anatomist::Processor *theProcessor();
  set_AObjectPtr getObjects () const;
  set_AWindowPtr getWindows () const;
  set_ReferentialPtr getReferentials() const;
  set_TransformationPtr getTransformations() const;
  anatomist::PaletteList & palettes();
  Point3df lastPosition( const anatomist::Referential *toref=0 ) const;
  int userLevel() const;
  void setUserLevel( int );
  anatomist::GlobalConfiguration* config();
  void quit();

  void registerObject( anatomist::AObject *, bool = true );
%MethodCode
  theAnatomist->registerObject( a0, a1 );
%End
  void unregisterObject( anatomist::AObject * );
%MethodCode
  theAnatomist->unregisterObject( a0 );
%End
  void registerWindow( anatomist::AWindow * );
%MethodCode
  theAnatomist->registerWindow( a0 );
%End
  void unregisterWindow( anatomist::AWindow * );
%MethodCode
  theAnatomist->unregisterWindow( a0 );
%End
  anatomist::Referential *centralReferential() const;
%MethodCode
  sipRes = theAnatomist->centralReferential();
%End
  int verbose();
%MethodCode
    sipRes = carto::verbose;
%End
  void mapObject( anatomist::AObject * obj );
%MethodCode
  theAnatomist->mapObject( a0 );
%End
  void unmapObject( anatomist::AObject * obj );
%MethodCode
  theAnatomist->unmapObject( a0 );
%End

  anatomist::Transformation*
    getTransformation( const anatomist::Referential*,
                       const anatomist::Referential* );
%MethodCode
  sipRes = theAnatomist->getTransformation( a0, a1 );
%End

  std::string objectsFileFilter() const;
%MethodCode
  sipRes = new std::string( theAnatomist->objectsFileFilter() );
%End

  void addObjectsFileFilter( const std::string & filter );
%MethodCode
  theAnatomist->addObjectsFileFilter( *a0 );
%End

  void updateFileDialogObjectsFilter();
%MethodCode
  theAnatomist->updateFileDialogObjectsFilter();
%End

  static std::string version();
%MethodCode
  sipRes = new std::string( anatomist::Anatomist::versionString() );
%End
};


class AObjectConverter
{
%TypeHeaderCode
#include <pyanatomist/pyanatomist.h>
%End

public:
  static rc_ptr_AimsData_U8 aimsData_U8( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_S16 aimsData_S16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_U16 aimsData_U16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_S32 aimsData_S32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_U32 aimsData_U32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_FLOAT aimsData_FLOAT( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_DOUBLE aimsData_DOUBLE( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_RGB aimsData_RGB( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsData_RGBA aimsData_RGBA( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_U8 volume_U8( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_S16 volume_S16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_U16 volume_U16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_S32 volume_S32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_FLOAT volume_FLOAT( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_DOUBLE volume_DOUBLE( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_RGB volume_RGB( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Volume_RGBA volume_RGBA( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsTimeSurface_2_VOID aimsSurface2( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsTimeSurface_3_VOID aimsSurface3( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_AimsTimeSurface_4_VOID aimsSurface4( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_BucketMap_VOID aimsBucketMap_VOID( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_TimeTexture_FLOAT aimsTexture_FLOAT( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_TimeTexture_S16 aimsTexture_S16( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_TimeTexture_S32 aimsTexture_S32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_TimeTexture_U32 aimsTexture_U32( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_TimeTexture_POINT2DF aimsTexture_POINT2DF( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Graph aimsGraph( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_Tree aimsTree( anatomist::AObject*,
      carto::Object options = carto::Object() );
  static rc_ptr_SparseOrDenseMatrix aimsSparseOrDenseMatrix( 
      anatomist::AObject*,
      carto::Object options = carto::Object() );

  static anatomist::AObject* anatomist( rc_ptr_Volume_U8 );
  static anatomist::AObject* anatomist( rc_ptr_Volume_S16 );
  static anatomist::AObject* anatomist( rc_ptr_Volume_U16 );
  static anatomist::AObject* anatomist( rc_ptr_Volume_S32 );
  static anatomist::AObject* anatomist( rc_ptr_Volume_U32 );
  static anatomist::AObject* anatomist( rc_ptr_Volume_FLOAT );
  static anatomist::AObject* anatomist( rc_ptr_Volume_DOUBLE );
  static anatomist::AObject* anatomist( rc_ptr_Volume_RGB );
  static anatomist::AObject* anatomist( rc_ptr_Volume_RGBA );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_U8 );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_S16 );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_U16 );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_S32 );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_U32 );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_FLOAT );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_DOUBLE );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_RGB );
  static anatomist::AObject* anatomist( rc_ptr_AimsData_RGBA );
  static anatomist::AObject* anatomist( rc_ptr_AimsTimeSurface_2_VOID );
  static anatomist::AObject* anatomist( rc_ptr_AimsTimeSurface_3_VOID );
  static anatomist::AObject* anatomist( rc_ptr_AimsTimeSurface_4_VOID );
  static anatomist::AObject* anatomist( rc_ptr_BucketMap_VOID );
  static anatomist::AObject* anatomist( rc_ptr_Graph );
  static anatomist::AObject* anatomist( rc_ptr_TimeTexture_FLOAT );
  static anatomist::AObject* anatomist( rc_ptr_TimeTexture_S16 );
  static anatomist::AObject* anatomist( rc_ptr_TimeTexture_S32 );
  static anatomist::AObject* anatomist( rc_ptr_TimeTexture_U32 );
  static anatomist::AObject* anatomist( rc_ptr_TimeTexture_POINT2DF );
  static anatomist::AObject* anatomist( rc_ptr_Tree );
  static anatomist::AObject* anatomist( rc_ptr_SparseOrDenseMatrix );
};

