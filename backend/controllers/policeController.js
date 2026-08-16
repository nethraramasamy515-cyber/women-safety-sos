const { PoliceStation } = require('../models');
const { Op } = require('sequelize');

const HELPLINES = [
  { name: 'Women Helpline', number: '1091', description: '24x7 Women in Distress' },
  { name: 'Police', number: '100', description: 'Police Emergency' },
  { name: 'Ambulance', number: '108', description: 'Medical Emergency' },
  { name: 'Fire Brigade', number: '101', description: 'Fire Emergency' },
  { name: 'Emergency', number: '112', description: 'Universal Emergency Number' },
  { name: 'Child Helpline', number: '1098', description: 'Child in Distress' },
  { name: 'Anti Poison', number: '1066', description: 'Poison Information Center' },
  { name: 'Disaster Management', number: '108', description: 'Disaster Response' },
  { name: 'Nirbhaya Helpline', number: '181', description: 'Women Safety Helpline' },
  { name: 'National Commission for Women', number: '7827-170-170', description: 'NCW Complaint' },
];

exports.getPoliceStations = async (req, res) => {
  try {
    const { latitude, longitude, radius } = req.query;

    let stations;

    if (latitude && longitude) {
      const lat = parseFloat(latitude);
      const lon = parseFloat(longitude);
      const rad = parseFloat(radius) || 10;

      const latMin = lat - (rad / 111);
      const latMax = lat + (rad / 111);
      const lonMin = lon - (rad / (111 * Math.cos((lat * Math.PI) / 180)));
      const lonMax = lon + (rad / (111 * Math.cos((lat * Math.PI) / 180)));

      stations = await PoliceStation.findAll({
        where: {
          latitude: { [Op.between]: [latMin, latMax] },
          longitude: { [Op.between]: [lonMin, lonMax] },
        },
      });
    } else {
      stations = await PoliceStation.findAll();
    }

    res.json({ stations });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

exports.getHelplines = (req, res) => {
  res.json({ helplines: HELPLINES });
};
