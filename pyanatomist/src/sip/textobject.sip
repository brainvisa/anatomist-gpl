namespace anatomist
{

  class TextObject : anatomist::ASurface_3
  {
%TypeHeaderCode
#include <anatomist/surface/textobject.h>
%End

  public:
    TextObject( const std::string & text="",
      const Point3df & pos=Point3df( 0,0,0 ) );
    virtual ~TextObject();
    const std::string & text() const;
    void setText( const std::string & );
    int type() const;
    virtual anatomist::GLComponent* glAPI();
    virtual bool isTransparent() const;
    void setFont( QFont *font /Transfer/ );
    QFont* font();
    void setScale( float );
    float scale() const;
    void setPosition( const Point3df & );
    Point3df position() const;
  };

};

