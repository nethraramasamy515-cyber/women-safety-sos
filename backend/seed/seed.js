const { PoliceStation } = require('../models');
const sequelize = require('../config/db');

const policeStations = [
  { name: 'Central Police Station', address: 'MG Road, City Center', latitude: 28.6139, longitude: 77.2090, phone: '011-23360451' },
  { name: 'Women Safety Wing', address: 'Connaught Place, New Delhi', latitude: 28.6315, longitude: 77.2167, phone: '011-23342764' },
  { name: 'North District Police HQ', address: 'Kamla Nagar, Delhi', latitude: 28.6809, longitude: 77.1917, phone: '011-27620350' },
  { name: 'South Police Station', address: 'Saket, New Delhi', latitude: 28.5220, longitude: 77.2098, phone: '011-26513479' },
  { name: 'East District Police', address: 'Preet Vihar, Delhi', latitude: 28.6424, longitude: 77.2964, phone: '011-22443477' },
  { name: 'West District Police', address: 'Rajouri Garden, Delhi', latitude: 28.6492, longitude: 77.1231, phone: '011-25103333' },
  { name: 'Cyber Crime Police Station', address: 'ITO, New Delhi', latitude: 28.6284, longitude: 77.2412, phone: '011-23379181' },
  { name: 'Traffic Police HQ', address: 'Pragati Maidan, Delhi', latitude: 28.6167, longitude: 77.2440, phone: '011-23388324' },
  { name: 'Airport Police Station', address: 'IGI Airport, New Delhi', latitude: 28.5562, longitude: 77.1000, phone: '011-25665281' },
  { name: 'Railway Police Station', address: 'New Delhi Railway Station', latitude: 28.6448, longitude: 77.2167, phone: '011-23344765' },
];

const seedDatabase = async () => {
  try {
    await sequelize.authenticate();
    console.log('Connected to database');

    await sequelize.sync({ alter: true });

    const existingCount = await PoliceStation.count();
    if (existingCount > 0) {
      console.log('Police stations already seeded. Skipping.');
    } else {
      await PoliceStation.bulkCreate(policeStations);
      console.log(`Seeded ${policeStations.length} police stations`);
    }

    console.log('Database seeding complete');
    process.exit(0);
  } catch (error) {
    console.error('Seeding error:', error);
    process.exit(1);
  }
};

seedDatabase();
