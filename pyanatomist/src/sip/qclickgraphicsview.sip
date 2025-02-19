

class QClickGraphicsView: public QGraphicsView
{
%TypeHeaderCode
#include <anatomist/dialogs/qclickgraphicsview.h>
%End

%Docstring
    QGraphicsView which emits signal for mouse press, move and release
    events.

    The normal QGraphicsView captures such events and does not expose them, so
    a widget containing the graphics view cannot react to mouse events, even if
    the graphics view does nothing with them.
%End

public:

  virtual ~QClickGraphicsView();

signals:
  void mousePressed( QMouseEvent * );
%Docstring
  signal emitted upon mouse press event
%End

  void mouseMoved( QMouseEvent * );
%Docstring
  signal emitted upon mouse move event
%End

  void mouseReleased( QMouseEvent * );
%Docstring
  signal emitted upon mouse release event
%End

protected:
  virtual void mousePressEvent( QMouseEvent *event );
  virtual void mouseMoveEvent( QMouseEvent *event );
  virtual void mouseReleaseEvent( QMouseEvent *event );
};

