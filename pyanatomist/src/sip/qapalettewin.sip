

namespace anatomist
{

  class APaletteExtensionAction : QAction
  {
%TypeHeaderCode
#include <anatomist/color/qwObjPalette.h>
%End

  public:
    APaletteExtensionAction( QObject* parent );
    APaletteExtensionAction( const QString & text, QObject * parent );
    APaletteExtensionAction( const QIcon & icon, const QString & text, 
                             QObject * parent );
    virtual ~APaletteExtensionAction();

    virtual void extensionTriggered( const set_AObjectPtr & ) = 0;
  };

};

class QAPaletteWin : QWidget
{
%TypeHeaderCode
#include <anatomist/color/qwObjPalette.h>
%End

public:
  static void addExtensionAction( 
    anatomist::APaletteExtensionAction* action /Transfer/ );

private:
  QAPaletteWin();
};

