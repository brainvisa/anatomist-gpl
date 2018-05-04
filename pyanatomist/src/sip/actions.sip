
namespace anatomist
{

  class LabelEditAction : anatomist::Action
  {
%TypeHeaderCode
#include <anatomist/window3D/labeleditaction.h>
%End

  public:
    LabelEditAction();
    LabelEditAction( const anatomist::LabelEditAction & a );
    virtual ~LabelEditAction();

    virtual std::string name() const;

    void pick();
%Docstring
    pick selection label
%End

    void edit();
%Docstring
    set current (picked) label to seleted objects
%End

    std::string label() const;
%Docstring
    current label
%End

    void setLabel( const std::string & l, const anatomist::AObject* obj = 0 );
%Docstring
    setLabel(label, obj=None)
    setLabel(label, color)

    set (picked) current label. obj is used to find a nomenclature and color

    Parameters
    ----------
    label: str
        label name
    obj: AObject
        used to find a nomenclature and color
    color: aims.AimsRGB
        color associated to the label, outside any nomenclature context
%End
    void setLabel( const std::string & l, const AimsRGB & color );

    QWidget* actionView( QWidget* );
    bool viewableAction() const;
  };

};
