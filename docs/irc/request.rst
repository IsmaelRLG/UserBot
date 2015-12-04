=====================
Solicitar información
=====================

Se puede obtener cierta informacion del servidor de la respuesta de whois,
who, etc, esta informacion es procesada y retornada en codigo util para python.

class request
=============

clase madre para todas las solicitudes, esta clase debe ser heredada, y debe
cumplir con una estricta estructura, se debe definir la funcion que hara la
solicitud bajo el nombre de "execute", y el nombre de la funcion la cual
procesara el resultado debe ser "func_reqs", esta funcion debe solicitar los 
argumentos:
    * name -- contiene el nombre del evento procesado, el nombre por default
        es el nombre de una variable del modulo "ircregex"
    * group -- es el metodo "group" de un resultado de una expresion regular
        los grupos estan definidos por nombres, para consultar los nombres
        definidos revise manualmente el modulo "ircregex" y busque el nombre
        del evento y podra identificar los nombres de los grupos.

