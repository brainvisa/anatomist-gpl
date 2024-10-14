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
  float min1() const;
  float max1() const;
  float min2() const;
  float max2() const;
  void setMin1( float x );
  void setMax1( float x );
  void setMin2( float x );
  void setMax2( float x );

  float absMin1( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute min for a given object
%End
  float absMax1( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute max for a given object
%End
  float absMin2( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute min for a given object
%End
  float absMax2( const anatomist::AObject * obj ) const;
%Docstring
  get the absolute max for a given object
%End
  void setAbsMin1( const anatomist::AObject * obj, float x );
%Docstring
  set the min from an absolute value for a given object
%End
  void setAbsMax1( const anatomist::AObject * obj, float x );
%Docstring
  set the max from an absolute value for a given object
%End
  void setAbsMin2( const anatomist::AObject * obj, float x );
%Docstring
  set the min from an absolute value for a given object
%End
  void setAbsMax2( const anatomist::AObject * obj, float x );
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
  QImage* toQImage( int w = 0, int h = 0 );
  rc_ptr_Volume_RGBA toVolume( int w = 0, int h = 0, bool scaled = true );

  /** Maximum size of the internal palette image.
      0 means unused: no palette image is needed.
      -1 means no limit: may grow as large as the reference palette image
      -2 means unchanged
    */
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
  AimsRGBA normColor( float x, float y = 0 ) const;
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

};

