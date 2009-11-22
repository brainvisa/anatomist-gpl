namespace anatomist
{

  class GlobalConfiguration : Tree
  {
%TypeHeaderCode
#include <anatomist/application/globalConfig.h>
%End

    public:
      GlobalConfiguration();
      virtual ~GlobalConfiguration();

      virtual std::string configFilename( const std::string & initial );
      virtual void load( const std::string & filename = "" );
      virtual void apply();
      virtual void update();
      virtual void save( const std::string & filename = "" );

//      void registerLocalConfiguration( LocalConfiguration* cfg );
//      void unregisterLocalConfiguration( LocalConfiguration* cfg );
  };

};

