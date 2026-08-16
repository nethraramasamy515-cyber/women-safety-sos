const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const SosAlert = require('./SosAlert');
const EmergencyContact = require('./EmergencyContact');

const AlertRecipient = sequelize.define('AlertRecipient', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  alertId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    field: 'alert_id',
  },
  contactId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    field: 'contact_id',
  },
  status: {
    type: DataTypes.ENUM('notified', 'failed'),
    defaultValue: 'notified',
  },
  notifiedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
    field: 'notified_at',
  },
}, {
  tableName: 'alert_recipients',
  timestamps: false,
});

AlertRecipient.belongsTo(SosAlert, { foreignKey: 'alert_id', as: 'alert' });
AlertRecipient.belongsTo(EmergencyContact, { foreignKey: 'contact_id', as: 'contact' });
SosAlert.hasMany(AlertRecipient, { foreignKey: 'alert_id', as: 'recipients' });

module.exports = AlertRecipient;
