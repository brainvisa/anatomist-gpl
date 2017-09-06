
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
      virtual list_AObjectPtr load( const std::string & filename,
        anatomist::ObjectReader::PostRegisterList &,
        carto::Object options ) = 0;
    };

    ObjectReader();
    virtual ~ObjectReader();

    static anatomist::ObjectReader* reader();

    static void registerLoader( const std::string & extension,
      anatomist::ObjectReader::LoadFunctionClass *newFunc /Transfer/ );

    list_AObjectPtr *load( const std::string & filename,
                                      bool notifyFail = true,
                                      carto::Object options = carto::none()
                                    ) const /ReleaseGIL, Factory/;
%MethodCode
  anatomist::ObjectReader::PostRegisterList prl;
  std::list<anatomist::AObject *> obj = sipCpp->load( *a0, prl, a1, *a2 );
  sipRes = new std::list<anatomist::AObject *>( obj );
%End

    virtual bool reload( anatomist::AObject* object, bool notifyFail = true, 
                         bool onlyoutdated = false ) const;
  };

}; // namespace anatomist

