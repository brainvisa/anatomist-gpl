
namespace anatomist
{

class Module
{
%TypeHeaderCode
#include <anatomist/application/module.h>
%End

public:
  Module();
  virtual ~Module();

  virtual std::string name() const =0;
  virtual std::string description() const =0;
  virtual Tree *controlWinOptions() const;
  void init();

protected:
  virtual void objectsDeclaration();
  virtual void objectPropertiesDeclaration();
  virtual void viewsDeclaration();
  virtual void actionsDeclaration();
  virtual void controlsDeclaration();
  virtual void controlGroupsDeclaration();

private:
  Module( const anatomist::Module & );
};


class ModuleManager
{
%TypeHeaderCode
#include <anatomist/application/module.h>
%End

public:
  static anatomist::ModuleManager *instance();
  ~ModuleManager();

  unsigned size() const;

  SIP_PYTUPLE modules();
%MethodCode
  unsigned	i;
  PyObject	*l = PyTuple_New( sipCpp->size() );
  anatomist::ModuleManager::const_iterator it, e = sipCpp->end();

  for( i=0, it=sipCpp->begin(); it!=e; ++i, ++it )
    PyTuple_SET_ITEM( l, i,
                      sipConvertFromInstance( *it, 
                                              sipClass_anatomist_Module, 0 ) );
  sipRes = l;
%End

protected:
  void insert( anatomist::Module * /Transfer/ );
  void remove( anatomist::Module * /TransferBack/ );

private:
  ModuleManager();
};

};

