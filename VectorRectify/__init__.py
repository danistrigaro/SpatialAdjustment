# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SpatialAdjustment
                                 A QGIS plugin
 A tool to adjust vector layers
                             -------------------
        begin                : 2015-05-21
        copyright            : (C) 2015 by Daniele Strigaro
        email                : daniele.strigaro@gmail.com
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
    """Load SpatialAdjustment class from file SpatialAdjustment.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vector_rectify import VectorRectify
    return VectorRectify(iface)
