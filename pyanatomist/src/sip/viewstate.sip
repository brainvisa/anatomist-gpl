
namespace anatomist
{

class ViewState
{
%TypeHeaderCode
#include <anatomist/window/viewstate.h>
%End

%ConvertToSubClassCode
  sipType = sipType_anatomist_ViewState;
  *sipCppRet = sipCpp;
  if( dynamic_cast<anatomist::SliceViewState *>( sipCpp ) )
  {
    *sipCppRet = dynamic_cast<anatomist::SliceViewState *>( sipCpp );
      sipType = sipType_anatomist_SliceViewState;
  }
%End

public:
  ViewState( float t = 0, anatomist::AWindow * = 0 );
  ViewState( const vector_FLOAT & timedims, anatomist::AWindow * = 0 );
  virtual ~ViewState();

  virtual anatomist::SliceViewState *sliceVS();

  vector_FLOAT       timedims;
  anatomist::AWindow *window;
};


class SliceViewState : anatomist::ViewState
{
%TypeHeaderCode
#include <anatomist/window/viewstate.h>
#ifndef PYAIMS_AIMSVECTOR_FLOAT_3_DEFINED
#define PYAIMS_AIMSVECTOR_FLOAT_3_DEFINED
typedef AimsVector<float, 3> AimsVector_FLOAT_3;
#endif
%End

public:
  SliceViewState( float t = 0, bool slicewanted = false,
                  const Point3df & pos = Point3df(),
                  const aims::Quaternion* orient = 0,
                  const anatomist::Referential* wref = 0,
                  const anatomist::Geometry* wgeom = 0,
                  const aims::Quaternion* vorient = 0,
                  anatomist::AWindow * = 0 );
  SliceViewState( const vector_FLOAT & timedims, bool slicewanted = false,
                  const Point3df & pos = Point3df(),
                  const aims::Quaternion* orient = 0,
                  const anatomist::Referential* wref = 0,
                  const anatomist::Geometry* wgeom = 0,
                  const aims::Quaternion* vorient = 0,
                  anatomist::AWindow * = 0 );

  virtual ~SliceViewState();

  virtual anatomist::SliceViewState *sliceVS();

  bool                          wantslice;
  Point3df                position;
  const aims::Quaternion        *orientation;
  const anatomist::Referential  *winref;
  const anatomist::Geometry     *wingeom;
  const aims::Quaternion        *vieworientation;
};

};

