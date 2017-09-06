namespace anatomist
{

  class MObjectIO
  {
%TypeHeaderCode
#include <anatomist/object/mobjectio.h>
%End

  public:

    static carto::Object readMObject( const std::string & filename );
    static carto::Object readMObject( carto::Object object_descr,
                                      const std::string & path = "" );

    static carto::Object createMObjectDescr( anatomist::AObject* aobject,
                                             const std::string & path = "",
                                             bool writeLeafs = true );
    static carto::Object createMObjectDescr( carto::Object aobject,
                                             const std::string & path = "",
                                             bool writeLeafs = true );
    static bool writeMObject( anatomist::AObject* aobject,
                              const std::string & filename,
                              bool writeLeafs = true );
    static bool writeMObject( carto::Object aobject,
                              const std::string & filename,
                              bool writeLeafs = true );
    static bool saveDescription( carto::Object aobject,
                                 const std::string & filename,
                                 bool writeLeafs = true );
  };

};

