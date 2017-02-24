namespace anatomist
{

  class MObjectIO
  {
%TypeHeaderCode
#include <anatomist/object/mobjectio.h>
%End

  public:

    static carto::Object readMObject( carto::Object object_descr,
                                      const std::string & path = "" );

    static carto::Object writeMObject( anatomist::AObject* aobject,
                                       const std::string & path = "" );
    static carto::Object writeMObject( carto::Object aobject,
                                       const std::string & path = "" );
  };

};

