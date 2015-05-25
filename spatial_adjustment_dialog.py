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
    markerListMP = []
    markerListMC = []
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
        QObject.connect(self.cleanSelBtn, SIGNAL("clicked()"), self.cleanSel)
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
        """
        prova codice per snap

        # trasforma in screen coordinates
        newPoint = self.mapPreview.getCoordinateTransform().transform(point)
        # .. e in QPoint 
        pnt = QPoint(newPoint.x(),newPoint.y())
        # attiva lo snapper
        mySnapper = QgsMapCanvasSnapper(self.mapPreview)
        (reval, snapped) = mySnapper.snapToBackgroundLayers(pnt)
        if snapped != []:
            print "ok"
        else:
            print 'no'
        """
        markerMapPreview = self.addPnt(self.mapPreview,point)
        self.markerListMP.append(markerMapPreview)
        self.srcList.append([point.x(),point.y()])
        nRow = self.tableWidget.rowCount()
        self.tableWidget.insertRow(nRow)
        checkItem = QTableWidgetItem()
        checkItem.setFlags(Qt.ItemIsUserCheckable |
                           Qt.ItemIsEnabled)
        checkItem.setCheckState(Qt.Checked)
        self.tableWidget.setItem(nRow,0, checkItem)        
        self.tableWidget.setItem(nRow,1, QTableWidgetItem(str(point.x())))        
        self.tableWidget.setItem(nRow,2, QTableWidgetItem(str(point.y())))


        self.clickTool1.canvasClicked.disconnect()
        self.mapPreview.unsetMapTool(self.clickTool1)
        self.clickTool2 = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.clickTool2)
        self.clickTool2.canvasClicked.connect(self.clickMapCanvas)

    def clickMapCanvas(self, point, button):
        QMessageBox.information(None, 'info', str(point.x())+', '+str(point.y()))
        markerMapCanvas = self.addPnt(self.canvas,point)
        self.markerListMC.append(markerMapCanvas)
        self.dstList.append([point.x(),point.y()])
        self.clickTool2.canvasClicked.disconnect()
        self.canvas.unsetMapTool(self.clickTool2)
        nRow = self.tableWidget.rowCount()
        self.tableWidget.setItem(nRow-1,3, QTableWidgetItem(str(point.x())))        
        self.tableWidget.setItem(nRow-1,4, QTableWidgetItem(str(point.y())))

    def cleanSel(self):
        """
            Pulisce lo stack dei selezionati e toglie i marker;
        """
        # elimina i marcatori
        for m in self.markerListMC:
            self.canvas.scene().removeItem(m)
            print m
        self.markerListMC = []
        for m in self.markerListMP:
            self.mapPreview.scene().removeItem(m)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.markerListMP = []
        # rinfresca il video
        self.canvas.refresh()
        self.mapPreview.refresh()

    def getValues(self):
        """
            get the table values
        """
        nRow = self.tableWidget.rowCount()
        nCol = self.tableWidget.columnCount()
        data = []
        for r in range(nRow):
            riga = []
        for c in range(nCol):
            item = self.tableWidget.item(r,c)
            print item.text()
            riga.append(item.text())
        data.append(riga)
        return data

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
        #QMessageBox.information(, 'info', "running" )
        basepath = os.path.dirname(__file__)
        idCsv = 'sad'
        filepath = os.path.abspath(os.path.join(basepath, idCsv+".csv"))
        data = self.getValues()
        with open(filepath, "w") as gcpCSV:
            writer = csv.writer(gcpCSV, delimiter=' ')
            i = 0
            for r in data:
                writer.writerow(r)
                i = i+1
        gcpCSV.close()
        #for m in gcpList:
        #    csv.writerow()
        out = processing.runalg('grass:v.transform.pointsfile',self.vLayer,filepath,None,None,None,None,0,'prova.shp')
        print str(out['output'])
        self.vLayer = QgsVectorLayer(str(out['output']), 'output_spatialadjustment.shp', "ogr")
        os.remove(filepath)

