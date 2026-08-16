const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');

const SosAlert = sequelize.define('SosAlert', {
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
  latitude: {
    type: DataTypes.DECIMAL(10, 8),
    allowNull: false,
  },
  longitude: {
    type: DataTypes.DECIMAL(11, 8),
    allowNull: false,
  },
  locationUrl: {
    type: DataTypes.STRING,
    field: 'location_url',
  },
  status: {
    type: DataTypes.ENUM('active', 'resolved', 'false_alarm'),
    defaultValue: 'active',
  },
  message: {
    type: DataTypes.TEXT,
    defaultValue: 'SOS! I need help!',
  },
}, {
  tableName: 'sos_alerts',
  timestamps: true,
});

SosAlert.belongsTo(User, { foreignKey: 'user_id', as: 'user' });
User.hasMany(SosAlert, { foreignKey: 'user_id', as: 'sosAlerts' });

module.exports = SosAlert;
