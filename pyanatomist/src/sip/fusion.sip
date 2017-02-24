
%ModuleCode
#if SIP_VERSION >= 0x040700
#include <anatomist/fusion/defFusionMethods.h>
#include <anatomist/surface/fusiontexsurf.h>
#endif
%End

namespace anatomist
{

class FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End

%ConvertToSubClassCode
	if (dynamic_cast<anatomist::Fusion2dMethod *>(sipCpp))
		sipClass = sipClass_anatomist_Fusion2dMethod;
	else if (dynamic_cast<anatomist::Fusion3dMethod *>(sipCpp))
		sipClass = sipClass_anatomist_Fusion3dMethod;
	else if (dynamic_cast<anatomist::FusionCutMeshMethod *>(sipCpp))
		sipClass = sipClass_anatomist_FusionCutMeshMethod;
	else if (dynamic_cast<anatomist::FusionMultiTextureMethod *>(sipCpp))
		sipClass = sipClass_anatomist_FusionMultiTextureMethod;
	else if (dynamic_cast<anatomist::FusionSliceMethod *>(sipCpp))
		sipClass = sipClass_anatomist_FusionSliceMethod;
	else if (dynamic_cast<anatomist::FusionTexSurfMethod *>(sipCpp))
		sipClass = sipClass_anatomist_FusionTexSurfMethod;
	else if (dynamic_cast<anatomist::FusionTextureMethod *>(sipCpp))
		sipClass = sipClass_anatomist_FusionTextureMethod;
	else if (dynamic_cast<anatomist::PlanarFusion3dMethod *>(sipCpp))
		sipClass = sipClass_anatomist_PlanarFusion3dMethod;
	else if (dynamic_cast<anatomist::Fusion2DMeshMethod *>(sipCpp))
		sipClass = sipClass_anatomist_Fusion2DMeshMethod;
  	else	sipClass = 0;
%End

public:
	FusionMethod();
	virtual ~FusionMethod();

	virtual int canFusion(const set_AObjectPtr &) = 0;
	virtual anatomist::AObject *fusion(const vector_AObjectPtr &) = 0 /Factory/;

	virtual std::string ID() const = 0;
	virtual bool orderingMatters() const;
	virtual std::string generatedObjectType() const = 0 /AutoGen/;
};

class Fusion2dMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	Fusion2dMethod();
	virtual ~Fusion2dMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class Fusion3dMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	Fusion3dMethod();
	virtual ~Fusion3dMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class FusionCutMeshMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	FusionCutMeshMethod();
	virtual ~FusionCutMeshMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class FusionMultiTextureMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	FusionMultiTextureMethod();
	virtual ~FusionMultiTextureMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class FusionSliceMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	FusionSliceMethod();
	virtual ~FusionSliceMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class FusionTexSurfMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/surface/fusiontexsurf.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	FusionTexSurfMethod();
	virtual ~FusionTexSurfMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class FusionTextureMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	FusionTextureMethod();
	virtual ~FusionTextureMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class PlanarFusion3dMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	PlanarFusion3dMethod();
	virtual ~PlanarFusion3dMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class Fusion2DMeshMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	Fusion2DMeshMethod();
	virtual ~Fusion2DMeshMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

/* //FIXME : à deplacer dans un/des plugin(s)
class AInterpolerMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/interpoler/interpolMethod.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	AInterpolerMethod();
	virtual ~AInterpolerMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};


class PlaneFusionMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	PlaneFusionMethod();
	virtual ~PlaneFusionMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class CylinderFusionMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	CylinderFusionMethod();
	virtual ~CylinderFusionMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};

class ASurfMatchMethod : anatomist::FusionMethod
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#include <anatomist/fusion/defFusionMethods.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#include "sipanatomistsipset_AObjectPtr.h"
#endif
%End
	public:
	ASurfMatchMethod();
	virtual ~ASurfMatchMethod();
        virtual int canFusion(const set_AObjectPtr &);
        virtual anatomist::AObject *fusion(const vector_AObjectPtr &) /Factory/;
        virtual std::string ID() const = 0;
};
*/

class FusionFactory
{
%TypeHeaderCode
#include <anatomist/fusion/fusionFactory.h>
#if SIP_VERSION < 0x040700
#include "sipanatomistsipvector_AObjectPtr.h"
#endif
%End

public:
  FusionFactory();
  virtual ~FusionFactory();

  virtual anatomist::FusionMethod *chooseMethod(vector_AObjectPtr &, bool=false);
  virtual anatomist::FusionMethod *method(const std::string&) const;
  list_STRING allowedMethods( const set_AObjectPtr & ) const;
%MethodCode
  std::multimap<int, std::string> am = sipCpp->allowedMethods( *a0 );
  sipRes = new std::list<std::string>;
  std::multimap<int, std::string>::const_reverse_iterator i, e = am.rend();
  for( i=am.rbegin(); i!=e; ++i )
    sipRes->push_back( i->second );
%End

  static anatomist::FusionFactory *factory();
  static bool registerMethod(anatomist::FusionMethod * /Transfer/);
  static bool canFusion(const set_AObjectPtr &);
  static set_STRING methods() const;
};



};

