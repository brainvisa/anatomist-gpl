
class QAColorDialog : QDialog
{
%TypeHeaderCode
#include <anatomist/dialogs/colorDialog.h>
%End

public:
  QAColorDialog( QColor, QWidget * parent = 0, const char * name = 0,
                 bool modal = true, bool allowAlpha = false,
                 bool allowNeutralAlpha = false, int initalpha = 255,
                 bool neutralph = false );
  virtual ~QAColorDialog();

  static QColor getColor( QColor, QWidget * parent = 0,
                          const char * name = 0, int* alpha /In, out/ = 0,
                          bool *neutraph /In, Out/ = 0 );
  void relook( const QColor & col, int initalpha = 255,
               bool allowalpha = false, bool neutralpha = false,
               bool allownalph = false );

  QColor        color() const;
  int alpha() const;
  bool neutralAlpha() const;

signals:
  void colorChanged();
};

