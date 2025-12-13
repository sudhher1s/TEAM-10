import { Request, Response, NextFunction } from 'express';

export const logRequest = (req: Request, _res: Response, next: NextFunction) => {
  console.log(`[AUDIT][REQUEST] ${req.method} ${req.originalUrl}`);
  next();
};

export const logResponse = (_req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[AUDIT][RESPONSE] status=${res.statusCode} durationMs=${duration}`);
  });
  next();
};
