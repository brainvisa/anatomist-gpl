

namespace anatomist
{

  class QMagnetSlider: QSlider
  {
%Docstring
  /** Specialized slider with "magnet" values, used for
    MiniPaletteWidgetEdit.

    It features float min/max values (typically matching an AObject texture
    values),
    magnets which mark some given significant values, and emits signals when
    the slider is moved.

    The values range can be changed afterwards.
%End

%TypeHeaderCode
#include <anatomist/dialogs/qmagnetslider.h>
%End

  public:
    QMagnetSlider( Qt::Orientation orientation = Qt::Vertical,
                   QWidget *parent = nullptr );
    virtual ~QMagnetSlider();

    void setMagnets( const set_FLOAT & magnets );
%Docstring
    Magnets are "attractive" values, where the mouse must be moved
    further to pass them when moving the slider.
%End

    void setDefault( float value );
    void setAbsRange( float min1, float max1 );
    void setAbsValue( float value );
    float absValue() const;
    void resetDefault();

  signals:
    void absValueChanged( float );
    void sliderPressed( const std::string & );
    void sliderMoved( const std::string & );
    void sliderReleased( const std::string & );
    void sliderDoubleClicked();
  };


};

