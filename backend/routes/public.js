const express = require('express');
const router = express.Router();
const { getPoliceStations, getHelplines } = require('../controllers/policeController');

router.get('/police-stations', getPoliceStations);
router.get('/helplines', getHelplines);

module.exports = router;
