
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
                       const Point3df & pos=Point3df( 0, 0, 0 ) );
    virtual ~TransformedObject();

    virtual bool renderingIsObserverDependent() const;
    virtual bool render( anatomist::GLPrimitives &,
      const anatomist::ViewState & );
    void setPosition( const Point3df & );
    Point3df position() const;
    void setOffset( const Point3df & );
    Point3df offset() const;
  };

};

