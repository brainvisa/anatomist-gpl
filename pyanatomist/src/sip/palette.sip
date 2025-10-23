namespace anatomist
{

class APalette : Volume_RGBA
{
%TypeHeaderCode
#include <anatomist/color/palette.h>
%End

public:
  APalette(const std::string & = "", unsigned = 256,
	unsigned = 1, unsigned = 1, unsigned = 1);
  virtual ~APalette();

  std::string name() const;
  void setName( const std::string & );
  bool isTransparent() const;
  void update();
};


class AObjectPalette
{
%TypeHeaderCode
#include <anatomist/color/objectPalette.h>
%End

public:
  AObjectPalette( rc_ptr_APalette );
  AObjectPalette(const anatomist::AObjectPalette &);
  virtual ~AObjectPalette();

  rc_ptr_APalette refPalette() const;
  rc_ptr_APalette refPalette2() const;
  void setRefPalette( rc_ptr_APalette pal );
  void setRefPalette2( rc_ptr_APalette pal );
  double min1() const;
  double max1() const;
  double min2() const;
  double max2() const;
  void setMin1( double x );
  void setMax1( double x );
  void setMin2( double x );
  void setMax2( double x );
  double relValue1( const AObject * obj, double absval ) const;
  double relValue2( const AObject * obj, double absval ) const;
  double absValue1( const AObject * obj, double relval ) const;
  double absValue2( const AObject * obj, double relval ) const;

  double absMin1( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute min for a given object
%End
  double absMax1( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute max for a given object
%End
  double absMin2( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute min for a given object
%End
  double absMax2( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute max for a given object
%End
  void setAbsMin1( const anatomist::AObject * obj, double x );
%Docstring
  set the min from an absolute value for a given object
%End
  void setAbsMax1( const anatomist::AObject * obj, double x );
%Docstring
  set the max from an absolute value for a given object
%End
  void setAbsMin2( const anatomist::AObject * obj, double x );
%Docstring
  set the min from an absolute value for a given object
%End
  void setAbsMax2( const anatomist::AObject * obj, double x );
%Docstring
  set the max from an absolute value for a given object
%End

  bool zeroCenteredAxis1() const;
  bool zeroCenteredAxis2() const;
  void setZeroCenteredAxis1( bool );
  void setZeroCenteredAxis2( bool );
  void create( unsigned dimx, unsigned dimy = 1, unsigned dimz = 1,
               unsigned dimt = 1 );
  virtual void fill();
  bool isTransparent() const;
  Volume_RGBA* colors ();
  QImage* toQImage( int w = 0, int h = 0, double min1 = 0., double max1 = 1.,
                    double zero1 = 0.5, double min2 = 0., double max2 = 1.,
                    double zero2 = 0.5 ) const;
%Docstring
    qimage = palette.toQImage(w=0, h=0, min1=0., max1=1., min2=0., max2=1.)

    Get the palette image in a QImage.

    The image takes into account the palette min/max settings.

    Extra optional parameters allow to scale the image. They are not
    interpreted the same way as min/max bounds (which determine where on
    the palette image the object extrema are mapped), but at the contrary,
    allow to zoom the palette view on specific object values bounds.
%End

  rc_ptr_Volume_RGBA toVolume( int w = 0, int h = 0, bool scaled = true );

  int maxSizeX() const;
%Docstring
maxSizeX()
Maximum size of the internal palette image.
0 means unused: no palette image is needed.
-1 means no limit: may grow as large as the reference palette image
-2 means unchanged
%End

  int maxSizeY() const;
  void setMaxSize( int maxsizex, int maxsizey );
%Docstring
  setMaxSize(sx, sy)
%End

  int glMaxSizeX() const;
%Docstring
glMaxSizeX()
Maximum size of the OpenGL palette image, after scaling.
0 means unused: no GL palette image is needed.
-1 means no limit: may grow as large as the reference palette image
-2 means unchanged
%End
  int glMaxSizeY() const;
  void glSetMaxSize( int glmaxsizex, int glmaxsizey );
  AimsRGBA normColor( double x, double y = 0 ) const;
  AimsRGBA normColor( const Point2df & pos ) const;
};


class PaletteList
{
%TypeHeaderCode
#include <anatomist/color/paletteList.h>
%End

public:
  virtual ~PaletteList();

  unsigned size() const;
  virtual void load( const std::string &dirname, bool clr=false );
  virtual void save( const std::string &dirname, bool bin=false ) const;
  virtual void clear();
  virtual void erase( rc_ptr_APalette pal );
  virtual void push_back( rc_ptr_APalette pal );
  rc_ptr_APalette find( const std::string & );
  const list_rc_ptr_APalette & palettes() const;

private:
  PaletteList();
};


  class PaletteSelectWidget : public QTableWidget
  {
%TypeHeaderCode
#include <anatomist/color/paletteselectwidget.h>
%End

  public:
    PaletteSelectWidget( QWidget *parent = 0,
                         const std::string & selected = "",
                         bool allow_none = false );
    virtual ~PaletteSelectWidget();
    std::string selectedPalette() const;
    void selectPalette( const std::string & name );

    static void fillPalette( const rc_ptr_APalette pal,
                             QPixmap & pix );

  signals:
    void paletteSelected( const std::string & palette );
  };

};

