
%#if SIP_VERSION == 0x040403%
%ModuleCode
// work around a bug in SIP 4.4.3
anatomist::Action* 
anatomist::ActionDictionary::ActionCreatorBase::operator () ()
{
  std::cout << "pure virtual method anatomist::ActionDictionary::ActionCreatorBase::operator () called\n";
  return 0;
}

anatomist::Control* 
anatomist::ControlDictionary::ControlCreatorBase::operator () ()
{
  return 0;
}
%End
%#endif%

namespace anatomist
{


class Action
{
%TypeHeaderCode
#include <anatomist/window3D/trackball.h>
#include <anatomist/window3D/control3D.h>
#include <anatomist/window3D/transformer.h>
#include <anatomist/window3D/labeleditaction.h>
%End

%ConvertToSubClassCode
  if( dynamic_cast<anatomist::Trackball *>( sipCpp ) )
  {
    if( dynamic_cast<anatomist::ContinuousTrackball *>( sipCpp ) )
    {
      sipType = sipType_anatomist_ContinuousTrackball;
      *sipCppRet = static_cast<anatomist::ContinuousTrackball *>( sipCpp );
    }
    else if (dynamic_cast<anatomist::Transformer *>(sipCpp))
    {
        if (dynamic_cast<anatomist::PlanarTransformer *>(sipCpp))
        {
            sipType = sipType_anatomist_PlanarTransformer;
            *sipCppRet = static_cast<anatomist::PlanarTransformer *>(sipCpp);
        }
        else
        {
            sipType = sipType_anatomist_Transformer;
            *sipCppRet = static_cast<anatomist::Transformer *>(sipCpp);
        }
    }
    else
      sipType = sipType_anatomist_Trackball;
  }
  else if( dynamic_cast<anatomist::WindowActions *>( sipCpp ) )
    sipType = sipType_anatomist_WindowActions;
  else if( dynamic_cast<anatomist::LinkAction *>( sipCpp ) )
    sipType = sipType_anatomist_LinkAction;
  else if( dynamic_cast<anatomist::MenuAction *>( sipCpp ) )
    sipType = sipType_anatomist_MenuAction;
  else if( dynamic_cast<anatomist::SelectAction *>( sipCpp ) )
    sipType = sipType_anatomist_SelectAction;
  else if( dynamic_cast<anatomist::Zoom3DAction *>( sipCpp ) )
    sipType = sipType_anatomist_Zoom3DAction;
  else if( dynamic_cast<anatomist::Translate3DAction *>( sipCpp ) )
    sipType = sipType_anatomist_Translate3DAction;
  else if( dynamic_cast<anatomist::Sync3DAction *>( sipCpp ) )
    sipType = sipType_anatomist_Sync3DAction;
  else if( dynamic_cast<anatomist::SliceAction *>( sipCpp ) )
    sipType = sipType_anatomist_SliceAction;
  else if( dynamic_cast<anatomist::DragObjectAction *>( sipCpp ) )
    sipType = sipType_anatomist_DragObjectAction;
  else if( dynamic_cast<anatomist::LabelEditAction *>( sipCpp ) )
    sipType = sipType_anatomist_LabelEditAction;
  else if(dynamic_cast<anatomist::TranslaterAction *>(sipCpp))
  {
    if (dynamic_cast<anatomist::ResizerAction *>(sipCpp))
    {
        sipType = sipType_anatomist_ResizerAction;
        *sipCppRet = static_cast<anatomist::ResizerAction *>(sipCpp);
    }
    else
    {
        sipType = sipType_anatomist_TranslaterAction;
        *sipCppRet = static_cast<anatomist::TranslaterAction *>(sipCpp);
    }
  }
  else if( dynamic_cast<anatomist::MovieAction *>( sipCpp ) )
  {
    sipType = sipType_anatomist_MovieAction;
    *sipCppRet = static_cast<anatomist::MovieAction *>( sipCpp );
  }
  else
    sipType = 0;
%End

public:
  Action();
  virtual ~Action();
  virtual std::string name() const = 0;
  virtual bool viewableAction() const;
  virtual bool isSingleton();
  anatomist::View * view();
  virtual QWidget* actionView(QWidget *);
};


class ActionDictionary
{
%TypeHeaderCode
#include <anatomist/controler/actiondictionary.h>
%End

public:
  class ActionCreatorBase
  {
  public:
    virtual ~ActionCreatorBase();
%#if SIP_VERSION == 0x040403%
    virtual anatomist::Action* operator () () /Factory;
%#else%
    virtual anatomist::Action* operator () () =0 /Factory/;
%#endif%

  protected:
    ActionCreatorBase();
  };

  ~ActionDictionary();
  static anatomist::ActionDictionary* instance();

