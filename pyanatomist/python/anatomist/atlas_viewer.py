#! /usr/bin/python
# -*- coding: utf-8 -*-
# -*- coding:Latin-1 -*- #
"""
"""

import sys
import json
import gc #use in "SelectionAtlasAction"
import re
import os

from PyQt4.QtGui import QLineEdit, QPushButton, QMainWindow, QApplication
from PyQt4.QtGui import QWidget, QLabel, QVBoxLayout, QToolBar, QIcon
from PyQt4.QtGui import QHBoxLayout, QDockWidget, QErrorMessage, QAction
from PyQt4.QtGui import QDesktopWidget,QTreeWidget, QTreeWidgetItem, QMenu
from PyQt4.QtGui import QFileDialog, QTreeWidgetItemIterator,QAbstractItemView
from PyQt4.QtCore import Qt, SIGNAL, QT_TRANSLATE_NOOP, QThread
try:
  from PyQt4.QtCore import QString
  _use_qstring = True
except ImportError:
  _use_qstring = False

from anatomist import cpp
import anatomist.direct.api as anatomist
from soma import aims

#To do ==> making accessor : self.tree.leaves_sorted
#      ==> accessor ?? : self.clust_dict
class AtlasJsonRois(QMainWindow):
  """This class is the graphical interface inherited from QMainWindow
  """

  def __init__(self, arg_roi_path, t1mri_vol_path=None, json_roi_path=None,
        nomenclature_path=None):
    """
    """
    QMainWindow.__init__(self)
    self.setGeometry(0, 0, 750, 500 )
    self.setWindowTitle("Atlas viewer")
    self.centerOnScreen()
    #*********# Start Anatomist #********
    a = anatomist.Anatomist('-b')
    ad = anatomist.cpp.ActionDictionary.instance()
    ad.addAction( 'SelectionAtlasAction', SelectionAtlasAction )
    cd = anatomist.cpp.ControlDictionary.instance()
    cd.addControl( 'SelectionAtlasControl', SelectionAtlasControl, 2 )
    cm = anatomist.cpp.ControlManager.instance()
    cm.addControl( 'QAGLWidget3D', '', 'SelectionAtlasControl' )
    #*****# Definition of windows #**********
    self.viewer_widget = QWidget()
    self.setCentralWidget(self.viewer_widget)

    # MRI anatomist wiever
    self.window_anat_viewer = a.createWindow('3D', no_decoration=True)
    self.window_anat_viewer.setControl('SelectionAtlasControl')
    self.window_anat_viewer.setParent(self.viewer_widget)
    w_anat_viewer_layout = QVBoxLayout( self.viewer_widget )
    w_anat_viewer_layout.addWidget( self.window_anat_viewer.getInternalRep() )

    dock = QDockWidget()
    self.addDockWidget(Qt.RightDockWidgetArea, dock)
    tool_window = QWidget()		
    dock.setWidget(tool_window)
    
    toolbar = QToolBar('View toolbar')
    icondir = os.path.expandvars( os.path.join( \
      aims.carto.Paths.globalShared(), 'anatomist-%s' % '.'.join( \
       [ str(x) for x in aims.version() ] ), 'icons', 'atlas_viewer' ) )
    self.open_json = QAction(QIcon(os.path.join(icondir,'Open_icon.png')), 'open JSON', self)
    toolbar.addAction(self.open_json)
    self.save_json = QAction(QIcon(os.path.join(icondir,'Save_icon.png')), 'save JSON', self)
    toolbar.addAction(self.save_json)
    self.all_brain = QAction(QIcon(os.path.join(icondir,'brain.png')), 'reset selection brain', self)
    toolbar.addAction(self.all_brain)
    self.right_brain = QAction(QIcon(os.path.join(icondir,'left_brain.png')), 'select right brain', self)
    toolbar.addAction(self.right_brain)
    self.left_brain = QAction(QIcon(os.path.join(icondir,'right_brain.png')), 'select left brain', self)
    toolbar.addAction(self.left_brain)
    self.central_struct = QAction(QIcon(os.path.join(icondir,'central_struct.png')), 'select central struct', self)
    toolbar.addAction(self.central_struct)
    self.t1mri_view = QAction(QIcon(os.path.join(icondir,'t1mri.png')), 'select t1mri view', self)
    toolbar.addAction( self.t1mri_view )
    self.menu_file = QMenu( "t1mri_view")
    self.t1mri_axial_view = QAction( 'select axial t1mri view', self)
    self.t1mri_sagittal_view = QAction( 'select sagittal t1mri view', self)
    self.t1mri_coronal_view = QAction( 'select coronal t1mri view', self)
    self.dimension = QAction( 'change 2D / 3D', self)
    self.menu_file.addAction(self.t1mri_axial_view)
    self.menu_file.addAction(self.t1mri_sagittal_view)
    self.menu_file.addAction(self.t1mri_coronal_view)
    self.menu_file.addAction(self.dimension)
    self.t1mri_view.setMenu(self.menu_file)
    self.outline = QAction( QIcon(os.path.join(icondir,'roi_contour.png')), 'Display outline of selected rois', self )
    toolbar.addAction(self.outline)
    self.convention = QAction( QIcon(os.path.join(icondir,'convention_brain_2.png')), 'change convention display', self )
    toolbar.addAction(self.convention)

    # load data and nomenclature
    graph = aims.read( arg_roi_path )

    if nomenclature_path is not None:
      nomenclature = aims.read(nomenclature_path)

    json_dict = {}
    if json_roi_path is not None:
      json_file = open(json_roi_path)
      json_dict = json.load(json_file), None
      del json_file

    # Tool window
    self.tree = TreeRois(json_dict, nomenclature)
    self.tree_widget = self.tree.getWidget()
    self.tree_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

    name_group_label = QLabel()
    name_group_label.setText("New group name :")
    self.name_group = QLineEdit()
    group_layout = QHBoxLayout()
    group_layout.addWidget(name_group_label)
    group_layout.addWidget(self.name_group)
    create_group = QPushButton()
    create_group.setText("Create group")
    tool_window_layout = QVBoxLayout()
    tool_window_layout.addWidget(toolbar)
    tool_window_layout.addWidget(self.tree_widget)
    tool_window_layout.addWidget(name_group_label)
    tool_window_layout.addLayout(group_layout)
    tool_window_layout.addWidget(create_group)
    tool_window.setLayout(tool_window_layout)

    #display atlas in Axial anatomist window
    self.nomenclature = None
    if self.tree.nomenclature is not None:
      self.nomenclature = a.toAObject( self.tree.nomenclature )
    self.ana_graph = a.toAObject(graph)
    self.window_anat_viewer.addObjects( self.ana_graph, add_graph_nodes=True)
    if t1mri_vol_path is not None:
      t1mri = aims.read( t1mri_vol_path )
      self.t1mri_anat_vol = a.toAObject(t1mri)
      self.window_anat_viewer.addObjects(self.t1mri_anat_vol)
      self.statusBar().showMessage("Display convention : Radiological")
    else:
      self.t1mri_anat_vol = None

    if not self.nomenclature:
      self.ana_graph.setColorMode( self.ana_graph.PropertyMap )
      self.ana_graph.setColorProperty( 'name' )
      self.ana_graph.setPalette( a.getPalette( "random" ) )
      self.ana_graph.notifyObservers()

    self.window_anat_viewer.show()
    #******************************************
    #save cluster in Python dictionary
    graphs = self.window_anat_viewer.objects
    self.clust_dict = {}
    for n in graphs:
      #self.t1mri_anat_vol must be managed otherwise
      if n != self.t1mri_anat_vol:
        name = n.name.split()
        name = name[0]
        if name in self.clust_dict:
          self.clust_dict[name].append(n)
        else:
          self.clust_dict[name] = [n]
    #******************************************
    self.tree_widget.itemChanged.connect(self.tree.updateSelection)
    create_group.clicked.connect(self.validateGroup)
    
    self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
    self.tree_widget.customContextMenuRequested.connect(self.tree.removeAction)

    #self.tree_widget.itemPressed.connect(self.tree.removeNode)
    self.tree_widget.itemClicked.connect(self.updateViewWithTree)
    self.connect(self.save_json, SIGNAL('triggered()'), self.saveTree)
    self.connect(self.open_json, SIGNAL('triggered()'), self.loadTree)
    self.connect(self.all_brain, SIGNAL('triggered()'), self.resetBrain) 
    self.connect(self.right_brain, SIGNAL('triggered()'), self.selectRightBrain)    
    self.connect(self.left_brain, SIGNAL('triggered()'), self.selectLeftBrain)
    self.connect(self.central_struct, SIGNAL('triggered()'), self.selectCentralStruct)
    self.connect( self.t1mri_view, SIGNAL('triggered()'), self.selectT1MRIView)
    self.connect( self.dimension, SIGNAL('triggered()'), self.changeDimension)
    self.connect( self.convention, SIGNAL('triggered()'), self.changeConvention)
    self.connect( self.outline, SIGNAL('triggered()'), self.ViewOutline)
