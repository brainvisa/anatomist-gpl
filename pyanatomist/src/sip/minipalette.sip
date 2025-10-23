

namespace anatomist
{

  class MiniPaletteGraphics : anatomist::Observer
  {
%Docstring
      MiniPaletteGraphics is an element which draws a palette in a
      GraphicsView scene. It is used by MiniPaletteWidget, but can be used
      alone in a QGraphicsView.

      It provides a small sized palette widget which can be used to display
      the palette.

      The palette view displayes the palette assigned to an object, and the
      view may be zoomed to a given values range.
%End

%TypeHeaderCode
#include <anatomist/color/minipalette.h>
%End

  public:
    MiniPaletteGraphics( QGraphicsView *graphicsview,
                         anatomist::AObject *object=0, int dim=0,
                         float width=-10000, float height=-10000,
                         float left=-10000, float top=-10000,
                         bool with_view=true );
%Docstring
      Parameters
      ----------
      graphicsview:
          the existing graphic view where the palette should be drawn
      object:
          object to display or edit the palette for
      width:
          width of the display in the graphics view. -10000 (default) means
          whole scene width.
      height:
          height of the display in the graphics view. -10000 (default) means
          whole scene height.
      left:
          left position of the display in the graphics view. -10000 (default)
          means centered in scene.
      top:
          top position of the display in the graphics view. -10000 (default)
          means centered in scene.
      with_view: bool
          if False, the palette view will not be displayed.
%End

    virtual ~MiniPaletteGraphics();

    anatomist::AObject *getObject();
    void setObject( anatomist::AObject *obj, int dims=1 );
%Docstring
    set or change the observed object. dim is the texure dimension observed
%End

    void setRange( double min, double max, int dim );
    void updateDisplay();
    void resize( float x, float y, float w, float h );
    float width() const;
    float height() const;
    float top() const;
    float left() const;
    void clear();
    virtual void update( const anatomist::Observable *observable, void *arg );
    double min( int dim ) const;
    double max( int dim ) const;
    int observedDimensions() const;

  private:
    MiniPaletteGraphics( const anatomist::MiniPaletteGraphics & );
  };


  class MiniPaletteWidget: public QWidget
  {
%Docstring
    MiniPaletteWidget.

    It provides a small sized palette widget which can be used both to display
    the palette in a GUI, and to edit the palette range (optionally).

    The palette view displayes the palette assigned to an object, and the view
    may be zoomed to a given values range.

    The palatte may be zoomed in/out using the mouse wheel. This action will
    not change the palette settings, but only the view displayed.

    Edition is possible if enabled, either using the allow_edit constructor
    parameter, or using the method :meth:`allow_edit`.

    Edition is triggered in 2 modes:

    - if ``click_to_edit`` is True (the default), a click on the palette will
      open the editor mode.
    - otherwise a mouse hover will open it, and it will be closed when the
      mouse leaves the editor, without the need for a user click.

    The edition mode opens a popup frameless widget, with sliders.
    \see MiniPaletteWidgetTranscient.
%End

%TypeHeaderCode
#include <anatomist/color/minipalette.h>
%End

  public:
    MiniPaletteWidget( anatomist::AObject *object = 0, int dim = 0,
                       bool allow_edit = true,
                       bool self_parent = true, QWidget *edit_parent = 0,
                       bool click_to_edit = true, bool auto_range = false,
                       bool with_view = true );
%Docstring
        Parameters
        ----------
        object: :class:`AObject` or None
            object to display or edit the palette for
        dim: int
            texture dimension observed
        allow_edit: bool
            if True, an editor will popup, either by clicking on the widget, or
            by "hovering" it if ``click_to_edit`` is False.
        edit_parent: :class:`QWidget` or None or 0
            the parent widget passed to the editor widget, if edition is
            allowed. The special value ``0`` means that the parent will be the
            :class:`MiniPaletteWidget`, ``self``.
        click_to_edit: bool
            if False, the edition widget will popup as soon as the mouse cursor
            passes over the palette widget, without clicking.
            If True, only a user click will open the editor window.
        auto_range: bool
            For edition mode, allow the auto-zoom mode when palette range is
            modified.
      with_view: bool
          if False, the palette view will not be displayed.
%End

    virtual ~MiniPaletteWidget();
    anatomist::AObject *getObject();
    void setObject( anatomist::AObject *obj, int dim = 0 );
    void allowEdit( bool allow, bool self_parent = true,
                    QWidget *edit_parent = 0 );
%Docstring
        Enalbes or disable the edition capabilities