  anatomist::Action* getActionInstance( const std::string & );
  void addAction( const std::string &, 
                  anatomist::ActionDictionary::ActionCreatorBase* /Transfer/ ) 
    /PyName=_addAction/;
  bool removeAction( const std::string & );

private:
  ActionDictionary();
  ActionDictionary( const anatomist::ActionDictionary & );
};


class ActionPool
{
%TypeHeaderCode
#include <anatomist/controler/actionpool.h>
%End

public:
  ~ActionPool();
  anatomist::Action* action( const std::string & );
  set_STRING actionSet() const;

private:
  ActionPool();
};


class Control
{
%TypeHeaderCode
#include <anatomist/controler/control.h>
#include <anatomist/controler/action.h>
%End

%TypeCode
#include <anatomist/window3D/control3D.h>
%End

%ConvertToSubClassCode
  if( dynamic_cast<anatomist::Control3D *>( sipCpp ) )
    sipType = sipType_anatomist_Control3D;
  else if( dynamic_cast<anatomist::Select3DControl *>( sipCpp ) )
    sipType = sipType_anatomist_Select3DControl;
  else if( dynamic_cast<anatomist::FlightControl *>( sipCpp ) )
    sipType = sipType_anatomist_FlightControl;
  else if( dynamic_cast<anatomist::ObliqueControl *>( sipCpp ) )
    sipType = sipType_anatomist_ObliqueControl;
  else if( dynamic_cast<anatomist::TransformControl *>( sipCpp ) )
    sipType = sipType_anatomist_TransformControl;
  else if( dynamic_cast<anatomist::CutControl *>( sipCpp ) )
    sipType = sipType_anatomist_CutControl;
  else
    sipType = 0;
%End

public:
  class KeyActionLink
  {
  public:
    virtual ~KeyActionLink();
    virtual void execute() = 0;
    virtual anatomist::Control::KeyActionLink* clone() const = 0 /Factory/;
  };

  class MouseActionLink
  {
  public:
    virtual ~MouseActionLink();
    virtual void execute( int, int, int, int ) = 0;
    virtual anatomist::Action* action() = 0;
    virtual anatomist::Control::MouseActionLink* clone() const = 0 /Factory/;
  };

  class WheelActionLink {
  public:
    virtual ~WheelActionLink() ;
    virtual void execute( int, int, int, int, int ) = 0 ;
    virtual anatomist::Control::WheelActionLink* clone() const = 0 /Factory/;
  };

  class SelectionChangedActionLink
  {
  public:
    virtual ~SelectionChangedActionLink();
    virtual void execute() = 0 ;
    virtual anatomist::Control::SelectionChangedActionLink*
      clone() const = 0 /Factory/;
  };

  Control( int, std::string );
  virtual ~Control();

  std::string name() const;
  virtual std::string description() const;
  int priority();
  int userLevel() const;
  void setUserLevel( int );
  void setPriority( int );
  virtual void doAlsoOnSelect( anatomist::ActionPool * );
  virtual void doAlsoOnDeselect( anatomist::ActionPool * );
  SIP_PYOBJECT actions();
%MethodCode
  std::map<std::string, anatomist::Action *> ac = sipCpp->actions();
  sipRes = PyDict_New();
  std::map<std::string, anatomist::Action *>::const_iterator i, e = ac.end();
  PyObject* action;
  for( i=ac.begin(); i!=e; ++i )
  {
    action = sipConvertFromType( i->second, sipType_anatomist_Action, 0 );
    PyDict_SetItemString( sipRes, i->first.c_str(), action );
    Py_DecRef( action );
  }
%End

  virtual void eventAutoSubscription( anatomist::ActionPool * );

  bool keyPressEventSubscribe( int, Qt::KeyboardModifiers, 
                               const anatomist::Control::KeyActionLink &,
                               const std::string & name = "" )
    /PyName=_keyPressEventSubscribe/;
  bool keyReleaseEventSubscribe( int, Qt::KeyboardModifiers, 
                                 const anatomist::Control::KeyActionLink &,
                                 const std::string & name = "" )
    /PyName=_keyReleaseEventSubscribe/;
  bool mousePressButtonEventSubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers,
      const anatomist::Control::MouseActionLink &,
      const std::string & name = "" )
    /PyName=_mousePressButtonEventSubscribe/;
  bool mouseReleaseButtonEventSubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers,
      const anatomist::Control::MouseActionLink &,
      const std::string & name = "" )
    /PyName=_mouseReleaseButtonEventSubscribe/;
  bool mouseDoubleClickEventSubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers,
      const anatomist::Control::MouseActionLink &,
      const std::string & name = "" )
    /PyName=_mouseDoubleClickEventSubscribe/;
  bool mouseMoveEventSubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers,
      const anatomist::Control::MouseActionLink &,
      const std::string & name = "" )
    /PyName=_mouseMoveEventSubscribe/;
  bool mouseLongEventSubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers,
      const anatomist::Control::MouseActionLink &, 
      const anatomist::Control::MouseActionLink &, 
      const anatomist::Control::MouseActionLink &, 
      bool )
    /PyName=_mouseLongEventSubscribe/;

  bool keyPressEventUnsubscribe( int, Qt::KeyboardModifiers );
  bool keyReleaseEventUnsubscribe( int, Qt::KeyboardModifiers );
  bool mousePressButtonEventUnsubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers );
  bool mouseReleaseButtonEventUnsubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers );
  bool mouseDoubleClickEventUnsubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers );
  bool mouseMoveEventUnsubscribe
    ( Qt::MouseButtons, Qt::KeyboardModifiers );
  bool mouseLongEventUnsubscribe( Qt::MouseButtons, Qt::KeyboardModifiers );

  bool wheelEventSubscribe( const WheelActionLink& actionMethod )
    /PyName=_wheelEventSubscribe/;
  bool wheelEventUnsubscribe();
  bool wheelEventUnsubscribeAll();
  bool selectionChangedEventSubscribe(
    const SelectionChangedActionLink& actionMethod )
    /PyName=_selectionChangedEventSubscribe/;
  bool selectionChangedEventUnsubscribe();

  set_STRING keyPressActionLinkNames() const;
  set_STRING keyReleaseActionLinkNames() const;
  set_STRING mousePressActionLinkNames() const;
  set_STRING mouseReleaseActionLinkNames() const;
  set_STRING mouseDoubleClickActionLinkNames() const;
  set_STRING mouseMoveActionLinkNames() const;
};


