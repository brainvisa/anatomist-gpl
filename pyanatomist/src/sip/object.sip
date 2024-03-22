
namespace anatomist
{

  class AObject : anatomist::Observer, anatomist::Observable
  {
%TypeHeaderCode
#include <anatomist/graph/Graph.h>
#include <anatomist/graph/GraphObject.h>
%End

%TypeCode
#include <anatomist/application/Anatomist.h>
#include <pyanatomist/sipconverthelpers.h>
%End

%ConvertToTypeCode
  return anatomist::sipConvertToTypeCodeFromInternalRep( sipPy,
    sipType_anatomist_AObject, sipTransferObj, sipIsErr, sipCppPtr );
%End

  public:
    enum ObjectType
    {
      VOLUME,
      BUCKET,
      FACET,
      TRIANG, 
      LIST, 
      VECTOR, 
      MAP, 
      SET, 
      GRAPH, 
      GRAPHOBJECT, 
      VOLSURF, 
      MULTISURF, 
      MULTIBUCKET, 
      MULTIVOLUME, 
      FUSION2D, 
      FUSION3D, 
      FASCICLE,
      FASCICLEGRAPH,
      TEXTURE,
      TEXSURFACE, 
      OTHER
    };

    AObject( const std::string & = "" );
    virtual ~AObject();

    std::string name() const;
    std::string fileName() const;
    int type() const;
    int id() const;

    void setName( std::string );
    void setFileName( std::string );
    set_AObjectPtr parents() const;
%MethodCode
    const anatomist::AObject::ParentList & pl = sipCpp->parents();
    sipRes = new std::set<anatomist::AObject *>;
    anatomist::AObject::ParentList::const_iterator i, e = pl.end();
    for( i=pl.begin(); i!=e; ++i )
      sipRes->insert( *i );
%End

    virtual bool Is2DObject() = 0;
    virtual bool Is3DObject() = 0;
    virtual bool isTransparent() const;
    virtual bool renderingIsObserverDependent() const;

    virtual anatomist::GLComponent *glAPI() = 0;

    virtual anatomist::AObject* clone( bool shallow = 0 ) /Factory/;

    void setChanged();
%MethodCode
    // make setChanged() more violent than in the C++ version

    sipCpp->setChanged();
    anatomist::GLComponent	*gc = sipCpp->glAPI();
    if( gc )
      {
        gc->glSetChanged( anatomist::GLComponent::glBODY, true );
        gc->glSetChanged( anatomist::GLComponent::glGEOMETRY, true );
        gc->glSetChanged( anatomist::GLComponent::glMATERIAL, true );
        int i, nt = gc->glNumTextures();
        for( i=0; i<nt; ++i )
          {
            gc->glSetTexImageChanged( true, i );
            gc->glSetTexEnvChanged( true, i );
          }
      }
%End

    virtual void setInternalsChanged();
    virtual void internalUpdate();
    virtual bool render( anatomist::GLPrimitives &, const anatomist::ViewState & );

    void setType(int);
    void SetMaterial(const anatomist::Material &mat);
    virtual void setReferential(anatomist::Referential * /Transfer/);
    anatomist::Referential *getReferential () const;
    anatomist::AObject *referentialInheritance() const;
    virtual void setReferentialInheritance( anatomist::AObject* ao );
    virtual bool boundingBox( vector_FLOAT & /TransferBack/,
      vector_FLOAT & /TransferBack/) const;
    virtual bool boundingBox2D( vector_FLOAT & /TransferBack/,
      vector_FLOAT & /TransferBack/) const;
    virtual vector_FLOAT voxelSize() const;
    virtual void setVoxelSize( const vector_FLOAT & );
    virtual anatomist::AObjectPalette *palette();
    virtual void setPalette( const anatomist::AObjectPalette & palette );
    virtual const anatomist::AObjectPalette *getOrCreatePalette() const;
    virtual void adjustPalette();
    virtual Tree* optionTree() const;
    virtual anatomist::Material & GetMaterial();
    long loadDate() const;
    void setLoadDate( long t );
    bool isCopy() const;
    carto::GenericObject* attributed();
%MethodCode
    anatomist::AttributedAObject* ao
      = dynamic_cast<anatomist::AttributedAObject *>( sipCpp );
    if( ao )
      sipRes = ao->attributed();
    else
      sipRes = 0;
%End

