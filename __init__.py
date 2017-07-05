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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RepairGeometry class from file RepairGeometry.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .repair_geometry import RepairGeometry
    return RepairGeometry(iface)
