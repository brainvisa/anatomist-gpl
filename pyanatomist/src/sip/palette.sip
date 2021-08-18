namespace anatomist
{

class APalette // : AimsData_RGBA
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
  bool zeroCenteredAxis1() const;
  bool zeroCenteredAxis2() const;
  void setZeroCenteredAxis1( bool );
  void setZeroCenteredAxis2( bool );
  void create( unsigned dimx, unsigned dimy = 1, unsigned dimz = 1,
               unsigned dimt = 1 );
  virtual void fill();
  bool isTransparent() const;
  AimsData_RGBA* colors ();
  QImage* toQImage( int w = 0, int h = 0 );
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

