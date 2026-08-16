const express = require('express');
const router = express.Router();
const { triggerAlert, getHistory, resolveAlert, getActiveAlerts } = require('../controllers/sosController');
const { auth } = require('../middleware/auth');

router.use(auth);

router.post('/trigger', triggerAlert);
router.get('/history', getHistory);
router.get('/active', getActiveAlerts);
router.put('/:id/resolve', resolveAlert);

module.exports = router;
