import request from 'supertest';
import app from '../../src/app';

describe('Health Check API', () => {
    it('should return a 200 status and a message indicating the service is running', async () => {
        const response = await request(app).get('/health');
        expect(response.status).toBe(200);
        expect(response.body).toEqual({ message: 'Service is running' });
    });
});