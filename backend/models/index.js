const sequelize = require('../config/db');
const User = require('./User');
const EmergencyContact = require('./EmergencyContact');
const SosAlert = require('./SosAlert');
const AlertRecipient = require('./AlertRecipient');
const IncidentLog = require('./IncidentLog');
const PoliceStation = require('./PoliceStation');

module.exports = {
  sequelize,
  User,
  EmergencyContact,
  SosAlert,
  AlertRecipient,
  IncidentLog,
  PoliceStation,
};
