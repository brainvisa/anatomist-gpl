namespace anatomist
{

class GLComponent
{
%TypeHeaderCode
#include <anatomist/object/Object.h>
#include <anatomist/mobject/ObjectList.h>
#include <anatomist/surface/glcomponent.h>
#include <pyanatomist/refglitem.h>
%End

%TypeCode
#include <pyaims/vector/numpyarrayfunc.h>
%End


public:
  enum glTextureMode
  {
    glGEOMETRIC,
    glLINEAR,
    glREPLACE,
    glDECAL,
    glBLEND,
    glADD,
    glCOMBINE,
    glLINEAR_ON_DEFINED,
  };

  enum glTextureFiltering
  {
    glFILT_NEAREST,
    glFILT_LINEAR,
  };

  enum glPart
  {
    glGENERAL,
    glBODY,
    glMATERIAL,
    glGEOMETRY,
    glPALETTE,
    glREFERENTIAL,
    glTEXIMAGE,
    glTEXENV,

    glNOPART,
    glTEXIMAGE_NUM,
    glTEXENV_NUM,
  };

  enum glAutoTexturingMode
  {
    glTEX_MANUAL,
    glTEX_OBJECT_LINEAR,
    glTEX_EYE_LINEAR,
    glTEX_SPHERE_MAP,
    glTEX_REFLECTION_MAP,
    glTEX_NORMAL_MAP,
  };


  class TexExtrema
  {
%TypeHeaderCode
#include <anatomist/surface/glcomponent.h>
#ifndef PYAIMSSIP_VECTOR_FLOAT_DEFINED
#define PYAIMSSIP_VECTOR_FLOAT_DEFINED
typedef std::vector<float> vector_FLOAT;
#endif
%End

  public:
    TexExtrema();
    virtual ~TexExtrema();

    vector_FLOAT	min;
    vector_FLOAT	max;
    vector_FLOAT	minquant;
    vector_FLOAT	maxquant;
    bool	scaled;
  };

  GLComponent();
  virtual ~GLComponent();

  virtual anatomist::GLComponent *glAPI() = 0;
  virtual const anatomist::GLComponent::TexExtrema &
    glTexExtrema(unsigned = 0) const;

  virtual void glSetChanged( anatomist::GLComponent::glPart,
    bool = true ) const;
  virtual bool glHasChanged( anatomist::GLComponent::glPart ) const;

  virtual void glSetTexImageChanged( bool x = true,
                                     unsigned tex = 0 ) const ;
  virtual void glSetTexEnvChanged( bool x = true, unsigned tex = 0 ) const;

  virtual anatomist::GLPrimitives glMainGLL( const anatomist::ViewState & );

  virtual bool glMakeBodyGLL( const anatomist::ViewState & state,
                              const anatomist::GLList & gllist ) const;
  virtual void glBeforeBodyGLL( const anatomist::ViewState & state,
                                anatomist::GLPrimitives & pl ) const;
  virtual void glAfterBodyGLL( const anatomist::ViewState & state,
                               anatomist::GLPrimitives & pl ) const;
  virtual bool glMakeTexImage( const anatomist::ViewState & state,
                              const anatomist::GLTexture & gltex,
                               unsigned tex ) const;
  virtual bool glMakeTexEnvGLL( const anatomist::ViewState & state,
                                const anatomist::GLList & gllist,
                                unsigned tex ) const;

  virtual unsigned glNumVertex( const anatomist::ViewState & ) const;
  virtual unsigned glNumPolygon( const anatomist::ViewState & ) const;
  virtual unsigned glNumTextures() const;
  virtual unsigned glNumTextures( const anatomist::ViewState & ) const;
  virtual anatomist::GLComponent::glTextureMode glTexMode
    ( unsigned tex = 0 ) const;
  virtual void glSetTexMode( anatomist::GLComponent::glTextureMode mode,
                             unsigned tex = 0 );
  virtual float glTexRate( unsigned tex = 0 ) const;
  virtual void glSetTexRate( float rate, unsigned tex = 0 );
  virtual anatomist::GLComponent::glTextureFiltering glTexFiltering
    ( unsigned tex = 0 ) const;
  virtual void glSetTexFiltering( anatomist::GLComponent::glTextureFiltering x,
                                  unsigned tex = 0 );
  virtual anatomist::GLComponent::glAutoTexturingMode glAutoTexMode
    ( unsigned tex = 0 ) const;
  virtual void glSetAutoTexMode
    ( anatomist::GLComponent::glAutoTexturingMode mode, unsigned tex = 0 );
  virtual GLint glGLTexMode( unsigned tex = 0) const;
  virtual GLint glGLTexFiltering( unsigned tex = 0 ) const;
  virtual void glSetTexRGBInterpolation( bool x, unsigned tex = 0 );
  virtual bool glTexRGBInterpolation( unsigned tex = 0 ) const;
  virtual unsigned glDimTex( const anatomist::ViewState &,
                             unsigned tex = 0 ) const;
  virtual unsigned glTexCoordSize( const anatomist::ViewState &,
                                   unsigned tex = 0 ) const;
  virtual bool glAllowedTexRGBInterpolation( unsigned tex = 0 ) const;
  virtual bool glAllowedTexRate( unsigned tex = 0 ) const;
  virtual std::string viewStateID( anatomist::GLComponent::glPart part,
    const anatomist::ViewState & ) const;
  virtual carto::Object debugInfo() const;

  SIP_PYOBJECT glVertexArray( const anatomist::ViewState & ) /Factory/;
%MethodCode
  std::vector<int> dims( 2, sipCpp->glNumVertex( *a0 ) );
  dims[1] = 3;

  PyArray_Descr *descr = PyArray_DescrFromType( NPY_FLOAT32 );
  sipRes = aims::initNumpyArray( sipSelf, descr, dims.size(),
                                 &dims[0],
                                 (char *) sipCpp->glVertexArray( *a0 ) );
%End

  SIP_PYOBJECT glNormalArray( const anatomist::ViewState & ) /Factory/;
%MethodCode
  if( sipCpp->glNormalArray( *a0 ) == 0 )
  {
    sipRes = Py_None;
    Py_INCREF( Py_None );
  }
  else
  {
    std::vector<int> dims( 2, sipCpp->glNumVertex( *a0 ) );
    dims[1] = 3;

    PyArray_Descr *descr = PyArray_DescrFromType( NPY_FLOAT32 );
    sipRes = aims::initNumpyArray( sipSelf, descr, dims.size(),
                                  &dims[0],
                                  (char *) sipCpp->glNormalArray( *a0 ) );
  }
%End

  SIP_PYOBJECT glPolygonArray( const anatomist::ViewState & ) /Factory/;
%MethodCode
  std::vector<int> dims( 2, sipCpp->glNumPolygon( *a0 ) );
  dims[1] = int( sipCpp->glPolygonSize( *a0 ) );

  PyArray_Descr *descr = PyArray_DescrFromType( NPY_INT32 );
  sipRes = aims::initNumpyArray( sipSelf, descr, dims.size(),
                                &dims[0],
                                (char *) sipCpp->glPolygonArray( *a0 ) );
%End

  SIP_PYOBJECT glTexCoordArray( const anatomist::ViewState &,
                                unsigned tex = 0 ) /Factory/;

%MethodCode
  if( sipCpp->glTexCoordArray( *a0, a1 ) == 0 )
  {
    sipRes = Py_None;
    Py_INCREF( Py_None );
  }
  else
  {
    std::vector<int> dims( 2, sipCpp->glNumVertex( *a0 ) );
    dims[1] = int( sipCpp->glDimTex( *a0, a1 ) );

    PyArray_Descr *descr = PyArray_DescrFromType( NPY_FLOAT32 );
    sipRes = aims::initNumpyArray(
      sipSelf, descr, dims.size(),
      &dims[0],
      (char *) sipCpp->glTexCoordArray( *a0, a1 ) );
  }
%End

  rc_ptr_Volume_RGBA glBuildTexImage(
    const anatomist::ViewState & state, unsigned tex, int dimx = -1,
    int dimy = -1, bool useTexScale = true ) const;
  virtual const Material *glMaterial() const;
  virtual const AObjectPalette* glPalette( unsigned tex = 0 ) const;
};

};

