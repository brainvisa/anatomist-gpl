
%ModuleCode
#if SIP_VERSION >= 0x040700
#include <anatomist/object/sliceable.h>
#endif
%End


namespace anatomist
{

class Sliceable : anatomist::GLComponent /Abstract/
{
%TypeHeaderCode
#include <anatomist/object/sliceable.h>
%End

public:
  Sliceable();
  virtual ~Sliceable();
  virtual rc_ptr_Volume_RGBA rgbaVolume( const anatomist::SliceViewState* = 0,
      int tex = 0 ) const;
  virtual void rgbaVolume( Volume_RGBA &, const anatomist::SliceViewState* = 0,
      int tex = 0 ) const;
};



class SliceableObject : anatomist::AObject, anatomist::Sliceable /Abstract/
{
%TypeHeaderCode
#include <anatomist/object/sliceable.h>
%End

public:
  SliceableObject();
  virtual ~SliceableObject();
};


class SelfSliceable
{
%TypeHeaderCode
#include <anatomist/object/selfsliceable.h>
%End

public:
  SelfSliceable();
  SelfSliceable( const Point3df & pos, const aims::Quaternion & quat );
  virtual ~SelfSliceable();

  void setOffset( const Point3df & pos );
  void setQuaternion( const aims::Quaternion & quat );
  void setSlice( const Point3df & pos, const aims::Quaternion & quat );
  aims::Quaternion quaternion() const;
  Point3df offset() const;
  void setPlane( const Point4df & plane );
  Point4df plane() const;
  void invertSlice();

  virtual void sliceChanged();

  virtual void setOffsetSilent( const Point3df & pos );
  virtual void setQuaternionSilent( const aims::Quaternion & quat );
  virtual void setSliceSilent( const Point3df & pos,
                               const aims::Quaternion & quat );
  void setPlaneSilent( const Point4df & plane );
};


class ClippedObject : anatomist::MObject, anatomist::SelfSliceable
{
%TypeHeaderCode
#include <anatomist/object/clippedobject.h>
%End

public:
  ClippedObject( const vector_AObjectPtr & );
  virtual ~ClippedObject();
};

};
