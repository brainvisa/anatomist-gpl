
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
                          const char * name = 0, int* alpha /In/ = 0,
                          bool *neutraph /In/ = 0, int* alphaout /out/ =0,
                          bool *neutraphout /Out/ = 0 );
%MethodCode
  int alpha = 255;
  bool neutralpha = false;
  alpha = a3;
  neutralpha = a4;
  sipRes = new QColor( QAColorDialog::getColor( *a0, a1, a2, &alpha,
    &neutralpha ) );
  a5 = alpha;
  a6 = neutralpha;
%End

  void relook( const QColor & col, int initalpha = 255,
               bool allowalpha = false, bool neutralpha = false,
               bool allownalph = false );

  QColor        color() const;
  int alpha() const;
  bool neutralAlpha() const;

signals:
  void colorChanged();
};