#--------------******************-------------***************------
    self.connect( self.t1mri_axial_view, SIGNAL('triggered()'), self.muteAxial)
    self.connect( self.t1mri_sagittal_view, SIGNAL('triggered()'), self.muteSagittal)
    self.connect( self.t1mri_coronal_view, SIGNAL('triggered()'), self.muteCoronal)
#--------------******************-------------***************------
  def ViewOutline(self):
    """This method is to replace mesh(es) by it(their) outline(s) in the viewer """
    a = anatomist.Anatomist('-b')
    if self.window_anat_viewer.windowType == "3D":
      self.window_anat_viewer.muteAxial()
    selected_items = self.tree_widget.selectedItems()
    try:
      a.removeObjects(objects=self.outline_object_list,windows=[self.window_anat_viewer],remove_children=True)
      a.deleteObjects( self.outline_object_list )
      self.outline_object_list = []
    except AttributeError:
      self.outline_object_list = []
    for item in selected_items:
      for cluster in self.clust_dict[str(item.text(1))]:
        for b in cluster.children:
          if b.objectType == 'SURFACE':
            c = a.duplicateObject(b)
            outline_object = a.fusionObjects( [ c ], "Fusion2DMeshMethod")
            self.outline_object_list.append( outline_object )

      d = self.clust_dict[str(item.text(1))][0].material.diffuse
      diffuse = [d[0], d[1], d[2], 0]
      #setMaterial is only used to modify the opacity and ghost parameters
      #WARNING : Penser à remettre une transparence normale pour les autres (anciennement mis à 0 par ce biais)
      a.execute( 'SetMaterial', objects = self.clust_dict[str(item.text(1))],\
                                         diffuse = diffuse,\
                                         ghost = 1,\
                                         refresh = 1 )  
    for graph in self.outline_object_list:
      self.window_anat_viewer.addObjects(graph, add_graph_nodes=True)
