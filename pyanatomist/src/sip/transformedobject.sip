
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
                       const Point3df & pos=Point3df( 0, 0, 0 ),
                       bool strongref=false );
    virtual ~TransformedObject();

    virtual bool renderingIsObserverDependent() const;
    virtual bool render( anatomist::GLPrimitives &,
      const anatomist::ViewState & );
    void setPosition( const Point3df & );
    Point3df position() const;
    void setOffset( const Point3df & );
    Point3df offset() const;
    void setDynamicOffsetFromPoint( const Point3df & );
    void removeDynamicOffset();
    bool usesDynamicOffset() const;
    Point3df dynamicOffsetFromPoint() const;
    void setScale( float scale );
    float scale() const;
    virtual anatomist::GLComponent* glAPI();
  };

};

