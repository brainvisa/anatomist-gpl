
namespace anatomist
{

class Trackball : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/trackball.h>
%End

public:
  Trackball();
  virtual ~Trackball();

  virtual void beginTrackball( int x, int y, int globalX, int globalY );
  virtual void moveTrackball( int x, int y, int globalX, int globalY );
  virtual void endTrackball( int x, int y, int globalX, int globalY );
  void setCenter();
  void showRotationCenter();
  aims::Quaternion rotation( int x, int y );
};


class ContinuousTrackball : QObject, anatomist::Trackball
{
%TypeHeaderCode
#include <anatomist/window3D/trackball.h>
%End

  public:
    ContinuousTrackball();
    virtual ~ContinuousTrackball();

    virtual void beginTrackball( int x, int y, int globalX, int globalY );
    virtual void moveTrackball( int x, int y, int globalX, int globalY );
    virtual void endTrackball( int x, int y, int globalX, int globalY );
    void startOrStop();
    void stop();
};


class TrackOblique : anatomist::Trackball
{
%TypeHeaderCode
#include <anatomist/window3D/trackOblique.h>
%End

public:
  TrackOblique();
  TrackOblique( const anatomist::TrackOblique & a );
  virtual ~TrackOblique();

  virtual std::string name() const;

  virtual void beginTrackball( int x, int y, int globalX, int globalY );
  virtual void moveTrackball( int x, int y, int globalX, int globalY );
  virtual void endTrackball( int x, int y, int globalX, int globalY );
  aims::Quaternion rotation( int x, int y );

  aims::Quaternion	beginQuaternion() const;
};


class TrackObliqueSlice : anatomist::TrackOblique
{
%TypeHeaderCode
#include <anatomist/window3D/trackObliqueSlice.h>
%End

public:
  TrackObliqueSlice();
  TrackObliqueSlice( const anatomist::TrackObliqueSlice & a );
  virtual ~TrackObliqueSlice();

  virtual std::string name() const;

  virtual void beginTrackball( int x, int y, int globalX, int globalY );
  virtual void moveTrackball( int x, int y, int globalX, int globalY );
  virtual void endTrackball( int x, int y, int globalX, int globalY );

};


class TrackCutAction : anatomist::Trackball
{
%TypeHeaderCode
#include <anatomist/window3D/trackcut.h>
%End

public:

  TrackCutAction();
  TrackCutAction( const anatomist::TrackCutAction & a );
  virtual ~TrackCutAction();

  virtual std::string name() const;

  virtual void beginTrackball( int x, int y, int globalX, int globalY );
  virtual void moveTrackball( int x, int y, int globalX, int globalY );
  virtual void endTrackball( int x, int y, int globalX, int globalY );

  void axialSlice();
  void coronalSlice();
  void sagittalSlice();
  void setSlice( const aims::Quaternion & q );

};


class CutSliceAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/trackcut.h>
%End

public:
  CutSliceAction();
  CutSliceAction( const anatomist::CutSliceAction & a );
  virtual ~CutSliceAction();

  virtual std::string name() const;

  virtual void beginTrack( int x, int y, int globalX, int globalY );
  virtual void moveTrack( int x, int y, int globalX, int globalY );
  virtual void endTrack( int, int, int, int );
};


class WindowActions : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    WindowActions();
    virtual ~WindowActions();

    void close();
    void toggleShowTools();
    void toggleFullScreen();
};


class LinkAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    LinkAction();
    virtual ~LinkAction();

    void execLink( int x, int y, int globalX, int globalY );
    void endLink( int x, int y, int globalX, int globalY );
};


class MenuAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    MenuAction();
    virtual ~MenuAction();

    void execMenu( int x, int y, int globalX, int globalY );
};


class SelectAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    SelectAction();
    virtual ~SelectAction();

    void select( int modifier, int x, int y );
    void execSelect( int x, int y, int globalX, int globalY );
    void execSelectAdding( int x, int y, int globalX, int globalY );
    void execSelectToggling( int x, int y, int globalX, int globalY );

    void toggleSelectAll();
    void removeFromWindow();
    void removeFromGroup();
};


class Zoom3DAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    Zoom3DAction();
    virtual ~Zoom3DAction();

    void beginZoom( int x, int y, int globalX, int globalY );
    void moveZoom( int x, int y, int globalX, int globalY );
    void endZoom( int x, int y, int globalX, int globalY );
    void endZoomKey();
    void zoomInOnce();
    void zoomOutOnce();
    void zoomWheel( int, int, int, int, int );
    void zoom( int distance );
};


class PinchZoomAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    PinchZoomAction();
    virtual ~PinchZoomAction();

    void pinchStart( QPinchGesture *gesture );
    void pinchMove( QPinchGesture *gesture );
    void pinchStop( QPinchGesture *gesture );
};


class TouchRotateAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    TouchRotateAction();
    virtual ~TouchRotateAction();

    void touchStart( QTouchEvent *event );
    void touchMove( QTouchEvent *event );
    void touchStop( QTouchEvent *event );
};


