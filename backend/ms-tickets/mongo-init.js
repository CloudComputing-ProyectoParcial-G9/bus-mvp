// Script de inicialización para MongoDB
// Este script crea el usuario tickets_user en la base de datos tickets_db

// Cambiamos a la base de datos tickets_db
db = db.getSiblingDB('tickets_db');

// Creamos el usuario con permisos de lectura y escritura en la base de datos
db.createUser({
  user: 'tickets_user',
  pwd: 'tickets_password',
  roles: [
    {
      role: 'readWrite',
      db: 'tickets_db'
    }
  ]
});

// Creamos una colección inicial para asegurar que la base de datos existe
db.createCollection('tickets');

print('Usuario tickets_user creado exitosamente en la base de datos tickets_db');