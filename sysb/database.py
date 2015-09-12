# -*- coding: utf-8 -*-

import sqlite3
import logg


class ownbot(object):

    # Se crea la conexion y el cursor de la base de datos
    # Todo gira al rededor de esto!
    con = sqlite3.connect('db/userbot.db', check_same_thread=False)
    cur = con.cursor()
    __logg = logg.getLogger(__name__)
    __logg.info('Se aperturo la base de datos.')

    # Base de datos (Temporal, almacenada en la RAM)
    tmp = sqlite3.connect(':memory:', check_same_thread=False).cursor()

    # Excepciones
    Error = sqlite3.Error
    DatabaseError = sqlite3.DatabaseError
    DataError = sqlite3.DataError
    IntegrityError = sqlite3.IntegrityError
    InternalError = sqlite3.InternalError
    NotSupportedError = sqlite3.NotSupportedError
    OperationalError = sqlite3.OperationalError
    ProgrammingError = sqlite3.ProgrammingError
    InterfaceError = sqlite3.InterfaceError
    Warning = sqlite3.Warning  # lint:ok

    def create(self, table, values, INE=False, tmp=False, commit=True):
        """
        Crea una tabla en las bases de datos.
        Argumentos:
            table -- Nombre de la tabla a crear.
            values -- Valores que tendra la tabla.
            INE -- Solo se creara la tabla si no existe, valor booleano.
            tmp -- Booleano, que indica si la tabla a crear se realizara en la
                   base de datos temporal.
            commit -- Guardar los cambios efectuados en las base de datos,
                      de tipo booleano
        """

        self.exc('create table {0}{1} ({2})'.format(
            'if not exists ' if INE else '',
            table,
            values), tmp, commit)

    def delete(self, table, where='', tmp=False, commit=True):
        """
        Elimina uno o mas elementos de una tabla en las base de datos.
        Argumentos:
            table -- Tabla donde se eliminara el elemento.
            where -- Indica que objeto sera eliminado de las bases de datos.
            tmp -- Tipo booleano, indica si el comando a ejecutar se
                   realizara sobre la base de datos temporal.
            commit -- Guardar los cambios efectuados en las base de datos,
                      valor de tipo booleano, valor por default: True
        """
        self.exc('delete from {0}{1}'.format(table,
            ' where ' + where if where else ''), tmp, commit)

    def drop(self, tables, INE=False, tmp=False, commit=True):
        """
        Elimina una o mas tablas de las bases de datos.
        Argumentos:
            tables -- Tablas a eliminar de las bases de datos.
        """

        for table in tables:
            self.exc('drop table {0}{1}'.format(
                'if not exists ' if INE else '',
                table), tmp, commit)

    def exc(self, string, tmp=False, commit=True):
        """Efectua ejecuciones de comandos sobre la base de datos.
            Argumentos:
                string -- Cadena contenedora del comando a ejecutar.
                tmp -- Tipo booleano, indica si el comando a ejecutar se
                       realizara sobre la base de datos temporal.
                commit -- Guardar los cambios efectuados en las base de datos,
                          de tipo booleano, valor por default: True"""

        # Esto puede ser peligroso xD
        self.__logg.debug(
        "SQLite Shell ?> %s, args=(tmp=%s, commit=%s)" % (string, tmp, commit))

        if not tmp:
            self.cur.execute(string)
            if commit:
                self.con.commit()
        else:
            self.tmp.execute(string)

    def insert(self, table, element, values='', tmp=False, commit=True):
        """
        Inserta un elemento en una tabla de la base de datos.
        Argumentos:
            table -- Tabla donde se insertara el elemento.
            values -- valores de las tablas,
            elements -- Elementos a insertar
        """
        self.exc('insert into {}{} values ({})'.format(
            table,
            ' (%s)' % values if values else '', element), tmp, commit)

    def select(self, table, values, where='', tmp=False):
        """
        Selecciona uno o mas elementos de las base de datos y retorna su valor.
        Argumentos:
            table -- Nombre de la tabla a seleccionar.
            values -- Valores a seleccionar de la tabla.
            where --- Key optional
            tmp -- Booleano, que indica si el valor a seleccionar se realizara
                   en la base de datos temporal.
        """

        self.exc("select {0} from {1}{2}".format(
            values,
            table,
            ' where ' + where if where else ''), tmp, commit=False)

        return self.cur.fetchall()

    def update(self, table, value, where='', tmp=False, commit=True):
        """
        Actualiza un elemento de las bases de datos.
        Argumentos:
            table -- Nombre de la tabla donde se actualizara el elemento.
            value -- Elemento a setear.
            where -- Elemento especifico a setear.
        """

        self.exc('update {0} set {1}{2}'.format(table, value,
            ' where ' + where if where else ''), tmp, commit)


