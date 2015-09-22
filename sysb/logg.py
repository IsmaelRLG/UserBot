# -*- coding: utf-8 -*-
import coloredlogs

from logging import *


def logg(level=DEBUG):
    coloredlogs.install(level)
    getLogger(__name__).info('Los logs se han activado. Nivel: ' + str(level))


def set_level(level):
    coloredlogs.set_level(level)
    getLogger(__name__).info('Nivel de logs actualizado: ' + str(level))