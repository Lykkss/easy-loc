// /mongo-init.js
db = db.getSiblingDB('easyloc');

// Création des collections
db.createCollection('Customer');
db.createCollection('Vehicle');

// Création d’un user “user” avec droits readWrite sur la base easyloc
db.createUser({
  user: 'user',
  pwd: 'password',
  roles: [{ role: 'readWrite', db: 'easyloc' }]
});