        Parameters
        ----------
        allow: bool
            if True, an editor will popup, either by clicking on the widget, or
            by "hovering" it if ``click_to_edit`` is False.
        edit_parent: :class:`QWidget` or None or 0
            the parent widget passed to the editor widget, if edition is
            allowed. The special value ``0`` means that the parent will be the
            :class:`MiniPaletteWidget`, ``self``.
%End

    void setRange( double min, double max );
%Docstring
        set the view range in object values
%End

    void updateDisplay();
%Docstring
        redraws the palette view
%End

    void clear();
    void showEditor();
%Docstring
        pops up the editor, if the edition is allowed
%End

    void hideEditor();
    anatomist::MiniPaletteGraphics *miniPaletteGraphics();
    QGraphicsView *graphicsView();
    int observedDimension() const;

  signals:
    void rangeChanged( double, double );
    void paletteClicked();
  };


  class MiniPaletteWidgetEdit : public QWidget, public anatomist::Observer
  {
%Docstring
    Mini palette editor widget.

    :class:`MiniPaletteWidgetEdit` is part of the :class:`MiniPaletteWidget`
    infrastructure and in most cases will not be used directly.

    However a GUI may incorporate the editor widget.

    It is normally used within :class:`MiniPaletteWidgetTranscient`, itself
    used in the edition mode of :class:`MiniPaletteWidget`. In turn,
    :class:`MiniPaletteWidgetEdit` contains a non-editable
    :class:`MiniPaletteWidget` object.

    The editor thus presents a palette view, plus 2 sliders to set the min and
    max range of the palette. The view may be zoomed using the mouse wheel (see
    :class:`MiniPaletteWidget`), and it can also use an automatic zoom mode, if
    ``auto_range=True`` is passed to the constructor, or :meth:`set_auto_range`
    is called. In auto range mode, the zoom range is adapted after each user
    interaction on sliders (after the mouse is released).
%End

%TypeHeaderCode
#include <anatomist/color/minipalette.h>
%End

  public:
    MiniPaletteWidgetEdit( anatomist::AObject *object=0,
                           int dim = 0,
                           bool auto_range=false,
                           bool with_view = true,
                           bool allow_no_palette = false );
    virtual ~MiniPaletteWidgetEdit();

    void setObject( anatomist::AObject *obj, int dim = 0 );
    AObject* getObject();
    void updateDisplay();
%Docstring
        redraws the palette and sliders values
%End

    virtual void update( const anatomist::Observable *observable, void *arg );
    anatomist::MiniPaletteWidget *miniPaletteWidget();
    QSlider *minSlider();
    QSlider *maxSlider();
    int observedDimension() const;

  public slots:
    void adjustRange();
%Docstring
        auto-range function
%End

    void setAutoRange( bool auto_range );
%Docstring
        allows or disables the auto-zoom mode
%End

    void minChanged( double value );
    void maxChanged( double value );
    void setRange( double rmin, double rmax );
    void selectPalette();
    void setPalette( const std::string & palname );
    void gvMoved( QMouseEvent *event );
    void clearAutoBtn();
  };


  class MiniPaletteWidgetTranscient : public QWidget
  {
%Docstring
    The transcient palette editor widget features a
    :class:`MiniPaletteWidgetEdit` which shows up upon given conditions (see
    :class:`MiniPaletteWidget`) and closes when the editor widget loses focus.

    More precisely, if opened by a click, a complete focus loss is needed to
    close the window (which is generally triggered by another user action like
    a click at some other place or a keyboard focus change, using <tab> for
    instance).

    If not opened by a click, the widget will close as soon as the mouse
    pointer leaves the widget surface, or when the focus is lost, thus not
    requiring a click or keyboard user action.
%End

%TypeHeaderCode
#include <anatomist/color/minipalette.h>
%End

  public:
    MiniPaletteWidgetTranscient( anatomist::AObject *object = 0,
                                 int dim = 0,
                                 anatomist::MiniPaletteWidget* pw = 0,
                                 QWidget *parent = 0,
                                 bool opened_by_click = false,
                                 bool auto_range = false );
    virtual ~MiniPaletteWidgetTranscient();
    void reposition();
%Docstring
        Repositions / resizes the widget to superpose on its
        :class:`MiniPaletteWidget`
%End

    anatomist::MiniPaletteWidgetEdit* editor();

  public slots:
    void closeIfFinished();
    void sliderPressed();
    void sliderReleased();

  signals:
    void editorClosed();
%Docstring
    signal emitted when the editor widget closes
%End
  };

};

