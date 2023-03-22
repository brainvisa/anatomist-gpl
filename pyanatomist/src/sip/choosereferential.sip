
class ChooseReferentialWindow : QDialog, anatomist::Observer
{
%TypeHeaderCode
#include <anatomist/reference/wChooseReferential.h>
%End

public:
  ChooseReferentialWindow( const set_AObjectPtr &,
                           const char *name,
                           Qt::WindowFlags = Qt::WindowFlags() );
  ChooseReferentialWindow( const set_AWindowPtr &,
                           const char *name,
                           Qt::WindowFlags = Qt::WindowFlags() );
  ChooseReferentialWindow( const set_AWindowPtr &,
                           const set_AObjectPtr &,
                           const char *name,
                           Qt::WindowFlags = Qt::WindowFlags() );
  virtual ~ChooseReferentialWindow();

  void update(const anatomist::Observable* observable, void* arg);
  anatomist::Referential* selectedReferential() const;

public slots:
  void chooseRef( int );

protected:
  void drawContents( const char *name );
  virtual void unregisterObservable( anatomist::Observable* );
};

