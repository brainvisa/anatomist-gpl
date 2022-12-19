
%ModuleCode
#if SIP_VERSION >= 0x040700
#include <anatomist/control/wControl.h>
#include <anatomist/window3D/window3D.h>
#endif
%End


class ControlWindow : QMainWindow
{

%TypeHeaderCode
#include <anatomist/control/wControl.h>
#include <anatomist/window/Window.h>
%End

/* not available in Qt4...
%TypeCode
#include <anatomist/control/controlMenuHandler.h>
#include <anatomist/selection/qSelMenu.h>
%End
*/

%ConvertToSubClassCode
  if( dynamic_cast<ControlWindow *>( sipCpp ) )
    sipType = sipType_ControlWindow;
  else
    if( dynamic_cast<QAWindow *>( sipCpp ) )
      if( dynamic_cast<ControlledWindow *>( sipCpp ) )
        if( dynamic_cast<AWindow3D *>( sipCpp ) )
          sipType = sipType_AWindow3D;
        else
          sipType = sipType_ControlledWindow;
      else
        sipType = sipType_QAWindow;
    else
      sipType = 0;
%End

public:
  ControlWindow();
  virtual ~ControlWindow();

  set_AWindowPtr selectedWindows();
  void SelectWindow(anatomist::AWindow *win);
  void UnselectAllWindows();
  void enableClose( bool );
  bool closeEnabled() const;

/* not available in Qt4...
  QPopupMenu* getPopup( const std::string & name );
%MethodCode
  anatomist::AControlMenuHandler* mh = sipCpp->menuHandler();
  sipRes = mh->getPopup( *a0 );
%End
*/
};


