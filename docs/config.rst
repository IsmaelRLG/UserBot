=============
base de datos
=============

La base de datos se encuentra bajo SQLite3, la tabla de configuraciones se encuentra bajo el nombre de ``core``
el nombre de la clase es ``config``, se puede encontrar una variable con una clase ya instanciada bajo ``core``
esta clase poseé ciertos atributos, los cuales la mayoria son heredados de su clase padre ``ownbot`` que se
puede encontrar en el modulo :doc:`database<database>`. La clase ``config`` tiene la capacidad de guardar objetos
python, ya que estos son serializados mediante pickle (cPickle para mayor velocidad) y guardados en la base de
datos como texto plano, y al hacer la consulta, estos son cargados y retorna el objeto que se haya guardado

class config
============

Esta es la que se menciono anteriormente, como ya se dijo algunos de sus atributos son heredados de ``ownbot``
aunque aquí mencionaremos los metodos propios de esta clase:

.. table:: Metodos de ownbot
  ===============  ====================================================
      metodo           Descripción
  ===============  ====================================================
   ``addconfig``   Guarda un objeto en la base de datos.
                   Argumentos::
                       name -- nombre del objeto (usado para consultas)
                       _object -- el objeto a guardar

   ``delconfig``   Elimina un objeto guardado en la base de datos, en
                   caso de que el objeto no exista se arroja una excep-
                   ción de tipo ``sqlite3.OperationalError``
                   Argumentos::
                       name -- nombre del objeto

   ``obtconfig``   Realiza una consulta de un objeto que este guardado
                   en la base de datos, en caso de que el objeto no
                   exista retorna ``None``, de existir retorna el 
                   objeto.
                   Argumentos::
                       name -- nombre del objeto

   ``upconfig``    Actualiza un objeto que haya sido guardado
                   Argumentos::
                       name -- nombre del objeto
                       _object -- el nuevo objeto
  ===============  ====================================================
