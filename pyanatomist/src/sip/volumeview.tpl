
namespace anatomist
{

  class AVolumeView_%Template1typecode% : anatomist::ObjectVector
  {
%TypeHeaderCode
  #include <anatomist/volume/volumeview.h>
  #ifndef PYANATOMIST_VOLUMEVIEW_%Template1typecode%_DEFINED
  #define PYANATOMIST_VOLUMEVIEW_%Template1typecode%_DEFINED
  namespace anatomist
  {
    typedef anatomist::AVolumeView<%Template1% > AVolumeView_%Template1typecode%;
  }
  #endif
%End

  public:
    AVolumeView_%Template1typecode%( const list_AObjectPtr & );
    AVolumeView_%Template1typecode%( const std::string & filename );
    AVolumeView_%Template1typecode%( rc_ptr_Volume_%Template1typecode% vol );
    AVolumeView_%Template1typecode%( SIP_PYOBJECT )
      [( const std::vector<carto::rc_ptr<carto::Volume<%Template1% > > > & )];
%MethodCode
  if( !PySequence_Check( a0 ) )
  {
    sipIsErr = 1;
    PyErr_SetString( PyExc_TypeError, "wrong argument type" );
  }
  else
  {
    unsigned	i, n = PySequence_Size( a0 );
    std::vector<carto::rc_ptr<carto::Volume<%Template1% > > > vec;
    vec.reserve( n );
    PyObject	*pyitem;
    const sipTypeDef* st
      = sipFindType( "rc_ptr_Volume_%Template1typecode%" );
    if( !st )
    {
      sipIsErr = 1;
      PyErr_SetString( PyExc_TypeError, "cannot find SIP type for rc_ptr_Volume_%Template1typecode%" );
    }
    else
    {
      for( i=0; i<n && !sipIsErr; ++i )
      {
        pyitem = PySequence_GetItem(a0,i);
        bool ok = false;
        if( pyitem )
        {
          if( st && sipCanConvertToType( pyitem, st, SIP_NOT_NONE ) )
          {
            ok = true;
          }
        }
        if( !ok )
        {
          sipIsErr = 1;
          std::ostringstream s;
          s << "wrong list item type, item " << i;
          PyErr_SetString( PyExc_TypeError, s.str().c_str() );
          if( pyitem )
            Py_DECREF( pyitem );
          break;
        }

        int state = 0;
        carto::rc_ptr<carto::Volume<%Template1% > > *item
          = reinterpret_cast<carto::rc_ptr<carto::Volume<%Template1% > > *>(
            sipConvertToType( pyitem, st, 0, SIP_NOT_NONE, &state,
                              &sipIsErr ) );
        if( item && !sipIsErr )
        {
          vec.push_back( *item );
          sipReleaseType( item, st, state );
        }
        Py_DECREF( pyitem );
      }
      if( !sipIsErr )
        sipCpp = new sipanatomist_AVolumeView_%Template1typecode%( vec );
    }
  }
%End

    virtual ~AVolumeView_%Template1typecode%();

    virtual void setVolume( rc_ptr_Volume_%Template1typecode% vol );

    void setupTransformationFromView();
    void setupViewFromTransformation();
    void setTargetSize( vector_S32 & );
    const vector_S32 & targetSize() const;
    int resolutionLevel() const;
    int selectBestResolutionLevel( const Point3df & vs ) const;
    rc_ptr_AObject view();
%MethodCode
    sipRes = new carto::rc_ptr<anatomist::AObject>( sipCpp->view().get() );
%End

    Point3df initialFOV() const;
    void setInitialFOV( const Point3df & fov );

    // overloads
    virtual int MType() const;
    static int classType();
    virtual bool CanRemove( anatomist::AObject* obj );
    virtual bool render( anatomist::GLPrimitives & prim,
                         const anatomist::ViewState & vs );
    virtual void setFileName( const std::string & fname );
    virtual void SetExtrema();
    virtual void adjustPalette();
    virtual Point3df VoxelSize();
    bool Is2DObject();
    bool textured2D();
    bool Is3DObject();
    virtual bool isTransparent() const;
    float MinX2D() const;
    float MinY2D() const;
    float MinZ2D() const;
    float MaxX2D() const;
    float MaxY2D() const;
    float MaxZ2D() const;
    float MinT() const;
    float MaxT() const;
    virtual bool boundingBox( Point3df & bmin, Point3df & bmax ) const;

    // virtual void update( const anatomist::Observable *observable, void *arg );
  };

};

