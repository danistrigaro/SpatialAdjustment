# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SpatialAdjustmentDialog
                                 A QGIS plugin
 A tool to adjust vector layers
                             -------------------
        begin                : 2015-05-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Daniele Strigaro
        email                : daniele.strigaro@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic
from qgis.gui import *
from qgis.core import *
import processing
import csv

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'spatial_adjustment_dialog_base.ui'))


class SpatialAdjustmentDialog(QtGui.QDialog, FORM_CLASS):
    vLayer = ""
    srcList = []
    dstList = []
    markerListMapPreview = []
    markerListCanvas = []
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(SpatialAdjustmentDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.canvas = iface.mapCanvas()
        #attacco funzioni ai bottoni
        QObject.connect(self.loadLayerBtn, SIGNAL("clicked()"), self.loadLayer)
        QObject.connect(self.removeLayerBtn, SIGNAL("clicked()"), self.removeLayer)
        QObject.connect(self.addGCPBtn, SIGNAL("clicked()"), self.addGCP)
        QObject.connect(self.run, SIGNAL("clicked()"), self.runAdjust)
        #creao il mapcavas
        self.mapPreview = QgsMapCanvas(self)
        self.tabWidget.addTab(self.mapPreview, "Map Canvas")

    #personal function
    #function to add layer
    def loadLayer(self):
        if (self.vLayer == ""):
            pname = QFileDialog.getOpenFileName(None,'Open file',os.path.expanduser('~'),'*.shp')
            if pname:
                fname = pname.split('/')
                self.vLayer = QgsVectorLayer(pname, fname[-1] + '_adjust', "ogr")
                print "aperto layer",fname[-1]
                layerToSet = []
                QgsMapLayerRegistry.instance().addMapLayers([self.vLayer], False)
                layerToSet.append(QgsMapCanvasLayer(self.vLayer, True, False))
                self.mapPreview.setLayerSet(layerToSet)
                self.mapPreview.zoomToFullExtent()
                # azzera la tabella dei CP
                #self.on_pushButton_clear_pressed()
        else:
            QMessageBox.information(None, 'info', "Please remove the layer that is already present" )
    #function to remove layer
    def removeLayer(self):
        if (self.vLayer != ""):
            QgsMapLayerRegistry.instance().removeMapLayer(self.vLayer.id())
            self.mapPreview.refresh()
            self.vLayer = ""
    #functions to add point
    def addPnt(self,canvas,pnt):
        color = QColor(250,150,0)
        size = 25
        x,y = pnt.x(),pnt.y()
        marker = QgsVertexMarker(canvas)
        marker.setColor(color)
        marker.setIconSize(size)
        marker.setCenter(QgsPoint(x,y))
        marker.show()
        
        return marker

    def rmPnt(self):
        asd = 0

    def clickMapPreview(self, point, button):
        QMessageBox.information(None, 'info', str(point.x())+', '+str(point.y()) )
        self.addPnt(self.mapPreview,point)
        self.srcList.append([point.x(),point.y()])
        print self.srcList
        self.clickTool1.canvasClicked.disconnect()
        self.mapPreview.unsetMapTool(self.clickTool1)
        self.clickTool2 = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.clickTool2)
        self.clickTool2.canvasClicked.connect(self.clickMapCanvas)

    def clickMapCanvas(self, point, button):
        QMessageBox.information(None, 'info', str(point.x())+', '+str(point.y()))
        self.addPnt(self.canvas,point)
        self.dstList.append([point.x(),point.y()])
        self.clickTool2.canvasClicked.disconnect()
        self.canvas.unsetMapTool(self.clickTool2)

    def addGCP(self):
        if (self.vLayer != ""):
            # out click tool will emit a QgsPoint on every click
            self.clickTool1 = QgsMapToolEmitPoint(self.mapPreview)
            self.clickTool1.canvasClicked.connect(self.clickMapPreview)
            self.mapPreview.setMapTool(self.clickTool1)
        else:
            QMessageBox.information(None, 'info', "Please insert a layer" )

    #spatial adjustment function
    def runAdjust(self):
        QMessageBox.information(None, 'info', "running" )
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, os.urandom(10)+".csv"))
        with open(filepath, "w") as gcpCSV:
            writer = csv.writer(gcpCSV, delimiter=' ')
            i = 0
            for r in self.srcList:
                writer.writerow(r + self.dstList[i])
                i = i+1
        gcpCSV.close()
        #for m in gcpList:
        #    csv.writerow()
        
        processing.runalg('grass:v.transform.pointsfile','/home/daniele/Scrivania/catasto_prova/sgp_catasto/strade.shp','gcp.csv',None,None,None,None,None,None)
        os.remove(filepath)
