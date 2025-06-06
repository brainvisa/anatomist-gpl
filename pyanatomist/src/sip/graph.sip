
%ModuleCode
#if SIP_VERSION >= 0x040700
#include <anatomist/graph/Graph.h>
#endif
%End

namespace anatomist
{

class PythonAObject /PyName=AttributedAObject/
{
%TypeHeaderCode
#include <anatomist/graph/pythonAObject.h>
%End

public:
  ~PythonAObject();
  virtual carto::GenericObject * attributed()=0;
private:
  PythonAObject();
};


class AGraphObject : anatomist::MObject, anatomist::PythonAObject
{
%TypeHeaderCode
#include <anatomist/graph/GraphObject.h>
#include <pyaims/vector/vector.h>
#include <pyanatomist/refglitem.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipanatomistAIterator.h"
#endif
%End

public:
  AGraphObject (carto::GenericObject *);
  virtual	~AGraphObject ();
};


class AGraph : anatomist::MObject, anatomist::GLComponent,
  anatomist::PythonAObject
{
%TypeHeaderCode
#include <anatomist/graph/Graph.h>
#include <anatomist/mobject/MObject.h>
#include <pyaims/vector/vector.h>
#include <anatomist/surface/glcomponent.h>
#include <pyanatomist/refglitem.h>
%End

public:
  enum ColorMode
  {
    Normal, PropertyMap,
  };

  AGraph( Graph * /Transfer/, const char *, bool,
          const Point3dl & );
  AGraph( Graph * /Transfer/, const char *, bool=true,
          const Point3dl &=Point3dl(64, 64, 64) );
  virtual ~AGraph();

  Graph	*graph () const;

  ColorMode colorMode() const;
  void setColorMode( ColorMode );
  std::string colorProperty() const;
  void setColorProperty( const std::string & );
  void updateColors();
  void loadSubObjects( int mask );
  void updateAfterAimsChange();
  void setLabelsVolumeDimension( const Point3d & vd );
  void setLabelsVolumeDimension( const Point3dl & vd );
  Point3dl labelsVolumeDimension() const;
  set_STRING mappableVertexProperties() const;
  set_STRING mappableEdgeProperties() const;
  std::string labelProperty( bool allowDefault = true ) const;
  void setLabelProperty( const std::string & prop );
};

};

