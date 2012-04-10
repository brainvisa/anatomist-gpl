
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


class QAWindowFactory: QObject, anatomist::AWindowFactory
{
%TypeHeaderCode
#include <anatomist/window/qWinFactory.h>
%End

public:
  struct PixList
  {
    PixList();
    PixList( const QPixmap & s, const QPixmap & l, const QPixmap & a );
    QPixmap     psmall;
    QPixmap     plarge;
    QPixmap     pactive;
  };

  struct Descrip
  {
    Descrip();
    Descrip( const QString & b, const QString & l );
    QString     brief;
    QString     longer;
  };

  static const QAWindowFactory::PixList & pixmaps( int type );
  static const QAWindowFactory::PixList & pixmaps( const std::string & type );
  static const QAWindowFactory::Descrip & description( int type );
  static const QAWindowFactory::Descrip & description( const std::string & type );
  static void setPixmaps( int type, const PixList & pix );
  static void setPixmaps( const std::string & type, const PixList & pix );
  static void loadDefaultPixmaps( int type );
  static void loadDefaultPixmaps( const std::string & type );
  static void setDescription( int type, const QAWindowFactory::Descrip & des );
  static void setDescription( const std::string & type, const QAWindowFactory::Descrip & des );
};

