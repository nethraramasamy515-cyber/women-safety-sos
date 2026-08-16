const { User, SosAlert, EmergencyContact, AlertRecipient, IncidentLog } = require('../models');
const { Op } = require('sequelize');
const sequelize = require('../config/db');

exports.getDashboardStats = async (req, res) => {
  try {
    const totalUsers = await User.count();
    const totalAlerts = await SosAlert.count();
    const activeAlerts = await SosAlert.count({ where: { status: 'active' } });
    const resolvedAlerts = await SosAlert.count({ where: { status: 'resolved' } });
    const falseAlarms = await SosAlert.count({ where: { status: 'false_alarm' } });
    const totalContacts = await EmergencyContact.count();

    const recentAlerts = await SosAlert.findAll({
      include: [{ model: User, as: 'user', attributes: ['id', 'name', 'email', 'phone'] }],
      order: [['createdAt', 'DESC']],
      limit: 10,
    });

    const alertsByDay = await SosAlert.findAll({
      attributes: [
        [sequelize.fn('DATE', sequelize.col('createdAt')), 'date'],
        [sequelize.fn('COUNT', sequelize.col('id')), 'count'],
      ],
      group: [sequelize.fn('DATE', sequelize.col('createdAt'))],
      order: [[sequelize.fn('DATE', sequelize.col('createdAt')), 'DESC']],
      limit: 30,
    });

    res.json({
      stats: {
        totalUsers,
        totalAlerts,
        activeAlerts,
        resolvedAlerts,
        falseAlarms,
        totalContacts,
      },
      recentAlerts,
      alertsByDay,
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.getAllUsers = async (req, res) => {
  try {
    const users = await User.findAll({
      attributes: { exclude: ['password'] },
      include: [{ model: SosAlert, as: 'sosAlerts', attributes: ['id'] }],
      order: [['createdAt', 'DESC']],
    });

    const usersWithCount = users.map(u => {
      const obj = u.toJSON();
      obj.alertCount = obj.sosAlerts ? obj.sosAlerts.length : 0;
      delete obj.sosAlerts;
      return obj;
    });

    res.json({ users: usersWithCount });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.getAllAlerts = async (req, res) => {
  try {
    const { status } = req.query;
    const where = status ? { status } : {};

    const alerts = await SosAlert.findAll({
      where,
      include: [
        { model: User, as: 'user', attributes: ['id', 'name', 'email', 'phone'] },
        {
          model: AlertRecipient,
          as: 'recipients',
          include: [{ model: EmergencyContact, as: 'contact' }],
        },
      ],
      order: [['createdAt', 'DESC']],
    });
    res.json({ alerts });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.updateAlertStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const alert = await SosAlert.findByPk(id);
    if (!alert) {
      return res.status(404).json({ message: 'Alert not found' });
    }

    alert.status = status;
    await alert.save();

    res.json({ alert });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};