#--------------******************-------------***************------  
  def changeConvention(self):
    """This method aims is to change the display convention (Radiological/Neurological) """
    a = anatomist.Anatomist('-b')
    if 'axialConvention' in a.config().keys():
      del a.config()[ 'axialConvention' ]
      self.statusBar().showMessage("Display convention : Radiological")
    else:
      a.config()[ 'axialConvention' ] = 'neuro'
      self.statusBar().showMessage("Display convention : Neurological")
    self.muteAxial()
#--------------******************-------------***************------   
  def changeDimension(self):
    windowType = self.window_anat_viewer.windowType
    if windowType == "3D":
      self.window_anat_viewer.muteAxial()
    else:
      self.window_anat_viewer.mute3D()
  def muteAxial(self):
    #if the windowType is 3D we have to mute again after the orientation changed
    windowType = self.window_anat_viewer.windowType
    """Mute the t1mri orientation to Axial """
    self.window_anat_viewer.muteAxial()
    if windowType == "3D":
      self.window_anat_viewer.mute3D()
    
  def muteSagittal(self):
    #if the windowType is 3D we have to mute again after the orientation changed
    windowType = self.window_anat_viewer.windowType
    """Mute the t1mri orientation to Sagittal """
    self.window_anat_viewer.muteSagittal() 
    if windowType == "3D":
      self.window_anat_viewer.mute3D()
    
  def muteCoronal(self):
    #if the windowType is 3D we have to mute again after the orientation changed
    windowType = self.window_anat_viewer.windowType
    """Mute the t1mri orientation to Coronal"""
    self.window_anat_viewer.muteCoronal()
    if windowType == "3D":
      self.window_anat_viewer.mute3D()
