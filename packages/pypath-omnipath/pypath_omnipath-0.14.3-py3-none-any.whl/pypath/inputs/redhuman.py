#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  This file is part of the `pypath` python module
#
#  Copyright
#  2014-2022
#  EMBL, EMBL-EBI, Uniklinik RWTH Aachen, Heidelberg University
#
#  Authors: Dénes Türei (turei.denes@gmail.com)
#           Nicolàs Palacio
#           Olga Ivanova
#           Sebastian Lobentanzer
#           Ahmet Rifaioglu
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  Website: http://pypath.omnipathdb.org/
#

import pypath.resources.urls as urls
import pypath.share.curl as curl
import pypath.inputs.rdata as rdata


def redhuman_download():
    """
    https://www.nature.com/articles/s41467-020-16549-2
    https://github.com/saezlab/ocean/tree/master/data
    """

    url = urls.urls['redhuman']['url']
    c = curl.Curl(url, silent = False, large = True)
    rdata_path = c.fileobj.name
    c.fileobj.close()

    rdata_parsed = rdata.rdata.parser.parse_file(rdata_path)
    rdata_converted = rdata.rdata.conversion.convert(rdata_parsed)

    return rdata_converted['recon2_redhuman']
