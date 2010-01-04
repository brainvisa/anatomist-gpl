
namespace anatomist
{

  /* NOTE:
  These creation functions are *not* factories, since the returned window
  never belongs to python but always to C++ since ref-counting takes place
  in C++.
  */

  class AWindowCreator
  {
%TypeHeaderCode
#include <anatomist/window/winFactory.h>
%End

  public:
    virtual ~AWindowCreator();
    virtual anatomist::AWindow* operator()
      ( void *dock, carto::Object ) const = 0;
  };


  class AWindowFactory
  {
%TypeHeaderCode
#include <anatomist/window/winFactory.h>
%End

  public:
    static anatomist::AWindow* createWindow( const std::string & type,
      void *dock = 0, carto::Object params = carto::none() );
    static anatomist::AWindow* createWindow( int type, void *dock = 0, 
      carto::Object params = carto::none() );
    static bool initTypes();
    static std::string typeString( int type, int subtype = 0 );
    static int typeID( const std::string & type );
    static bool exist( int type );
    static bool exist( const std::string & type );
    static int registerType( const std::string & type,
      anatomist::AWindowCreator *creator /Transfer/ );
    static set_STRING types();
    // static const std::map<std::string, int> & typeID();
    // static const map_S32_STRING & typeNames();
  };

};

