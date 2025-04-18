db = db.getSiblingDB('easyloc');

// Création des collections si elles n'existent pas
db.createCollection('Customer');
db.createCollection('Vehicle');

// Création d'un utilisateur pour l'authentification
db.createUser({
  user: 'user', 
  pwd: 'password', 
  roles: [
    { role: 'readWrite', db: 'easyloc' }
  ]
});
