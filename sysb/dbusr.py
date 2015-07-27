# -*- coding: utf-8 -*-

import database


class usr(database.ownbot):

    def __init__(self):
        # Se crea la tabla "user" en la base de datos si no existe
        self.create('user', "uuid key text, nickname text, password text", True)
        # Se crea la tabla "status" en la base de datos temporal si no existe
        self.create('status',
            """
            uuid key text,
            username text,
            server text,
            status text
            """, INE=True, tmp=True)

    def auth(self, sob, user, passwd, mask):
        """Autentica al usuario, como el propietario de la cuenta, se comprueba
           si la contraseña y usuario son validos, y retorna valores booleanos.
           Argumentos:
               SOB -- "Socket Object - BOT"
               user -- Usuario que se debe encontrar registrado.
               passwd -- Contraseña, cadena contenedora de la contraseña."""

        if self.registered(user) is True:
            if self.info(user, 'password') is self.hash(passwd):
                turn.request(sob, mask.nick, id(user), com='whois', event=330)
                self.check(sob, turn.get(id(user)))

    def register(self, user, passwd):
        """Registrar usuario en la base de datos
           Argumentos:
               user -- Usuario a registrar, este debe ser unico de existir otro
                       igual se arroja una excepcion.
               passwd -- Contraseña del usuario esta se usara para autenticarse
                         como el propietario del usuario"""

        if not self.registered(user):
            self.exc("""
                insert into cuser (
                    uuid,
                    username,
                    password)
                values(
                    '%s',
                    '%s',
                    '%s')""" % (self.uuid(user), user, self.hash(passwd)))