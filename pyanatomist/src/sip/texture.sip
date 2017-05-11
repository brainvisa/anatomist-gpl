namespace anatomist
{

  class ATexture : anatomist::AObject, anatomist::GLComponent
  {
%TypeHeaderCode
#include <anatomist/surface/texture.h>
%End

%TypeCode
#include <aims/vector/vector.h>
%End

  public:
    ATexture();
    virtual ~ATexture();

    virtual unsigned size( float time = 0 ) const;
    virtual float textureTime( float time ) const;
    virtual unsigned glNumTextures() const;
    virtual unsigned glNumTextures( const anatomist::ViewState & ) const;
    virtual unsigned glDimTex( const anatomist::ViewState &, unsigned tex = 0 ) const;
    virtual unsigned glTexCoordSize( const anatomist::ViewState &,
                                     unsigned tex = 0 ) const;

    virtual bool Is2DObject();
    virtual bool Is3DObject();

    virtual float MinT() const;
    virtual float MaxT() const;
    virtual float MinT3D() const;
    virtual float MaxT3D() const;
    virtual unsigned dimTexture() const;

    virtual anatomist::AObject* ObjectAt( float, float, float, float, float = 0 );

    virtual void setTexExtrema();
    void setTexExtrema(float min,float max);

    virtual void normalize();
    void setTexture( rc_ptr_TimeTexture_FLOAT, bool = false );
    void setTexture( rc_ptr_TimeTexture_POINT2DF, bool = false );
    void setTexture( rc_ptr_TimeTexture_S16, bool = false );
    void setTexture( rc_ptr_TimeTexture_S32, bool = false );
    void setTexture( rc_ptr_TimeTexture_U32, bool = false );
    rc_ptr_TimeTexture_FLOAT texture1d( bool rescaled = false,
                                        bool always_copy = false );
%MethodCode
  sipRes = new rc_ptr_TimeTexture_FLOAT( sipCpp->texture<float>( a0, a1 ) );
%End

    rc_ptr_TimeTexture_POINT2DF texture2d( bool rescaled = false,
                                           bool always_copy = false );
%MethodCode
  sipRes = new rc_ptr_TimeTexture_POINT2DF( sipCpp->texture<Point2df>( a0, a1 ) );
%End

    virtual void createDefaultPalette( const std::string & name = "" );
    virtual void update( const anatomist::Observable* observable, void* arg );
    virtual void notifyObservers( void * = 0 );
    virtual void setInternalsChanged();

    virtual bool loadable() const;
    virtual bool savable() const;
    virtual bool reload( const std::string & filename );
    bool save( const std::string & filename );
    virtual anatomist::AObject* clone( bool shallow = true );
  };

};