#--------------******************-------------***************------
  def resetBrain( self ):
    """Reset the selections in QTree and AWindow"""
    for l in self.tree.getLeaves()[2]:
      l.setCheckState(0,Qt.Checked)
    for s in self.tree_widget.selectedItems():
      s.setSelected(False)
    self.updateViewWithTree()
    #WARNING this method is normally temporary
    a = anatomist.Anatomist('-b')
    try:
      a.removeObjects(objects=self.outline_object_list,windows=[self.window_anat_viewer],remove_children=True)
      a.deleteObjects( self.outline_object_list )
    except AttributeError:
      pass
  def selectRightBrain(self):
    """Select automatically ROIs which identify on the right side """
    selected_items = self.tree_widget.selectedItems()
    for s in selected_items:
      s.setSelected(False)
    self.tree.selectRightBrain()
    if len(set(self.tree_widget.selectedItems()).intersection(set(selected_items))) == len(self.tree_widget.selectedItems()) and\
        len(selected_items) != 0:
      self.tree.checkRightBrain()
    self.updateViewWithTree()

  def selectLeftBrain(self):
    """Select automatically ROIs which identify on the left side """
    selected_items = self.tree_widget.selectedItems()
    for s in selected_items:
      s.setSelected(False)
    self.tree.selectLeftBrain()
    if len(set(self.tree_widget.selectedItems()).intersection(set(selected_items))) == len(self.tree_widget.selectedItems()) and\
        len(selected_items) != 0:
      self.tree.checkLeftBrain()
    self.updateViewWithTree()
    
  def selectCentralStruct(self):
    """Select automatically ROIs which identify as central """
    selected_items = self.tree_widget.selectedItems()
    for s in selected_items:
      s.setSelected(False)
    self.tree.selectCentralStruct()
    if len(set(self.tree_widget.selectedItems()).intersection(set(selected_items))) == len(self.tree_widget.selectedItems()) and\
        len(selected_items) != 0:
      self.tree.checkCentralStruct()
    self.updateViewWithTree()

  def selectT1MRIView(self):
    """Display or remove the t1mri on the view """
    if self.t1mri_anat_vol is not None:
      if self.t1mri_anat_vol in self.window_anat_viewer.objects:
        self.window_anat_viewer.removeObjects(self.t1mri_anat_vol)
      else:
        self.window_anat_viewer.addObjects(self.t1mri_anat_vol)

  def getGravityCenter( self, aobject ):
      if 'gravity_center' in aobject.attributed():
        gravity_center_position = aobject.attributed()['gravity_center']
      else:
        bbox = aobject.boundingbox()
        gravity_center_position = bbox[1] - bbox[0]
      return gravity_center_position

  def selectionChanged( self ):
    """This method aims is to synchronize selection in the window with QTree selection """
    a = anatomist.Anatomist('-b')
    brain_item = (self.tree_widget.findItems("brain", Qt.MatchExactly))[0]
    self.tree.reduceAllItem(brain_item, root=True)
    if self.tree_widget.findItems("customized group", Qt.MatchExactly):
      group_item = (self.tree_widget.findItems("customized group", Qt.MatchExactly))[0]
      self.tree.reduceAllItem(group_item, root=True)
    #We remove the old selection
    items_selected = self.tree_widget.selectedItems()
    for i in items_selected:
      i.setSelected(False)
    #We update the selection with the window selection  
    g=a.getDefaultWindowsGroup()
    select_obj = g.getSelection()
    for i in select_obj:
      name = i.name.split()[0]
      #t1mri hasn't field : 'gravity_center'
      gravity_center_position = self.getGravityCenter( i )
      self.window_anat_viewer.camera(cursor_position=gravity_center_position)
      leaves_list = self.tree.getLeaves()
      leaves = leaves_list[2]
      for l in leaves:
        if str(l.text(1))==name:
          l.setSelected(True)
          self.tree.expandHierarchy(l)


  def updateViewWithTree(self, item=None ):
    a = anatomist.Anatomist('-b')
    #We have to distinguish if the action is about checking or simple selection
    if item is not None:
      if item in self.tree.memory_checked_dict.keys():
        if item.checkState(0) != self.tree.memory_checked_dict[ item ]:
          self.tree.createMemoryCheckedDict() 
          #the item's checkstate has changed
          if item.checkState(0)==0:
            self.tree.uncheckDescendant(item)
          self.tree.updateSelection(item)

    items = self.tree_widget.selectedItems()
    toggle_clust_dict = self.clust_dict.copy()
    clust_list=[]
    if len(items) != 1:
      for n in items:
        select_list = self.multipleOrSingleSelection( n, toggle_clust_dict, clust_list )
        clust_list = select_list[0]
        toggle_clust_dict = select_list[1]
    else:
      select_list = self.multipleOrSingleSelection( item, toggle_clust_dict, clust_list )
      clust_list = select_list[0]
      gravity_center_position = None
      if len( clust_list ) != 0:#check if clust_list is empty
        gravity_center_position = self.getGravityCenter( clust_list[0] )
        self.window_anat_viewer.camera(cursor_position=gravity_center_position)
      toggle_clust_dict = select_list[1]
    #"="Apply the colors of nodes
    if not self.nomenclature:
      self.ana_graph.setColorMode( self.ana_graph.PropertyMap )
      self.ana_graph.setColorProperty( 'name' )
      self.ana_graph.setPalette(a.getPalette("random"))
      self.ana_graph.notifyObservers()
    a.sync()
    #"="
    for g in clust_list:
      #it is possible that several graph correspond of unique ROI but disjunct
      objects = []
      if isinstance(g,list):
        d = g[0].material.diffuse
        objects.extend(g)
      else:
        d = g.material.diffuse
        objects.append(g)
      diffuse = [d[0], d[1], d[2], 1]
      #setMaterial is only used to modify the opacity and ghost parameters
      a.execute( 'SetMaterial', objects = objects,\
                                      diffuse = diffuse,\
                                      ghost = 0,\
                                      refresh = 1 )
    
    for g in toggle_clust_dict.values():
      objects = []
      if isinstance(g,list):
        d = g[0].material.diffuse
        objects.extend(g)
      else:
        d = g.material.diffuse
        objects.append(g)
      diffuse = [d[0], d[1], d[2], 0.3]
      #setMaterial is only used to modify the opacity and ghost parameters
      a.execute( 'SetMaterial', objects = objects,\
                                         diffuse = diffuse,\
                                         ghost = 0,\
                                         refresh = 1 )
    state_list = self.tree.getLeaves()
    unchecked_graphs_list = []
    for n in state_list[0]:
      item = self.clust_dict.get(str(n.text(1)))
      if item is not None:
        unchecked_graphs_list.extend(item)
    for g in unchecked_graphs_list:
      objects = []
      if isinstance(g,list):
        d = g[0].material.diffuse
        objects.extend(g)
      else:
        d = g.material.diffuse
        objects.append(g)
      diffuse = [d[0], d[1], d[2], 0]
      #setMaterial is only used to modify the opacity and ghost parameters
      a.execute( 'SetMaterial', objects=objects,\
                                        diffuse = diffuse,\
                                        ghost=1,\
                                        refresh = 1 )
                                        
    group = self.window_anat_viewer.group
    group.setSelection(clust_list) 
    
    #for obj in self.window_anat_viewer.objects:
    #  obj.setChanged()
