const { SosAlert, EmergencyContact, AlertRecipient, IncidentLog, User } = require('../models');
const { Op } = require('sequelize');

exports.triggerAlert = async (req, res) => {
  try {
    const { latitude, longitude, message } = req.body;

    if (!latitude || !longitude) {
      return res.status(400).json({ message: 'Location coordinates are required' });
    }

    const locationUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

    const alert = await SosAlert.create({
      userId: req.userId,
      latitude,
      longitude,
      locationUrl,
      message: message || 'SOS! I need help!',
    });

    const contacts = await EmergencyContact.findAll({
      where: { userId: req.userId },
    });

    const recipients = [];
    for (const contact of contacts) {
      const recipient = await AlertRecipient.create({
        alertId: alert.id,
        contactId: contact.id,
        status: 'notified',
      });
      recipients.push(recipient);
    }

    await IncidentLog.create({
      userId: req.userId,
      alertId: alert.id,
      action: 'SOS_TRIGGERED',
      description: `SOS alert triggered at location (${latitude}, ${longitude})`,
    });

    const fullAlert = await SosAlert.findByPk(alert.id, {
      include: [
        {
          model: AlertRecipient,
          as: 'recipients',
          include: [{ model: EmergencyContact, as: 'contact' }],
        },
      ],
    });

    res.status(201).json({
      alert: fullAlert,
      contactsNotified: contacts.length,
      message: 'SOS alert triggered. Emergency contacts have been notified.',
    });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.getHistory = async (req, res) => {
  try {
    const alerts = await SosAlert.findAll({
      where: { userId: req.userId },
      include: [
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

exports.resolveAlert = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const alert = await SosAlert.findOne({
      where: { id, userId: req.userId },
    });

    if (!alert) {
      return res.status(404).json({ message: 'Alert not found' });
    }

    alert.status = status || 'resolved';
    await alert.save();

    await IncidentLog.create({
      userId: req.userId,
      alertId: alert.id,
      action: 'ALERT_RESOLVED',
      description: `Alert resolved with status: ${alert.status}`,
    });

    res.json({ alert });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.getActiveAlerts = async (req, res) => {
  try {
    const alerts = await SosAlert.findAll({
      where: { userId: req.userId, status: 'active' },
      include: [
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