class Translate3DAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    Translate3DAction();
    virtual ~Translate3DAction();

    void beginTranslate( int x, int y, int globalX, int globalY );
    void moveTranslate( int x, int y, int globalX, int globalY );
    void endTranslate( int x, int y, int globalX, int globalY );
    void endTranslateKey();
};


class Sync3DAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    Sync3DAction();
    virtual ~Sync3DAction();

    void execSync();
    void execSyncOrientation();
};


class MovieAction : QObject, anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    MovieAction() ;
    virtual ~MovieAction() ;

    void sliceOn() ;
    void timeOn() ;
    void nextMode();
    void increaseSpeed();
    void decreaseSpeed();

    void startOrStop() ;
    bool isRunning() const;
};


class SliceAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    SliceAction();
    virtual ~SliceAction();

    void nextSlice();
    void previousSlice();
    void nextTime();
    void previousTime();
    void toggleLinkedOnSlider();
};


class DragObjectAction : anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    DragObjectAction();
    virtual ~DragObjectAction();

    void dragAll( int x, int y, int globalX, int globalY );
    void dragSelected( int x, int y, int globalX, int globalY );
};


namespace internal
{
class TransformerActionData : QObject
{
%TypeHeaderCode
#include <anatomist/window3D/transformer.h>
%End
    public:
        TransformerActionData();
        virtual ~TransformerActionData();
        virtual aims::Quaternion initialQuaternion() = 0;
        virtual anatomist::View* tadView() = 0;
        bool getCurrentMotion(Motion&);
        void setTransformData(const anatomist::Transformation &, bool absolute=false, bool addToHistory=false);
        void selectTransformations(anatomist::AWindow *);
        anatomist::Transformation* mainTransformation() const;
        void undo();
        void redo();
        bool undoable();
        bool redoable();
        
    public slots:
        virtual void resetTransform();
    
    protected:
        virtual void updateTemporaryObjects(const aims::Quaternion &) = 0;
        virtual void updateGVInfo(const aims::Quaternion &) = 0;
};
}; // namespace internal

class Transformer : anatomist::internal::TransformerActionData, anatomist::Trackball
{
%TypeHeaderCode
#include <anatomist/window3D/transformer.h>
%End

public:
    Transformer();
    virtual ~Transformer();
    void toggleDisplayInfo();
};

class PlanarTransformer : anatomist::Transformer
{
%TypeHeaderCode
#include <anatomist/window3D/transformer.h>
%End

public:
    PlanarTransformer();
    virtual ~PlanarTransformer();
};

class TranslaterAction : anatomist::internal::TransformerActionData, anatomist::Action
{
%TypeHeaderCode
#include <anatomist/window3D/transformer.h>
%End

public:
    TranslaterAction();
    virtual ~TranslaterAction();
};

class ResizerAction : anatomist::TranslaterAction
{
%TypeHeaderCode
#include <anatomist/window3D/transformer.h>
%End

public:
    ResizerAction();
    virtual ~ResizerAction();
};

class Control3D : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    Control3D( int priority = 1, 
      const std::string & name = "Default 3D control" );
    Control3D( const anatomist::Control3D & c );
    virtual ~Control3D();

    virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
    virtual void doAlsoOnSelect( anatomist::ActionPool * actionPool );
    virtual void doAlsoOnDeselect( anatomist::ActionPool * actionPool );
};


class Select3DControl : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

  public:
    Select3DControl( const std::string & name = "Selection 3D" );
    Select3DControl( const anatomist::Select3DControl & c );
    virtual ~Select3DControl();

    virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
    virtual void doAlsoOnSelect( anatomist::ActionPool * actionPool );
    virtual void doAlsoOnDeselect( anatomist::ActionPool * actionPool );
};


class FlightControl : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

public:
  FlightControl();
  FlightControl( const anatomist::FlightControl & c );
  virtual ~FlightControl();

  virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
  virtual void doAlsoOnDeselect( anatomist::ActionPool * actionPool );
};


class ObliqueControl : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

public:
  ObliqueControl( const std::string & name = "ObliqueControl" );
  ObliqueControl( const anatomist::ObliqueControl & c );
  virtual ~ObliqueControl();

  virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
};


class TransformControl : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

public:
  TransformControl();
  TransformControl( const anatomist::TransformControl & c );
  virtual ~TransformControl();

  virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
  virtual void doAlsoOnSelect( anatomist::ActionPool * actionPool );
  virtual void doAlsoOnDeselect( anatomist::ActionPool * actionPool );
};

class CutControl : anatomist::Control
{
%TypeHeaderCode
#include <anatomist/window3D/control3D.h>
%End

public:
  CutControl();
  CutControl( const anatomist::CutControl & c );
  virtual ~CutControl();

  virtual void eventAutoSubscription( anatomist::ActionPool * actionPool );
};

};

