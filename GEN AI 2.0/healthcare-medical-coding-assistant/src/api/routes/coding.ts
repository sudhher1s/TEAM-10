import { Router } from 'express';
import { validateCodingRequest } from '../middleware/validation';
import { authenticate } from '../middleware/auth';
import { predictCoding } from '../../services/codingEngine';

const router = Router();

// Route for predicting medical coding based on clinical notes
router.post('/predict', authenticate, validateCodingRequest, async (req, res) => {
    try {
        const { notes } = req.body;
        const result = await predictCoding(notes);
        res.status(200).json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

export default router;