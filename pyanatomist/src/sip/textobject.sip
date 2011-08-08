namespace anatomist
{

  class TextObject : anatomist::ASurface_3
  {
%TypeHeaderCode
#include <anatomist/surface/textobject.h>
%End

  public:
    TextObject( const std::string & text="" );
    virtual ~TextObject();
    const std::string & text() const;
    void setText( const std::string & );
    virtual int type() const;
    virtual anatomist::GLComponent* glAPI();
  };

};