#______________________________________________________________________________

  def multipleOrSingleSelection( self, item, toggle_clust_dict, clust_list):
    """This method is used to allow the multiple selection  """
    g = self.window_anat_viewer.group
    if item is not None and item.text(1):
      if item.checkState(0)==2:
        #??Why it's not already the case?
        if str(item.text(1)) in self.clust_dict.keys():
          clust_list.extend(self.clust_dict[str(item.text(1))])
        #??Why it's not already the case?
          if str(item.text(1)) in toggle_clust_dict.keys():
            del toggle_clust_dict[str(item.text(1))]
    else:
	
      leafChecked = self.tree.getLeavesChecked(item, [])
      for n in leafChecked:
        if n.childCount():
          for r in range(n.childCount()):
            #It necessary if the JSON data contains bad label values
            if str(n.child(r).text(1)) in self.clust_dict.keys():
              clust_list.extend(self.clust_dict[str(n.child(r).text(1))])
              if str(n.child(r).text(1)) in toggle_clust_dict:
                del toggle_clust_dict[str(n.child(r).text(1))]
        else:
          
            #It necessary if the JSON data contains bad label values
            if str(n.text(1)) in self.clust_dict.keys():
              clust_list.extend(self.clust_dict[str(n.text(1))])
              if str(n.text(1)) in toggle_clust_dict.keys():
                del toggle_clust_dict[str(n.text(1))]
    return [ clust_list, toggle_clust_dict ]
#______________________________________________________________________________
  def loadTree(self):
    filename = QFileDialog.getOpenFileName(self,\
    'Choose roi file','', "ROI file (*.roi)")
    self.tree.json_full_data = self.tree.createJSONData(filename)
    self.tree.updateTree(self.tree.json_full_data)
    #Update the leaves after the new roi file
    self.tree.leaves_sorted = self.tree.sortLeavesBySide()
    self.tree.createMemoryCheckedDict()

#______________________________________________________________________________
  def saveTree(self):
    self.tree.saveInJson(self)
#______________________________________________________________________________
  def validateGroup(self):
    #self.tree.createGroupWithNodeChecked(self.name_group.text())
    self.tree.createGroupWithNodeSelected(self.name_group.text())
    self.tree.leaves_sorted = self.tree.sortLeavesBySide()
#______________________________________________________________________________
  def centerOnScreen(self):
    '''centerOnScreen()
	centers the window on the screen.'''
    resolution = QDesktopWidget().screenGeometry()
    self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class TreeRois:
  
  def __init__(self, json_dict, nomenclature=None):
    # Initialization of Tree creation
    self.tree_widget = QTreeWidget()
    self.tree_widget.setColumnCount(2)
    self.tree_widget.headerItem().setText(0, "Labels name")
    self.tree_widget.headerItem().setText(1, "Labels value")
    self.json_full_data, self.nomenclature \
      = self.createJSONData(json_dict, nomenclature)
    self.updateTree(self.json_full_data)
    self.leaves_sorted = self.sortLeavesBySide()
    self.createMemoryCheckedDict()

  @staticmethod
  def treeToDict(nomenclature):
    roi_dict = {}
    children = [(child, roi_dict) for child in nomenclature.children()]
    while children:
      child, layer = children.pop(0)
      if child.childrenSize() == 0: # terminal element
        clist = layer.setdefault(child['name'], [])
        clist.append(child['name'])
      else:
        clist = layer.setdefault(child['name'], {})
        clist[child['name']] = [child['name']] # make it also a leaf
        children += [(c, clist) for c in child.children()]
    return roi_dict

  def createJSONData(self, json_dict, nomenclature):
    if nomenclature is not None:
      nom_dict = self.treeToDict(nomenclature)
      json_dict2 = {}
      if json_dict:
        json_dict2.update(json_dict)
      json_dict2['brain'] = nom_dict
      return json_dict2, nomenclature
    return json_dict, None
    #json_file = open(json_path)
    #return json.load(json_file), None
