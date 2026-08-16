const { EmergencyContact } = require('../models');

exports.getContacts = async (req, res) => {
  try {
    const contacts = await EmergencyContact.findAll({
      where: { userId: req.userId },
      order: [['is_primary', 'DESC'], ['name', 'ASC']],
    });
    res.json({ contacts });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.addContact = async (req, res) => {
  try {
    const { name, phone, relationship, isPrimary } = req.body;

    if (!name || !phone) {
      return res.status(400).json({ message: 'Name and phone are required' });
    }

    if (isPrimary) {
      await EmergencyContact.update(
        { isPrimary: false },
        { where: { userId: req.userId, isPrimary: true } }
      );
    }

    const contact = await EmergencyContact.create({
      userId: req.userId,
      name,
      phone,
      relationship: relationship || 'Other',
      isPrimary: isPrimary || false,
    });

    res.status(201).json({ contact });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.updateContact = async (req, res) => {
  try {
    const { id } = req.params;
    const { name, phone, relationship, isPrimary } = req.body;

    const contact = await EmergencyContact.findOne({
      where: { id, userId: req.userId },
    });

    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    if (isPrimary) {
      await EmergencyContact.update(
        { isPrimary: false },
        { where: { userId: req.userId, isPrimary: true } }
      );
    }

    if (name) contact.name = name;
    if (phone) contact.phone = phone;
    if (relationship) contact.relationship = relationship;
    if (isPrimary !== undefined) contact.isPrimary = isPrimary;

    await contact.save();
    res.json({ contact });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.deleteContact = async (req, res) => {
  try {
    const { id } = req.params;

    const contact = await EmergencyContact.findOne({
      where: { id, userId: req.userId },
    });

    if (!contact) {
      return res.status(404).json({ message: 'Contact not found' });
    }

    await contact.destroy();
    res.json({ message: 'Contact deleted' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};