class ControlDictionary
{
%TypeHeaderCode
#include <anatomist/controler/controldictionary.h>
%End

public:
  class ControlCreatorBase
  {
  public:
    virtual ~ControlCreatorBase();
%#if SIP_VERSION == 0x040403%
    virtual anatomist::Control* operator () () /Factory/;
%#else%
    virtual anatomist::Control* operator () () =0 /Factory/;
%#endif%

  protected:
    ControlCreatorBase();
  };

  ~ControlDictionary();
  static anatomist::ControlDictionary* instance();

  anatomist::Control* getControlInstance( const std::string & );
  void addControl( const std::string &, 
                   anatomist::ControlDictionary::ControlCreatorBase *
                   /Transfer/,
                   int, bool allowreplace = false ) /PyName=_addControl/;
  bool removeControl( const std::string & );
  int testPriorityUnicity( int );

private:
  ControlDictionary();
  ControlDictionary( const anatomist::ControlDictionary & );
};


class ControlManager
{
%TypeHeaderCode
#include <anatomist/controler/controlmanager.h>
%End

public:
  static anatomist::ControlManager* instance();

  void addControl( const std::string &, const std::string &, 
                   const std::string & );
  void addControl( const std::string &, const std::string &, 
                   const set_STRING & );
  bool removeControl( const std::string &, const std::string &,
                      const std::string & );
  bool removeControlList( const std::string &, const std::string & );
  void print() const /PyName=printSelf/;
  set_STRING
    availableControlList( const std::string &, 
                          const list_STRING & ) const;
  set_STRING
    availableControlList( const std::string &, const std::string & ) const;
  set_STRING
    activableControlList( const std::string &, 
                          const list_STRING & ) const;

private:
  ControlManager();
  ControlManager( const anatomist::ControlManager & );
};


class IconDictionary
{
%TypeHeaderCode
#include <anatomist/controler/icondictionary.h>
%End

public:
  static anatomist::IconDictionary* instance();

  const QPixmap* getIconInstance( std::string ) const;
  void addIcon( std::string, const QPixmap & );

private:
  IconDictionary();
  IconDictionary( const anatomist::IconDictionary & );
};

}; // namespace anatomist


class ControlSwitch : QObject
{
%TypeHeaderCode
#include <anatomist/controler/controlswitch.h>
%End

public:
  virtual ~ControlSwitch();
  anatomist::Action* getAction( const std::string& actionName );
  std::string activeControl() const;
  anatomist::Control* activeControlInstance() const;
  std::string controlDescription( const std::string & ctrlname ) const;

  void keyPressEvent( QKeyEvent *) ;
  void keyReleaseEvent( QKeyEvent *) ;
  void mousePressEvent ( QMouseEvent * ) ;
  void mouseReleaseEvent ( QMouseEvent * ) ;
  void mouseDoubleClickEvent ( QMouseEvent * ) ;
  void mouseMoveEvent ( QMouseEvent * ) ;
  void wheelEvent ( QWheelEvent * ) ;
  void focusInEvent ( QFocusEvent * ) ;
  void focusOutEvent ( QFocusEvent * ) ;
  void enterEvent ( QEvent * ) ;
  void leaveEvent ( QEvent * ) ;
  void paintEvent ( QPaintEvent * ) ;
  void moveEvent ( QMoveEvent * ) ;
  void resizeEvent ( QResizeEvent * ) ;
  void dragEnterEvent ( QDragEnterEvent * ) ;
  void dragMoveEvent ( QDragMoveEvent * ) ;
  void dragLeaveEvent ( QDragLeaveEvent * ) ;
  void dropEvent ( QDropEvent * ) ;
  void showEvent ( QShowEvent * ) ;
  void hideEvent ( QHideEvent * ) ;
  void selectionChangedEvent();

  std::map<int, std::string> activableControls() const;
  std::map<int, std::string> availableControls() const;

protected:
  ControlSwitch( anatomist::View * view ) ;
};

