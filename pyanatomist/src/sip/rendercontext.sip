
class RenderContext
{
%TypeHeaderCode
#include <anatomist/window3D/renderContext.h>
%End

  public:
    RenderContext(AWindow3D* win, anatomist::GLWidgetManager* widgetManager);
    ~RenderContext();
    // std::shared_ptr<anatomist::PrimList> renderObjects( const std::list<carto::shared_ptr<anatomist::AObject>> & objs);
};

