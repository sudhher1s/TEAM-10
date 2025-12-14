import { Request, Response, NextFunction } from 'express';
import { body, validationResult } from 'express-validator';

// Middleware for validating incoming requests
export const validateCodingRequest = [
    body('clinicalNotes').isString().withMessage('Clinical notes must be a string'),
    body('patientId').isNumeric().withMessage('Patient ID must be a number'),
    body('codingType').isIn(['ICD-10', 'CPT']).withMessage('Coding type must be either ICD-10 or CPT'),
    (req: Request, res: Response, next: NextFunction) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }
        next();
    }
];