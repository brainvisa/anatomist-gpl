
namespace anatomist
{

  class TransformedObject : anatomist::ObjectVector, anatomist::GLComponent
  {
%TypeHeaderCode
#include <anatomist/surface/transformedobject.h>
%End

  public:
    TransformedObject( const vector_AObjectPtr &,
                       bool followorientation=true,
                       bool followposition=false,
                       const Point3df & posoffset=Point3df( 1, 1, 0 ) );
    virtual ~TransformedObject();

    virtual bool renderingIsObserverDependent() const;
    virtual bool render( anatomist::GLPrimitives &,
      const anatomist::ViewState & );
  };

};

