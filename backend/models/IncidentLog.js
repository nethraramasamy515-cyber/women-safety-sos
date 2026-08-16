const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');
const SosAlert = require('./SosAlert');

const IncidentLog = sequelize.define('IncidentLog', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  userId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    field: 'user_id',
  },
  alertId: {
    type: DataTypes.INTEGER,
    defaultValue: null,
    field: 'alert_id',
  },
  action: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  description: {
    type: DataTypes.TEXT,
    defaultValue: null,
  },
}, {
  tableName: 'incident_logs',
  timestamps: true,
});

IncidentLog.belongsTo(User, { foreignKey: 'user_id', as: 'user' });
IncidentLog.belongsTo(SosAlert, { foreignKey: 'alert_id', as: 'alert' });
User.hasMany(IncidentLog, { foreignKey: 'user_id', as: 'incidentLogs' });

module.exports = IncidentLog;
