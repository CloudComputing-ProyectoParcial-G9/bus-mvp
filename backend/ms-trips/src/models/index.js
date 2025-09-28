const Route = require('./Route');
const Trip = require('./Trip');

// TEMPORALMENTE COMENTAMOS LAS RELACIONES PARA QUE FUNCIONE LA APP
// TODO: Arreglar las relaciones después

// // Una ruta puede tener muchos viajes
// Route.hasMany(Trip, {
//   foreignKey: 'routeId',
//   sourceKey: 'routeId',
//   as: 'trips',
//   onDelete: 'RESTRICT',
//   onUpdate: 'CASCADE'
// });

// // Un viaje pertenece a una ruta
// Trip.belongsTo(Route, {
//   foreignKey: 'routeId',
//   targetKey: 'routeId',
//   as: 'route',
//   onDelete: 'RESTRICT',
//   onUpdate: 'CASCADE'
// });

module.exports = {
  Route,
  Trip
};