#______________________________________________________________________________  
  def getWidget(self):
    return self.tree_widget
#______________________________________________________________________________
  def updateTree(self, json_data, p=None):
    #we remove the old Tree
    if p is None:
      for n in range(self.tree_widget.topLevelItemCount()):
        #the index is already '0' because when the first is taken the second become the first...
        TopLevelItem = self.tree_widget.takeTopLevelItem(0)
        del TopLevelItem
        #The following method doesn't work but I don't know why
        #root = self.tree_widget.topLevelItem(n)
        #self.tree_widget.removeItemWidget(root, 0)
    for j, n in enumerate(json_data):
          #we have to initialized the root nodes
      if p is None:
        c = QTreeWidgetItem(self.tree_widget)       
      else:
        c = QTreeWidgetItem(p)#create new nodes
	
      c.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
      c.setCheckState(0,Qt.Checked)
      c.setText(0, n)
      
      if isinstance(json_data[n],list):# create last label with its value
        c.setText(1, str(json_data[n][0]))
      else:
        self.updateTree(json_data[n], c)# Go to children nodes
#______________________________________________________________________________
  def existDescendantChecked(self, tree_node, checked=False):
    c = 0
    while c < tree_node.childCount():
      if tree_node.child(c).checkState(0)==2:
        checked = True
      checked = self.existDescendantChecked(tree_node.child(c), checked)
      c += 1
    return checked
#______________________________________________________________________________
  def uncheckDescendant(self, tree_node):
    c = 0
    while c < tree_node.childCount():
      tree_node.child(c).setCheckState(0,Qt.Unchecked)
      if tree_node.child(c).childCount() is not None:
        self.uncheckDescendant(tree_node.child(c))
      c += 1
#______________________________________________________________________________
  def updateSelection(self, tree_node):
    #the clones of the custom group and the original graphs must have the same checked state
    leaf_list = self.getLeaves()
    for n in leaf_list[2]:
      if tree_node.text(0) == n.text(0):
        n.setCheckState(0,tree_node.checkState(0))
    #0 => unchecked
    #2 => checked
    if tree_node.checkState(0)==0:
      if tree_node.parent() is not None:
        parent = tree_node.parent()
        # this case is use if we want checking parent node if all its children are unchecked
        checked = False# True if node at the same lvl node are all checked
        for p in range( parent.childCount() ):
          if parent.child(p).checkState(0)==2:
            checked = True#if one node (at same lvl) is unchecked
        if checked == False:
          parent.setCheckState(0,Qt.Unchecked)
        else:
          parent.setCheckState(0,Qt.PartiallyChecked)
          
    elif tree_node.checkState(0)==2:
      # this case is use if we want selected all children
      for c in range( tree_node.childCount() ):
        tree_node.child(c).setCheckState(0,Qt.Checked)
      if tree_node.parent() is not None:
        parent = tree_node.parent()
        # this case is use if we want checking parent node if all its children are checked
        checked = True# True if node at the same lvl node are all checked
        for p in range( parent.childCount() ):
          if parent.child(p).checkState(0)==0:
            checked = False#if one node (at same lvl) is unchecked
        if checked == True:
          parent.setCheckState(0,Qt.Checked)
        else:
          parent.setCheckState(0,Qt.PartiallyChecked)
    
    elif ( tree_node.checkState(0)==1 and tree_node.parent() is not None ):
      tree_node.parent().setCheckState(0,Qt.PartiallyChecked)
    
