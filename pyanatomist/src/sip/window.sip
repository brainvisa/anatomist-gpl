%ModuleHeaderCode
#include <anatomist/window/colorstyle.h>
%End

namespace anatomist
{

  void setQtColorStyle( QWidget* );

  class AWindow : carto::SharedObject, anatomist::Observer /Abstract/
  {
%TypeHeaderCode
#include <anatomist/window/Window.h>
%End

%TypeCode
#include <pyanatomist/sipconverthelpers.h>
%End

%ConvertToTypeCode
  return anatomist::sipConvertToTypeCodeFromInternalRep( sipPy,
    sipType_anatomist_AWindow, sipTransferObj, sipIsErr, sipCppPtr );
%End

  public:
    enum Type { CTRL_WINDOW = 100, WINDOW_2D = 101, WINDOW_3D = 102 };
    enum SubType { AXIAL_WINDOW = 200,
        SAGITTAL_WINDOW = 201,
        CORONAL_WINDOW = 202,
        OBLIQUE_WINDOW = 203,
        OTHER = 299
    };

    virtual ~AWindow();
    virtual std::string Title() const;

    virtual Type type() const = 0;
    virtual SubType subtype() const;
    virtual void registerObject( anatomist::AObject *, bool = false,
      int=-1 );
    virtual void unregisterObject( anatomist::AObject * );
    virtual void Refresh();
    int Group() const;
    bool hasObject(anatomist::AObject *) const;
    float getTime() const;
    virtual void setTime( float time );
    virtual Point3df getPosition() const;
    virtual void setPosition( const Point3df &position,
      const anatomist::Referential *refdep );
    void setHasCursor(int);
    virtual bool toolBarsVisible() const;
    virtual void showToolBars(int = 2 );
    void setFullScreen(int);
    set_AObjectPtr Objects() const;
    virtual anatomist::AObject *objectAt( const vector_FLOAT & pos );
    bool isTemporary( anatomist::AObject* o ) const;
    anatomist::Referential *getReferential() const;
    virtual void setReferential( anatomist::Referential *ref );
    virtual void show();
    virtual void hide();
    virtual const std::string & baseTitle() const;

    static anatomist::AWindow* fromObject( carto::GenericObject );
%MethodCode
  try
  {
    sipRes = a0->value<anatomist::AWindow *>();
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End

    Point3df* positionFromCursor (int x, int y ) /Factory/;
%MethodCode
    sipRes = new Point3df;
    if( !sipCpp->positionFromCursor( a0, a1, *sipRes ) )
    {
      delete sipRes;
      sipRes = 0;
    }
%End

  protected:
    AWindow();

  private:
    AWindow( const anatomist::AWindow & );

    virtual void displayClickPoint() const = 0;
  };

/*
  class QAWindowDrag : QStoredDrag
  {
%TypeHeaderCode
#include <anatomist/control/windowdrag.h>
%End

  public:
    QAWindowDrag( const set_AWindowPtr &, QWidget * dragSource = 0,
		  const char * name = 0 );
    virtual ~QAWindowDrag();

    static bool canDecode( const QMimeSource * e );
    static bool decode( const QMimeSource * e, set_AWindowPtr & o );
  };
*/


class View
{
%TypeHeaderCode
#include <anatomist/controler/view.h>
#include <anatomist/window/glwidget.h>
%End

%ConvertToSubClassCode
  if( dynamic_cast<anatomist::GLWidgetManager *>( sipCpp ) )
  {
    if( dynamic_cast<QAGLWidget *>( sipCpp ) )
    {
      *sipCppRet = dynamic_cast<QAGLWidget *>( sipCpp );
      sipType = sipType_QAGLWidget;
    }
    else
    {
      *sipCppRet = static_cast<anatomist::GLWidgetManager *>( sipCpp );
      sipType = sipType_anatomist_GLWidgetManager;
    }
  }
  else
    sipType = NULL;
%End

  public:
  View( anatomist::AWindow * );
  virtual ~View();
  anatomist::GLWidgetManager* glWidget();
%MethodCode
    sipRes = dynamic_cast<anatomist::GLWidgetManager *>( sipCpp );
%End

  ControlSwitch * controlSwitch();
  virtual std::string name() const =0;
  anatomist::AWindow * aWindow();
  // const anatomist::AWindow * aWindow() const;
};
};


class QAWindow : QMainWindow, anatomist::AWindow
{
%TypeHeaderCode
#include <qmainwindow.h>
#include <anatomist/window/Window.h>
#include <anatomist/window/qwindow.h>
#include <stdio.h>
%End

public:
  QAWindow( QWidget * /TransferThis/ = 0, const char *=0,
    carto::Object =carto::none(), Qt::WindowFlags=Qt::Window );
  virtual ~QAWindow();
  virtual void refreshNow();
  virtual bool close();
  static QAWindow* fromObject( carto::GenericObject );
%MethodCode
  try
  {
    anatomist::AWindow *aw = a0->value<anatomist::AWindow *>();
    sipRes = dynamic_cast<QAWindow *>(aw);
  }
  catch( std::exception & e )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_RuntimeError, e.what() );
    sipRes = 0;
  }
%End

public slots:
  void triggeredRefresh();

protected:
  virtual void dragEnterEvent( QDragEnterEvent* );
  virtual void dropEvent( QDropEvent* );
};


class AWindow3D : ControlledWindow, anatomist::Observable
{
%TypeHeaderCode
#include <anatomist/window3D/window3D.h>
%End
public:
  enum ViewType { Oblique, Axial, Sagittal, Coronal, ThreeD };
  enum ClipMode
  {
    NoClip,
    Single,
    Double
  };

  virtual ~AWindow3D();
  
  void focusView();
  void refreshTemp();
  void refreshTempNow();
  void refreshLightView();
  void refreshLightViewNow();
  void muteAxial();
  void muteCoronal();
  void muteSagittal();
  void muteOblique();
  void mute3D();
  virtual void Refresh();
  virtual void refreshNow();
  virtual anatomist::AObject* objectAtCursorPosition( int x, int y );

/*  virtual std::list<anatomist::AObject*> *objectsAtCursorPosition( int x,
      int y, int tolerenceRadius );
      */

  virtual int polygonAtCursorPosition( int x, int y,
                                       const anatomist::AObject* obj );
  ViewType viewType() const;
  bool isViewOblique() const;
  const aims::Quaternion & sliceQuaternion() const;
  QSlider * getSliceSlider() const;
  ClipMode clipMode() const;
  void setClipMode( ClipMode m );
  float clipDistance() const;
  void setClipDistance( float d );
  bool transparentZEnabled() const;
  void enableTransparentZ( bool );
  bool cullingEnabled() const;
  void setCulling( bool );
  bool flatShading() const;
  void setFlatShading( bool );
  bool smoothing() const;
  void setSmoothing( bool );
  void setFog( bool );
  bool fog() const;
  void resizeView( int w, int h );
  QImage snapshotImage( int width=0, int height=0, int bufmode=0 );
  virtual rc_ptr_ViewState viewState();

signals:
  void refreshed();
  void sliderChanged( int dim, int slice );
  void orientationChanged();
};


class FixedPointOfViewWindow : QWidget, anatomist::Observer
{
%TypeHeaderCode
#include <anatomist/window3D/wFixedPointOfView.h>
#include <anatomist/window3D/window3D.h>
%End
public:
  FixedPointOfViewWindow( AWindow3D* win, QWidget* parent = 0,
                          const char* name = 0 );
  virtual ~FixedPointOfViewWindow();

  void straightPOV(int);
  void edgePOV(int);
  void cornerPOV(int);
};

