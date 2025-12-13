import { Router } from 'express';
import { logRequest, logResponse } from '../../middleware/auditMiddleware';

const router = Router();

// Middleware to log requests and responses
router.use(logRequest);
router.use(logResponse);

// Example route for auditing
router.get('/audit', (req, res) => {
    res.status(200).json({ message: 'Audit log retrieved successfully' });
});

export default router;