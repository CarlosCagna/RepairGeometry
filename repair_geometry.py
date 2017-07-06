# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RepairGeometry
                                 A QGIS plugin
 Use some V.clean tools in select features
                             -------------------
        begin                : 2017-06-05
        copyright            : (C) 2017 by aCarlos Eduardo Cagna        
        email                : carlos.cagna@ibge.gov.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources
import processing    
# Import the code for the dialog
from repair_geometry_dialog import RepairGeometryDialog
import os.path


class RepairGeometry:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RepairGeometry_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Repair Geometry')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RepairGeometry')
        self.toolbar.setObjectName(u'RepairGeometry')
        self.iface = iface
        self.toolButton = QToolButton()
        self.toolButton.setMenu(QMenu())
        self.toolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.iface.addToolBarWidget(self.toolButton)
        self.dgl = RepairGeometryDialog()
        self.snap_= False     
        self.rmdangle_= False              
        self.chdangle_= False     
        self.rmbridge_= False     
        self.chbridge_= False     
        self.rmdupl_= False     
        self.rmdac_= False      
        self.bpol_= False     
        self.prune_= False     
        self.rmarea_= False     
        self.rmline_= False     
        self.rmsa_= False    
        self.load_errors= False    
        self.set_var_proj= QgsExpressionContextUtils.projectScope().variable('set_var_proj')
               
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RepairGeometry', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = RepairGeometryDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.actionRun = QAction(
            QIcon(':/plugins/RepairGeometry/icon.png'), 
            u"Repair Geometry", 
        self.iface.mainWindow())
        self.actionRun.setWhatsThis(u"Repair Geometry")
  
        self.iface.addPluginToMenu("&Repair Geometry", self.actionRun)
            
        m = self.toolButton.menu()
        m.addAction(self.actionRun)
        
        self.toolButton.setDefaultAction(self.actionRun)
        
        QObject.connect(self.actionRun, SIGNAL("triggered()"), self.run)
        
        self.actionConfigure = QAction(
        QIcon(':/plugins/RepairGeometry/icon.png'), 
        u"set v.clean variables", 
        self.iface.mainWindow())
        self.actionConfigure.setWhatsThis(u"set v.clean variables")
        m.addAction(self.actionConfigure)
        self.iface.addPluginToMenu("&Repair Geometry", self.actionConfigure)
        QObject.connect(self.actionConfigure, SIGNAL("triggered()"), self.set_variables)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Repair Geometry'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def set_variables(self):
        """Run method that performs all the real work"""
        #show the dialog
        self.dlg = RepairGeometryDialog()
        
        if self.iface.activeLayer()<> None:
            if QgsExpressionContextUtils.projectScope().variable('set') <> u'True':
                self.dlg.checkBox_1.setChecked(True)         
                self.dlg.checkBox_2.setChecked(True)           
                self.dlg.checkBox_12.setChecked(True)
                QgsExpressionContextUtils.setProjectVariable('set','True')
                
                if iface.activeLayer().crs().mapUnits() == 0:
                    x='3'
                    y = '-1'
                    z = '10'
       
                    self.dlg.threshold_0.setText(x)
                    self.dlg.threshold_1.setText(x)
                    self.dlg.threshold_2.setText(x)
                    self.dlg.threshold_3.setText(x)
                    self.dlg.threshold_4.setText(x)
                    self.dlg.threshold_5.setText(x)
                    self.dlg.threshold_6.setText(x)
                    self.dlg.threshold_7.setText(x)
                    self.dlg.threshold_8.setText(x)
                    self.dlg.threshold_9.setText(x)
                    self.dlg.threshold_10.setText(x)
                    self.dlg.threshold_11.setText(x)
                    self.dlg.threshold_12.setText(x)
                    
                    self.dlg.snap_0.setText(y)
                    self.dlg.snap_1.setText('1')
                    self.dlg.snap_2.setText('10')
                    self.dlg.snap_3.setText(y)
                    self.dlg.snap_4.setText(y)
                    self.dlg.snap_5.setText(y)
                    self.dlg.snap_6.setText(y)
                    self.dlg.snap_7.setText(y)
                    self.dlg.snap_8.setText(y)
                    self.dlg.snap_9.setText(y)
                    self.dlg.snap_10.setText(y)
                    self.dlg.snap_11.setText(y)
                    self.dlg.snap_12.setText(y)
                    
                    self.dlg.minarea_0.setText(z)
                    self.dlg.minarea_1.setText(z)
                    self.dlg.minarea_2.setText('10')
                    self.dlg.minarea_3.setText(z)
                    self.dlg.minarea_4.setText(z)
                    self.dlg.minarea_5.setText(z)
                    self.dlg.minarea_6.setText(z)
                    self.dlg.minarea_7.setText(z)
                    self.dlg.minarea_8.setText(z)
                    self.dlg.minarea_9.setText(z)
                    self.dlg.minarea_10.setText(z)
                    self.dlg.minarea_11.setText(z)
                    self.dlg.minarea_12.setText(z)
                                

                    
                elif iface.activeLayer().crs().mapUnits() == 2:
                    x='3e-05'
                    y = '-1'
                    z = '0.0001'
       
                    self.dlg.threshold_0.setText(x)
                    self.dlg.threshold_1.setText(x)
                    self.dlg.threshold_2.setText(x)
                    self.dlg.threshold_3.setText(x)
                    self.dlg.threshold_4.setText(x)
                    self.dlg.threshold_5.setText(x)
                    self.dlg.threshold_6.setText(x)
                    self.dlg.threshold_7.setText(x)
                    self.dlg.threshold_8.setText(x)
                    self.dlg.threshold_9.setText(x)
                    self.dlg.threshold_10.setText(x)
                    self.dlg.threshold_11.setText(x)
                    self.dlg.threshold_12.setText(x)
                    
                    self.dlg.snap_0.setText(y)
                    self.dlg.snap_1.setText('0.00001')
                    self.dlg.snap_2.setText('0.0001')
                    self.dlg.snap_3.setText(y)
                    self.dlg.snap_4.setText(y)
                    self.dlg.snap_5.setText(y)
                    self.dlg.snap_6.setText(y)
                    self.dlg.snap_7.setText(y)
                    self.dlg.snap_8.setText(y)
                    self.dlg.snap_9.setText(y)
                    self.dlg.snap_10.setText(y)
                    self.dlg.snap_11.setText(y)
                    self.dlg.snap_12.setText(y)
                    
                    self.dlg.minarea_0.setText(z)
                    self.dlg.minarea_1.setText(z)
                    self.dlg.minarea_2.setText('0.0001')
                    self.dlg.minarea_3.setText(z)
                    self.dlg.minarea_4.setText(z)
                    self.dlg.minarea_5.setText(z)
                    self.dlg.minarea_6.setText(z)
                    self.dlg.minarea_7.setText(z)
                    self.dlg.minarea_8.setText(z)
                    self.dlg.minarea_9.setText(z)
                    self.dlg.minarea_10.setText(z)
                    self.dlg.minarea_11.setText(z)
                    self.dlg.minarea_12.setText(z)
                                
                    
            else:
            
                    self.dlg.threshold_0.setText(QgsExpressionContextUtils.projectScope().variable('threshold_0'))
                    self.dlg.threshold_1.setText(QgsExpressionContextUtils.projectScope().variable('threshold_1'))
                    self.dlg.threshold_2.setText(QgsExpressionContextUtils.projectScope().variable('threshold_2'))
                    self.dlg.threshold_3.setText(QgsExpressionContextUtils.projectScope().variable('threshold_3'))
                    self.dlg.threshold_4.setText(QgsExpressionContextUtils.projectScope().variable('threshold_4'))
                    self.dlg.threshold_5.setText(QgsExpressionContextUtils.projectScope().variable('threshold_5'))
                    self.dlg.threshold_6.setText(QgsExpressionContextUtils.projectScope().variable('threshold_6'))
                    self.dlg.threshold_7.setText(QgsExpressionContextUtils.projectScope().variable('threshold_7'))
                    self.dlg.threshold_8.setText(QgsExpressionContextUtils.projectScope().variable('threshold_8'))
                    self.dlg.threshold_9.setText(QgsExpressionContextUtils.projectScope().variable('threshold_9'))
                    self.dlg.threshold_10.setText(QgsExpressionContextUtils.projectScope().variable('threshold_10'))
                    self.dlg.threshold_11.setText(QgsExpressionContextUtils.projectScope().variable('threshold_11'))
                    self.dlg.threshold_12.setText(QgsExpressionContextUtils.projectScope().variable('threshold_12'))
                    
                    self.dlg.snap_0.setText(QgsExpressionContextUtils.projectScope().variable('snap_0'))
                    self.dlg.snap_1.setText(QgsExpressionContextUtils.projectScope().variable('snap_1'))
                    self.dlg.snap_2.setText(QgsExpressionContextUtils.projectScope().variable('snap_2'))
                    self.dlg.snap_3.setText(QgsExpressionContextUtils.projectScope().variable('snap_3'))
                    self.dlg.snap_4.setText(QgsExpressionContextUtils.projectScope().variable('snap_4'))
                    self.dlg.snap_5.setText(QgsExpressionContextUtils.projectScope().variable('snap_5'))
                    self.dlg.snap_6.setText(QgsExpressionContextUtils.projectScope().variable('snap_6'))
                    self.dlg.snap_7.setText(QgsExpressionContextUtils.projectScope().variable('snap_7'))
                    self.dlg.snap_8.setText(QgsExpressionContextUtils.projectScope().variable('snap_8'))
                    self.dlg.snap_9.setText(QgsExpressionContextUtils.projectScope().variable('snap_9'))
                    self.dlg.snap_10.setText(QgsExpressionContextUtils.projectScope().variable('snap_10'))
                    self.dlg.snap_11.setText(QgsExpressionContextUtils.projectScope().variable('snap_11'))
                    self.dlg.snap_12.setText(QgsExpressionContextUtils.projectScope().variable('snap_12'))

                    self.dlg.minarea_0.setText(QgsExpressionContextUtils.projectScope().variable('minarea_0'))
                    self.dlg.minarea_1.setText(QgsExpressionContextUtils.projectScope().variable('minarea_1'))
                    self.dlg.minarea_2.setText(QgsExpressionContextUtils.projectScope().variable('minarea_2'))
                    self.dlg.minarea_3.setText(QgsExpressionContextUtils.projectScope().variable('minarea_3'))
                    self.dlg.minarea_4.setText(QgsExpressionContextUtils.projectScope().variable('minarea_4'))
                    self.dlg.minarea_5.setText(QgsExpressionContextUtils.projectScope().variable('minarea_5'))
                    self.dlg.minarea_6.setText(QgsExpressionContextUtils.projectScope().variable('minarea_6'))
                    self.dlg.minarea_7.setText(QgsExpressionContextUtils.projectScope().variable('minarea_7'))
                    self.dlg.minarea_8.setText(QgsExpressionContextUtils.projectScope().variable('minarea_8'))
                    self.dlg.minarea_9.setText(QgsExpressionContextUtils.projectScope().variable('minarea_9'))
                    self.dlg.minarea_10.setText(QgsExpressionContextUtils.projectScope().variable('minarea_10'))
                    self.dlg.minarea_11.setText(QgsExpressionContextUtils.projectScope().variable('minarea_11'))
                    self.dlg.minarea_12.setText(QgsExpressionContextUtils.projectScope().variable('minarea_12'))
                    

                    
                    self.dlg.checkBox_0.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('break')))
                    self.dlg.checkBox_1.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('snap')))         
                    self.dlg.checkBox_2.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmdangle')))           
                    self.dlg.checkBox_3.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('chdangle')))
                    self.dlg.checkBox_4.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmbridge'))) 
                    self.dlg.checkBox_5.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('chbridge'))) 
                    self.dlg.checkBox_6.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmdupl')))  
                    self.dlg.checkBox_7.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmdac')))  
                    self.dlg.checkBox_8.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('bpol')))  
                    self.dlg.checkBox_9.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('prune'))) 
                    self.dlg.checkBox_10.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmarea'))) 
                    self.dlg.checkBox_11.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmline'))) 
                    
                    self.dlg.checkBox_12.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('rmsa')))

                    self.dlg.errors_checkBox.setChecked(self.str_to_bool(QgsExpressionContextUtils.projectScope().variable('load_errors')))            

                    
        
        self.dlg.show() 
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        QgsExpressionContextUtils.setProjectVariable('threshold_0',self.dlg.threshold_0.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_1',self.dlg.threshold_1.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_2',self.dlg.threshold_2.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_3',self.dlg.threshold_3.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_4',self.dlg.threshold_4.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_5',self.dlg.threshold_5.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_6',self.dlg.threshold_6.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_7',self.dlg.threshold_7.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_8',self.dlg.threshold_8.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_9',self.dlg.threshold_9.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_10',self.dlg.threshold_10.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_11',self.dlg.threshold_11.text())
        QgsExpressionContextUtils.setProjectVariable('threshold_12',self.dlg.threshold_12.text())


        QgsExpressionContextUtils.setProjectVariable('snap_0',self.dlg.snap_0.text())
        QgsExpressionContextUtils.setProjectVariable('snap_1',self.dlg.snap_1.text())
        QgsExpressionContextUtils.setProjectVariable('snap_2',self.dlg.snap_2.text())
        QgsExpressionContextUtils.setProjectVariable('snap_3',self.dlg.snap_3.text())
        QgsExpressionContextUtils.setProjectVariable('snap_4',self.dlg.snap_4.text())
        QgsExpressionContextUtils.setProjectVariable('snap_5',self.dlg.snap_5.text())
        QgsExpressionContextUtils.setProjectVariable('snap_6',self.dlg.snap_6.text())
        QgsExpressionContextUtils.setProjectVariable('snap_7',self.dlg.snap_7.text())
        QgsExpressionContextUtils.setProjectVariable('snap_8',self.dlg.snap_8.text())
        QgsExpressionContextUtils.setProjectVariable('snap_9',self.dlg.snap_9.text())
        QgsExpressionContextUtils.setProjectVariable('snap_10',self.dlg.snap_10.text())
        QgsExpressionContextUtils.setProjectVariable('snap_11',self.dlg.snap_11.text())
        QgsExpressionContextUtils.setProjectVariable('snap_12',self.dlg.snap_12.text())
        
        QgsExpressionContextUtils.setProjectVariable('minarea_0',self.dlg.minarea_0.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_1',self.dlg.minarea_1.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_2',self.dlg.minarea_2.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_3',self.dlg.minarea_3.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_4',self.dlg.minarea_4.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_5',self.dlg.minarea_5.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_6',self.dlg.minarea_6.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_7',self.dlg.minarea_7.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_8',self.dlg.minarea_8.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_9',self.dlg.minarea_9.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_10',self.dlg.minarea_10.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_11',self.dlg.minarea_11.text())
        QgsExpressionContextUtils.setProjectVariable('minarea_12',self.dlg.minarea_12.text())
           
        QgsExpressionContextUtils.setProjectVariable('break',self.dlg.checkBox_0.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('snap',self.dlg.checkBox_1.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmdangle',self.dlg.checkBox_2.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('chdangle',self.dlg.checkBox_3.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmbridge',self.dlg.checkBox_4.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('chbridge',self.dlg.checkBox_5.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmdupl',self.dlg.checkBox_6.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmdac',self.dlg.checkBox_7.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('bpol',self.dlg.checkBox_8.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('prune',self.dlg.checkBox_9.isChecked())
        QgsExpressionContextUtils.setProjectVariable('rmarea',self.dlg.checkBox_10.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmline',self.dlg.checkBox_11.isChecked()) 
        QgsExpressionContextUtils.setProjectVariable('rmsa',self.dlg.checkBox_12.isChecked()) 
        
        QgsExpressionContextUtils.setProjectVariable('load_errors',self.dlg.errors_checkBox.isChecked()) 

        pass
        
    def str_to_bool(self, string):
        if string == 'true':
             return True
        else:
             return False

    def v_clean(self, v_clean_name, v_clean_number, threshold, snap, minarea):
            print ('self.'+v_clean_name+'_')
            clean = processing.runalg( "grass7:v.clean", self.OUTPUT, v_clean_number, threshold, self.extend, snap , minarea, None, None)                
            self.OUTPUT = QgsVectorLayer(clean["output"], ("clean_" + v_clean_name), "ogr") 

            error = QgsVectorLayer(clean["error"], ("error_" + v_clean_name), "ogr")
            if error.featureCount() <> 0 and QgsExpressionContextUtils.projectScope().variable('load_errors') == 'true':
                QgsMapLayerRegistry.instance().addMapLayer(error)        
                                               
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        inlayer= self.iface.activeLayer()
        
        
        if QgsExpressionContextUtils.projectScope().variable('set') <> u'True':              
           self.set_variables()
                
   
        if len(inlayer.selectedFeatures()) <> 0:

            xmin= inlayer.extent().xMinimum()
            xmax=inlayer.extent().xMaximum()
            ymin=inlayer.extent().yMinimum()
            ymax=inlayer.extent().yMaximum()

            self.extend =  str(float(xmin)) + ", " +  str(float(xmax))+", " + str(float(ymin))+ ", " +str(float(ymax))
            
            self.OUTPUT = inlayer


            
            if QgsExpressionContextUtils.projectScope().variable('break') == 'true':
                self.v_clean('break', 0, QgsExpressionContextUtils.projectScope().variable('threshold_0'), QgsExpressionContextUtils.projectScope().variable('snap_0'), QgsExpressionContextUtils.projectScope().variable('minarea_0'))
            if QgsExpressionContextUtils.projectScope().variable('snap') == 'true':     
                self.v_clean('snap', 1, QgsExpressionContextUtils.projectScope().variable('threshold_1'), QgsExpressionContextUtils.projectScope().variable('snap_1'), QgsExpressionContextUtils.projectScope().variable('minarea_1'))    
            if QgsExpressionContextUtils.projectScope().variable('rmdangle') == 'true':     
                self.v_clean('rmdangle', 2, QgsExpressionContextUtils.projectScope().variable('threshold_2'), QgsExpressionContextUtils.projectScope().variable('snap_2'), QgsExpressionContextUtils.projectScope().variable('minarea_2'))
            if QgsExpressionContextUtils.projectScope().variable('chdangle') == 'true':    
                self.v_clean('chdangle', 3, QgsExpressionContextUtils.projectScope().variable('threshold_3'), QgsExpressionContextUtils.projectScope().variable('snap_3'), QgsExpressionContextUtils.projectScope().variable('minarea_3'))
            if QgsExpressionContextUtils.projectScope().variable('rmbridge') == 'true':    
                self.v_clean('rmbridge', 4, QgsExpressionContextUtils.projectScope().variable('threshold_4'), QgsExpressionContextUtils.projectScope().variable('snap_4'), QgsExpressionContextUtils.projectScope().variable('minarea_4'))
            if QgsExpressionContextUtils.projectScope().variable('chbridge') == 'true':     
                self.v_clean('chbridge', 5, QgsExpressionContextUtils.projectScope().variable('threshold_5'), QgsExpressionContextUtils.projectScope().variable('snap_5'), QgsExpressionContextUtils.projectScope().variable('minarea_5'))
            if QgsExpressionContextUtils.projectScope().variable('rmdupl') == 'true':    
                self.v_clean('rmdupl', 6, QgsExpressionContextUtils.projectScope().variable('threshold_6'), QgsExpressionContextUtils.projectScope().variable('snap_6'), QgsExpressionContextUtils.projectScope().variable('minarea_6'))
            if QgsExpressionContextUtils.projectScope().variable('rmdac') == 'true':    
                self.v_clean('rmdac', 7, QgsExpressionContextUtils.projectScope().variable('threshold_7'), QgsExpressionContextUtils.projectScope().variable('snap_7'), QgsExpressionContextUtils.projectScope().variable('minarea_7'))  
            if QgsExpressionContextUtils.projectScope().variable('bpol') == 'true':    
                self.v_clean('bpol', 8, QgsExpressionContextUtils.projectScope().variable('threshold_8'), QgsExpressionContextUtils.projectScope().variable('snap_8'), QgsExpressionContextUtils.projectScope().variable('minarea_8')) 
            if QgsExpressionContextUtils.projectScope().variable('prune') == 'true':    
                self.v_clean('prune', 9, QgsExpressionContextUtils.projectScope().variable('threshold_9'), QgsExpressionContextUtils.projectScope().variable('snap_9'), QgsExpressionContextUtils.projectScope().variable('minarea_9'))   
            if QgsExpressionContextUtils.projectScope().variable('rmarea') == 'true':    
                self.v_clean('rmarea', 10, QgsExpressionContextUtils.projectScope().variable('threshold_10'), QgsExpressionContextUtils.projectScope().variable('snap_10'), QgsExpressionContextUtils.projectScope().variable('minarea_10')) 
            if QgsExpressionContextUtils.projectScope().variable('rmline') == 'true':    
                self.v_clean('rmline', 11, QgsExpressionContextUtils.projectScope().variable('threshold_11'), QgsExpressionContextUtils.projectScope().variable('snap_11'), QgsExpressionContextUtils.projectScope().variable('minarea_11'))
            if QgsExpressionContextUtils.projectScope().variable('rmsa') == 'true':    
                self.v_clean('rmsa', 12, QgsExpressionContextUtils.projectScope().variable('threshold_12'), QgsExpressionContextUtils.projectScope().variable('snap_12'), QgsExpressionContextUtils.projectScope().variable('minarea_12'))    
                        
                
            clean_shape = self.OUTPUT
                
            
            inlayer.startEditing()
            select = inlayer.selectedFeatures()
            box = inlayer.boundingBoxOfSelected()
            select_id= [] #seleciona as feicoes selecinadas no carvas para deletalas e substituilas pelo resultado do v.clean
            x=0
            for feat in select:
                 select_id.insert(x, feat.id())
                 x= x+1
            
            for feat in inlayer.getFeatures():
                if feat.id() in select_id:
                    inlayer.deleteFeature(feat.id())


            for feat in  clean_shape.getFeatures():
                inlayer.addFeature(feat)

                
            if inlayer.attributeDisplayName(0) == u'id':
                todos_id=[] #faz uma lista de todas id para indetificar aquelas que estao repetidas
                x=0
                for feat in inlayer.getFeatures():
                    if feat.attribute('id') <> NULL:     
                        todos_id.insert(x, feat.attribute('id'))
                        x=x+1                            
                      
                     
                for feat in inlayer.getFeatures(): #altera o id que aparecem repetidos para nao ocorrer conflito ao inserir os dados no postgis      
                       while todos_id.count(feat.attribute('id'))>1:
                        id_antigo = feat.attribute('id')
                        feat.setAttribute(inlayer.fieldNameIndex('id'), (max(todos_id)+1) )
                        inlayer.updateFeature(feat)
                        todos_id.insert(x, feat.attribute('id'))
                        todos_id.remove(id_antigo)
                        x=x+1
                        inlayer.updateFeature(feat)
                    
                for feat in inlayer.getFeatures():

                       if 'QgsPolygonV2' in str(feat.geometry().geometry()):
                        inlayer.deleteFeature(feat.id())
                        feat.geometry().convertToMultiType()
                        inlayer.addFeature(feat)
                        
            for feat in inlayer.getFeatures(): #seleciona no carvas as features adiconadas 
                if box.contains(feat.geometry().boundingBox()):
                    for feat_2 in clean_shape.getFeatures():
                        if feat.geometry().equals(feat_2.geometry()):
                            inlayer.select(feat.id())