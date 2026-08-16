const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');

const EmergencyContact = sequelize.define('EmergencyContact', {
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
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  phone: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  relationship: {
    type: DataTypes.STRING,
    defaultValue: 'Other',
  },
  isPrimary: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
    field: 'is_primary',
  },
}, {
  tableName: 'emergency_contacts',
  timestamps: true,
});

EmergencyContact.belongsTo(User, { foreignKey: 'user_id', as: 'user' });
User.hasMany(EmergencyContact, { foreignKey: 'user_id', as: 'emergencyContacts' });

module.exports = EmergencyContact;
