const { Sequelize } = require('sequelize');
require('dotenv').config();

let sequelize;

const dbUrl = process.env.MYSQL_ADDON_URI || process.env.DATABASE_URL || process.env.CC_MYSQL_URL;

if (dbUrl) {
  sequelize = new Sequelize(dbUrl, {
    dialect: 'mysql',
    logging: false,
    dialectOptions: {
      ssl: { rejectUnauthorized: true },
    },
    pool: { max: 10, min: 0, acquire: 30000, idle: 10000 },
  });
} else {
  sequelize = new Sequelize(
    process.env.DB_NAME || 'women_safety',
    process.env.DB_USER || 'root',
    process.env.DB_PASS || '',
    {
      host: process.env.DB_HOST || 'localhost',
      dialect: 'mysql',
      logging: false,
      pool: { max: 10, min: 0, acquire: 30000, idle: 10000 },
    }
  );
}

module.exports = sequelize;
