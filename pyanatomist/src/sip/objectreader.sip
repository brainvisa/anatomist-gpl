
namespace anatomist
{

  class ObjectReader
  {
%TypeHeaderCode
#include <anatomist/object/oReader.h>
%End

  public:
    class PostRegisterList
    {
    public:
      ~PostRegisterList();
    };

    class LoadFunctionClass
    {
    public:
      virtual ~LoadFunctionClass();
      virtual anatomist::AObject* load( const std::string & filename,
        anatomist::ObjectReader::PostRegisterList &,
        carto::Object options ) = 0;
    };

    ObjectReader();
    virtual ~ObjectReader();

    static anatomist::ObjectReader* reader();

    static void registerLoader( const std::string & extension,
      anatomist::ObjectReader::LoadFunctionClass *newFunc /Transfer/ );

    anatomist::AObject* load( const std::string & filename,
                                      bool notifyFail = true,
                                      carto::Object options = carto::none()
                                    ) const /ReleaseGIL/;
%MethodCode
  anatomist::ObjectReader::PostRegisterList prl;
  sipRes = sipCpp->load( *a0, prl, a1, *a2 );
%End

    virtual bool reload( anatomist::AObject* object, bool notifyFail = true, 
                         bool onlyoutdated = false ) const;
  };

}; // namespace anatomist

