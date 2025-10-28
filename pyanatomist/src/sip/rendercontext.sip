
namespace anatomist
{
  class RenderContext
  {
  %TypeHeaderCode
  #include <anatomist/window3D/renderContext.h>
  %End

    public:
      RenderContext(AWindow3D* win, anatomist::GLWidgetManager* widgetManager);
      ~RenderContext();
      //rc_ptr_anatomist::PrimList renderObjects( const std::list<carto::shared_ptr<anatomist::AObject>> & objs);
  };
};

