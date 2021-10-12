"""
Package for a database of Scattering Length Density data (SLD) for neutron
and x-ray scattering.
The query to the DB includes recalculation of SLD for needed radiation.

Part of ORSO initiative, see: https://www.reflectometry.org/

Contributers:
    Artur Glavic <artur.glavic@psi.ch>
"""

__version__='1.0 beta3'

from .database import SLDDB
from .dbconfig import DB_FILE
from .webapi import SLD_API

api=SLD_API()
