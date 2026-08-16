const express = require('express');
const router = express.Router();
const { getDashboardStats, getAllUsers, getAllAlerts, updateAlertStatus } = require('../controllers/adminController');
const { auth, adminAuth } = require('../middleware/auth');

router.use(auth, adminAuth);

router.get('/dashboard', getDashboardStats);
router.get('/users', getAllUsers);
router.get('/alerts', getAllAlerts);
router.put('/alerts/:id', updateAlertStatus);

module.exports = router;