    static std::map<std::string, carto::rc_ptr<anatomist::ObjectMenu> >
      &getObjectMenuMap();
    static rc_ptr_ObjectMenu getObjectMenu(std::string);
    static void setObjectMenu(std::string, rc_ptr_ObjectMenu );
    static std::string objectTypeName( int );
    static int 	registerObjectType (const std::string &);
    static void addObjectMenuRegistration
    ( anatomist::ObjectMenuRegistrerClass * /Transfer/ );
    void setHeaderOptions();
    virtual void storeHeaderOptions();
    virtual carto::Object makeHeaderOptions() const;

    SIP_PYTUPLE boundingbox() const;
%MethodCode
    // std::cout << "boundingbox\n";
    std::vector<float> bmin, bmax;
    if( !sipCpp->boundingBox( bmin, bmax ) )
      sipRes = PyTuple_New( 0 );
    else
    {
      // std::cout << "bmax: " << bmax << std::endl;
      sipRes = PyTuple_New( 2 );
      PyTuple_SetItem( sipRes, 0,
        sipConvertFromType( new vector_FLOAT( bmin ),
          sipType_vector_FLOAT, Py_None ) );
      PyTuple_SetItem( sipRes, 1,
        sipConvertFromType( new vector_FLOAT( bmax ),
          sipType_vector_FLOAT, Py_None ) );
    }
%End
  virtual void   notifyObservers (void *arg=0);
%MethodCode
  // overriden only until ControlWindow is an observer of objects
  sipCpp->notifyObservers( a0 );
  theAnatomist->NotifyObjectChange( sipCpp );
%End

  static anatomist::AObject* fromObject( carto::GenericObject & );
%MethodCode
  try
  {
    sipRes = a0->value<anatomist::AObject *>();
  }
  catch( std::exception & e )
  {
/*    try
    {
      sipRes = a0->value<carto::rc_ptr<anatomist::AObject> >().get();
    }
    catch( ... )
    {*/
      try
      {
        sipRes = a0->value<carto::shared_ptr<anatomist::AObject> >().get();
      }
      catch( ... )
      {
        sipIsErr = 1;
        PyErr_SetString( PyExc_RuntimeError, e.what() );
        sipRes = 0;
      }
//    }
  }
%End

    virtual const anatomist::AObject* nearestVertex(
      const vector_FLOAT & pos, int *vertex, float *distance, float tol = -1,
      int *polygon /In/ = 0, bool tex_only = false, int target_poly = -1 ) const;
%Docstring
        Get the nearest vertex to a given position.

        Only valid for a mesh-based object, otherwise 0 is returned.
        vertex and distance should point to a valid int and float, and will be
        filled with the mesh vertex index, and the distance to this vertex. If
        the object has children objects, the child with the nearest vertex will
        be returned. If tol is >=0, this tolerence threshold is used to filter
        out vertices too far (thus the function may fail and return 0). If
        polygon is given as a valid pointer to an int, the polygon index of the
        "nearest polygon" will also be filled. The nearest polygon will contain
        the nearest vertex, thus a polygon wich center is nearest to the given
        point can be discarded.

        The base implementation will perform an exaustive search, thus is
        costy. Optimized implementations could make use of a kdtree algorithm,
        but this default one does not.

        If the object is also displayed in a 3D window, OpenGL-based functions
        may be more efficient than this one.
%End

    virtual vector_FLOAT texValues( const vector_FLOAT & pos,
                                    const anatomist::Referential* orgRef,
                                    int poly = -1 ) const;
    virtual vector_FLOAT texValues( const vector_FLOAT & pos,
                                    int poly = -1 ) const;
    virtual float mixedTexValue( const vector_FLOAT & pos,
                                 const anatomist::Referential* orgRef,
                                 int poly = -1 ) const;
    virtual float mixedTexValue( const vector_FLOAT & pos,
                                 int poly = -1 ) const;
    virtual rc_ptr_Volume_FLOAT texValuesSeries(
      const vector_FLOAT & pos, int axis, const Referential* orgRef,
      int poly = -1 ) const;
    virtual rc_ptr_Volume_FLOAT texValuesSeries(
      const vector_FLOAT & pos, int axis, int poly = -1 ) const;
    virtual void
    getTextureLabels( const vector_FLOAT & texvalues,
                      vector_STRING & labels,
                      std::string & textype ) const;
    virtual void update( const anatomist::Observable *observable, void *arg );
    virtual std::string toolTip() const;

    virtual std::string objectFullTypeName() const;
    bool save( const std::string & filename, bool onlyIfModified );
    virtual bool save( const std::string & filename );
    bool userModified() const;
%Docstring
    if the object has been modified by user interaction, and needs saving
  %En

    void setUserModified( bool state = true );
%Docstring
    if the object has been modified by user interaction, and needs saving
%End

    bool allowsOverwriteOnSave() const;
    void setAllowsOverwriteOnSave( bool x );
  };

};