#______________________________________________________________________________
  def createGroupWithNodeSelected(self, group_name):
    """This method aims is to select all brain's node children if they're selected """
    group_list = []
    all_group_list = self.tree_widget.selectedItems()
    for node in all_group_list:
      if self.rootItem(node) == 'brain':
        group_list.append(node)
    
    self.createGroup(group_list, group_name)
    self.leaves_sorted = self.sortLeavesBySide()
    
  def createGroupWithNodeChecked(self, group_name):
    """This method aims is to select all brain's node children if they're checked """
    brain_item = (self.tree_widget.findItems("brain", Qt.MatchExactly))[0]
    if brain_item.checkState(0) in [0,1]: #It's not usefull to copy the full tree
      group_list = self.getLeavesChecked(brain_item, [])
    else:
      QErrorMessage.showMessage( QErrorMessage.qtHandler(),\
      "Error: It's not pertinent to copy all the nodes" )
    
    self.createGroup(group_list, group_name)
    self.leaves_sorted = self.sortLeavesBySide()
    
  def createGroup(self, group_list, group_name):
    """This method aims is to create new customize group"""
    if not self.tree_widget.findItems("customized group", Qt.MatchExactly):
      group_item = QTreeWidgetItem(self.tree_widget)
      group_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
      group_item.setCheckState(0,Qt.Checked)
      group_item.setText(0, "customized group")
    else:
      group_item = (self.tree_widget.findItems("customized group", Qt.MatchExactly))[0]
    
    new_group = QTreeWidgetItem(group_item)
    new_group.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
    new_group.setCheckState(0,Qt.Checked)   
    new_group.setText(0, group_name)
    clone_group = []
    for node in group_list:
      clone_group.append( node.clone() )
    new_group.addChildren(clone_group)
    
#______________________________________________________________________________      
  def getLeavesChecked(self, tree_item, leaf_list):
    """This method return the leaf checked if is unique (ex: brainstem)
    However if the leaf is a subtree of region (right ou left) this method return
    a subtree start with it parent ( and the other uncheked children are removed )"""
    if self.existDescendantChecked(tree_item):
      c = 0
      while c < tree_item.childCount():
        self.getLeavesChecked(tree_item.child(c), leaf_list)
        c += 1
    #we are on leaf level
    elif tree_item.checkState(0) == 2:
      text = tree_item.text(0)
      if _use_qstring:
        text = unicode( text )
      if 'R_' in text or 'L_' in text \
          or text.endswith('_left') or text.endswith('_right'):
        parent_existing_in_list = False
        for t in leaf_list:
          #to avoid duplicate
          if tree_item.parent().text(0) == t.text(0):
          #if the parent exist we just have to add item as child
            t.addChild(tree_item.clone())
            parent_existing_in_list = True

        if not parent_existing_in_list:
          p = tree_item.parent().clone()
          c = 0
          while c < p.childCount():
            #we remove all "systers" of item
            if p.child(c).text(0) != tree_item.text(0):
              p.removeChild(p.child(c))
            #we don't iterate c because p.childCount() = p.childCount()-1
            else:
              c += 1
          #we add the parent with only one child (the item)
          leaf_list.append(p)
      else:
        #usefull for example: brainstem (neither R nor L)
        leaf_list.append(tree_item.clone())
    return leaf_list
#______________________________________________________________________________    
  def getLeaves( self ):
    """This method sort the leaves into 3 categories """
    iterator = QTreeWidgetItemIterator( self.tree_widget )
    checked_state_list = []
    unchecked_state_list = []
    while iterator.value():
      item = iterator.value()
      if item.text(1) != '' and item.checkState(0)==0:
        unchecked_state_list.append(item)
      elif item.text(1) != '' and item.checkState(0)==2:
        checked_state_list.append(item)
      iterator += 1
    all_leaves = unchecked_state_list + checked_state_list

    return [ unchecked_state_list, checked_state_list, all_leaves]
  
#______________________________________________________________________________  
  def rootItem(self, node):
    """This method return the name of the root item """
    if node.parent() is not None:
      root_name = self.rootItem(node.parent())
    else:
      root_name = node.text(0)
    return root_name
#______________________________________________________________________________
  def removeAction(self):
    #We have to use this step to avoid the conflict with the other signal "Clicked"
    #so left click select the row and right click start this remove function
    self.removeNode( self.tree_widget.currentItem() )
    self.leaves_sorted = self.sortLeavesBySide()
    
  def removeNode(self, node):
    """This method aims is to delete the item clicked by the user"""
    if self.rootItem(node) == 'customized group':
      if node.text(0) != 'customized group':
        node.parent().removeChild(node)
    elif self.rootItem(node) == 'brain':
      QErrorMessage.showMessage( QErrorMessage.qtHandler(),\
      "Error: It's forbidden to delete this item" )
