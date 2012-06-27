# -*- coding: iso-8859-1 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from PyQt4 import QtCore, QtGui
from soma import aims
from soma.qt4gui.rangeSlider import QRangeSlider
from tempfile import mkstemp
import anatomist.api as ana
import os

class PaletteEditor( QtGui.QGroupBox ):
    def __init__( self, image,
                  default=None, title="", palette_filter=None,
                  real_min = 0, real_max = 100,
                  parent=None, sliderPrecision = 100, zoom = 1):
        QtGui.QGroupBox.__init__( self, parent )
        
        self.real_min = real_min
        self.real_max = real_max
        self.sliderPrecision = sliderPrecision
        
        a = ana.Anatomist('-b')
        self.image = image
        self.setTitle( title )

        vlay = QtGui.QVBoxLayout( self )
        vlay.setMargin( 0 )
        
        font = QtGui.QFont()
        font.setPixelSize(12 * zoom)
        
        if palette_filter != []:
            hlay = QtGui.QHBoxLayout()
            vlay.addLayout( hlay )
            hlay.addSpacerItem( QtGui.QSpacerItem( 20 , 20 , hPolicy = QtGui.QSizePolicy.Expanding ) )
            self.palettecb = QtGui.QComboBox( self )
            self.palettecb.setFont(font)
            if(zoom > 1.0):
              self.palettecb.setFixedWidth( 256 * zoom)
            else:
              self.palettecb.setFixedWidth( 256 * zoom * zoom )
            self.palettecb.setToolTip( "Change the palette" )
            hlay.addWidget( self.palettecb )
            hlay.addSpacerItem( QtGui.QSpacerItem( 20 , 20 , hPolicy = QtGui.QSizePolicy.Expanding ) )
        
        hlay = QtGui.QHBoxLayout()
        hlay.setMargin( 0 )
        hlay.setSpacing( 0 )
        
        vlay.addLayout( hlay )
                
        if isinstance( self.real_min, float ) or isinstance( self.real_max, float ):
            self.minsb = QtGui.QDoubleSpinBox( self )
            self.minsb.setFont(font)
            self.minsb.setSingleStep( 0.1 )
        else:
            self.minsb = QtGui.QSpinBox( self )
        self.minsb.setFixedWidth( 62 * zoom )
        self.minsb.setRange( self.real_min, self.real_max )
        self.minsb.setToolTip( "Change the palette minimum value" )
        self.minsb.setFont(font)
        hlay.addWidget( self.minsb )
        
        self.rangeslider = QRangeSlider()
        self.rangeslider.show()
        self.rangeslider.setFixedHeight(32 * zoom)
        self.rangeslider.setFixedWidth(256 * zoom * zoom)
        self.rangeslider.setMin(0)
        self.rangeslider.setMax(sliderPrecision)
        self.rangeslider.setRange(0, sliderPrecision)
        hlay.addWidget( self.rangeslider )
        
        if isinstance( self.real_min, float ) or isinstance( self.real_max, float ):
            self.maxsb = QtGui.QDoubleSpinBox( self )
            self.maxsb.setSingleStep( 0.1 )
        else:
            self.maxsb = QtGui.QSpinBox( self )
        self.maxsb.setFixedWidth( 62 * zoom   )
        self.maxsb.setRange( self.real_min, self.real_max )
        self.maxsb.setToolTip( "Change the palette maximum value" )
        self.maxsb.setFont(font)
        hlay.addWidget( self.maxsb )
        
        self.paletteDic = {}
        
        self.loadPaletteList( palette_filter )
        
        if(default is None):
          # set palette name using current object palette info
            try:
              default = ((image.palette()).refPalette()).name()         
            except:
              default = None

        if palette_filter != []:
            try:
                self.palettecb.setCurrentIndex( self.paletteDic[ default ] )
            except:
                self.palettecb.setCurrentIndex( 0 )
    
        if palette_filter != []:
            self.connect( self.palettecb,
                          QtCore.SIGNAL( " currentIndexChanged( const QString& ) " ),
                          self.paletteNameChanged )
        if isinstance( self.real_min, float ) or isinstance( self.real_max, float ):
            self.connect( self.minsb,
                          QtCore.SIGNAL( " valueChanged( double ) " ),
                          self.minSbChanged )
            self.connect( self.maxsb,
                          QtCore.SIGNAL( " valueChanged( double ) " ),
                          self.maxSbChanged )
        else:
            self.connect( self.minsb,
                          QtCore.SIGNAL( " valueChanged( int ) " ),
                          self.minSbChanged )
            self.connect( self.maxsb,
                          QtCore.SIGNAL( " valueChanged( int ) " ),
                          self.maxSbChanged )
             
        # set palette bound using current object palette info
        paletteStart = image.palette().min1() * (real_max - real_min) + real_min
        paletteStart = int(paletteStart)
        paletteEnd = image.palette().max1() * (real_max - real_min) +  real_min
        paletteEnd = int(paletteEnd)
        self.rangeslider.setStart(int(image.palette().min1() * (real_max - real_min) + real_min))
        self.rangeslider.setEnd(int(image.palette().max1() * (real_max - real_min) +  real_min))        
        self.paletteMinMaxChanged()
    
        self.connect( self.rangeslider,
                 QtCore.SIGNAL( "startValueChanged( int ) " ),
                 self.paletteMinMaxChanged)
        self.connect( self.rangeslider,
                 QtCore.SIGNAL( "endValueChanged( int ) " ),
                 self.paletteMinMaxChanged)
        

        
    def loadPaletteList( self, palette_filter ):
        if palette_filter == []:
            return
        
        a = ana.Anatomist( '-b' )
        for p in a.palettes().palettes():
            name = p.name()
            if palette_filter and not name in palette_filter:
                continue
            self.paletteDic.update( { p.name() : self.palettecb.count() } )
            self.palettecb.addItem( p.name() )

    def paletteNameChanged( self, name):
        apal = self.image.getOrCreatePalette()        
        self.image.setPalette( name,\
                               minVal=apal.min1(),\
                               maxVal=apal.max1() )
        self.paletteMinMaxChanged()

    def paletteMinMaxChanged( self ):
        min = self.rangeslider.start()
        max = self.rangeslider.end()
        refpal = self.image.getOrCreatePalette().refPalette()
        self.image.setPalette( refpal.name(),\
                                minVal=min*(1.0/self.sliderPrecision),\
                                maxVal=max*(1.0/self.sliderPrecision) )

        if not self.rangeslider._movingHandle:
            paletteinfo = self.updatePaletteLabel()
            tempfile = mkstemp()[1]
            paletteinfo[0].save(tempfile, "PNG")
            self.rangeslider.setStyleSheet("QRangeSlider * { border: 0px; padding: 0px; } \
                                            QRangeSlider #Head { background: " + paletteinfo[1] + " repeat-x; } \
                                            QRangeSlider #Span { background: url(" + tempfile + ") repeat-x; } \
                                            QRangeSlider #Tail { background: "+ paletteinfo[2] + " repeat-x; } \
                                            QRangeSlider > QSplitter::handle { background: #888888; } \
                                            QRangeSlider > QSplitter::handle:vertical { height: 4px; } \
                                            QRangeSlider > QSplitter::handle:pressed { background: #ACACAC; } ")
            os.remove(tempfile)
        
        
        real_min = ( ( self.real_max - self.real_min ) * min /  self.sliderPrecision ) + self.real_min
        real_max = ( ( self.real_max - self.real_min ) * max /  self.sliderPrecision ) + self.real_min
        
        self.minsb.blockSignals( True )
        self.minsb.setValue( real_min )
        self.minsb.blockSignals( False )
        self.maxsb.blockSignals( True )
        self.maxsb.setValue( real_max )
        self.maxsb.blockSignals( False )

    def updatePaletteLabel( self ):
        apal = self.image.getOrCreatePalette()
        min = apal.min1()
        max = apal.max1()

        refpal = apal.refPalette()
        dimx = refpal.dimX()
        dimy = refpal.dimY()
        if dimy < 32:
            dimy = 32
        if dimx > 256:
            dimx = 256
        elif dimx == 0:
            dimx = 1
        if dimy > 256:
            dimy = 256
        if (int(max - min) < 1): 
            min = 0
            max = 1
        
        facx = float( refpal.dimX() ) / dimx;
        facy = float( refpal.dimY() ) / dimy;
        
        rgb = aims.AimsRGBA
        minx = dimx * min
        maxx = dimx * max
        
        range = int(maxx-minx)
        
        imbackground = QtGui.QImage( QtCore.QSize( range, int(dimy) ), 4 )
        pmbackground = QtGui.QPixmap()
        
        for x in xrange( dimx ):
            rgb = refpal.value( int( facx * x ), 0)
        
            for y in xrange( dimy ):
                xpal = int(x*(maxx-minx)/dimx)
                if xpal >= range:
                    xpal = range-1
                
                imbackground.setPixel( xpal, y, QtGui.qRgb( rgb.red(), rgb.green(), rgb.blue() ) )
                
        if cmp( QtCore.QT_VERSION_STR , '4.7' ) == -1:
            pmbackground = QtGui.QPixmap.fromImage( imbackground )
        else:
            pmbackground.convertFromImage( imbackground );
        
        rgb = refpal.value( 0, 0 )
        valueinf = '#%02x%02x%02x' % (rgb.red(), rgb.green(), rgb.blue() )
        rgb = refpal.value( int( facx * (dimx-1) ), int( facy * (dimy-1) ) )
        valuesup = '#%02x%02x%02x' % (rgb.red(), rgb.green(), rgb.blue() )

        return ( pmbackground, valueinf, valuesup )

    def minSbChanged( self, value ):
        if value >= self.maxsb.value():
            value = self.maxsb.value()-1
        
        slider_value = self.sliderPrecision * ( value - self.real_min ) / ( self.real_max - self.real_min )
        
        self.rangeslider.setStart( int( slider_value ) )

    def maxSbChanged( self, value ):
        if value <= self.minsb.value():
            value = self.minsb.value()+1
        
        slider_value = self.sliderPrecision * ( value - self.real_min ) / ( self.real_max - self.real_min )
        
        self.rangeslider.setEnd( int( slider_value ) )
