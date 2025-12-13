import { Router } from 'express';
import codingRoutes from './coding';
import healthRoutes from './health';
import auditRoutes from './audit';

const router = Router();

router.use('/', healthRoutes);
router.use('/', codingRoutes);
router.use('/', auditRoutes);

export default router;