#______________________________________________________________________________
  def saveInJson(self, QMainWidget):
    """This method aims is to save the ".roi" file"""
    filename = QFileDialog.getSaveFileName(QMainWidget,\
    'Choose roi file','', "ROI file (*.roi)")
 
    #we have to remove the potential old nodes if exists
    if len(self.json_full_data) == 2:
      del self.json_full_data["customized group"]
    #we have to create new jsondata for "customized group"
    if self.tree_widget.findItems("customized group", Qt.MatchExactly):
      item = self.tree_widget.findItems("customized group", Qt.MatchExactly)[0]
      new_json_data = self.writeNodeInJson(item)  
      #we have to mix the both trees
      self.json_full_data["customized group"] = new_json_data
    write_file = open(filename, "w")
    write_file.write(json.dumps(self.json_full_data, indent=4))
    
  def writeNodeInJson(self, item, dictio={}):
    """This method aims is to create JSON data with current tree """
    c = 0
    while c < item.childCount():
      label_name = str(item.child(c).text(0))
      
      if item.child(c).text(1) == '':
        dictio[label_name] = {}
        self.writeNodeInJson(item.child(c), dictio[label_name])
      else:
        label_value = str(item.child(c).text(1))
        dictio[label_name] = [label_value]
        
      c += 1
    return dictio
  
  def expandHierarchy(self, item):
    """when an item is selected,it hierarchy is expanded to allow the visualization"""
    item.setExpanded( True )
    if item.parent():
      self.expandHierarchy(item.parent())
  
  def reduceAllItem( self, item, root=False ):
    if root == False:
      item.setExpanded( False )
    self.tree_widget.collapseAll()
  
  def sortLeavesBySide(self):
    """This method aims is to sort all the leaves by side (often use) """
    right = []
    left = []
    central = []
    leaves_sorted = {'right' : right, 'left' : left, 'central' : central }
    
    leaf_list = self.getLeaves()[2]
    for l in leaf_list:
      if re.search('R_', l.text(0)) or re.search('right', str(l.text(0)).lower()):
        right.append(l)
      elif re.search('L_', l.text(0)) or re.search('left', str(l.text(0)).lower()):
        left.append(l)
      else:
        central.append(l)
    return leaves_sorted
  
  def selectRightBrain(self):
    for i in self.leaves_sorted['right']:
      i.setSelected(True)

  def checkRightBrain(self):
    leaves_checked = self.getLeaves()[1]
    for l in leaves_checked:
      l.setCheckState(0,Qt.Unchecked)
    #intersection method is use to rechecked only the leaves already checked before
    #but on the side that we want
    for i in set(self.leaves_sorted['right']).intersection(set(leaves_checked)):
      i.setCheckState(0,Qt.Checked)

  def selectLeftBrain(self):
    for i in self.leaves_sorted['left']:
      i.setSelected(True)
  
  def checkLeftBrain(self):
    leaves_checked = self.getLeaves()[1]
    for l in leaves_checked:
      l.setCheckState(0,Qt.Unchecked)
    #intersection method is use to rechecked only the leaves already checked before
    #but on the side that we want
    for i in set(self.leaves_sorted['left']).intersection(set(leaves_checked)):
      i.setCheckState(0,Qt.Checked)

  def selectCentralStruct(self):
    for i in self.leaves_sorted['central']:
      i.setSelected(True)

  def checkCentralStruct(self):
    leaves_checked = self.getLeaves()[1]
    for l in leaves_checked:
      l.setCheckState(0,Qt.Unchecked)
    #intersection method is use to rechecked only the leaves already checked before
    #but on the side that we want
    for i in set(self.leaves_sorted['central']).intersection(set(leaves_checked)):
      i.setCheckState(0,Qt.Checked)

  def createMemoryCheckedDict(self):    
    """This method aims is to save the checked state of nodes """  
    self.memory_checked_dict = {}
    it = QTreeWidgetItemIterator( self.tree_widget )
    while it.value():
      item = it.value()
      self.memory_checked_dict[item] = item.checkState(0)
      it += 1

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class SelectionAtlasAction( cpp.Action, QThread ):
  """This class aims is to create new control in anatomist window"""
  modes_list = ["Basic", "Intersection", "Union"]
  mode_basic = 0
  mode_intersection = 1
  mode_union = 2
  BoxColor_Gray = 0
  BoxColor_AsSelection = 1
  BoxColor_Custom = 2
  BoxColor_Modes = ( 'gray', 'as_selection', 'custom' )
  mode = mode_basic
  
  def __init__(self):
    cpp.Action.__init__(self)
  
  def selectionChanged( self ):
    for obj in gc.get_objects():
      if isinstance(obj, AtlasJsonRois):
        obj.selectionChanged()
      
class SelectionAtlasControl( cpp.Select3DControl ):
  """This class aims is to allow an event when mesh is selected by mouse"""
  def __init__( self,
    name = QT_TRANSLATE_NOOP( 'ControlledWindow', 'SelectionAtlasControl' ) ):
    cpp.Select3DControl.__init__( self, name )
    
  def eventAutoSubscription( self, pool ):
    cpp.Select3DControl.eventAutoSubscription( self, pool )
    self.selectionChangedEventSubscribe( pool.action( \
      'SelectionAtlasAction' ).selectionChanged )
