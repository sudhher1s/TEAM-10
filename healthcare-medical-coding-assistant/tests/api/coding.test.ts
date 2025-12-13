import request from 'supertest';
import app from '../../src/app'; // Adjust the import based on your app's structure

describe('Coding API', () => {
    it('should return a 200 status for the coding prediction endpoint', async () => {
        const response = await request(app)
            .post('/api/coding/predict') // Adjust the endpoint based on your routing
            .send({
                clinicalNote: 'Patient has a history of hypertension and diabetes.'
            });
        
        expect(response.status).toBe(200);
        expect(response.body).toHaveProperty('icdCode');
    });

    it('should return a 400 status for invalid input', async () => {
        const response = await request(app)
            .post('/api/coding/predict')
            .send({
                clinicalNote: '' // Sending an empty clinical note
            });
        
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('error');
    });
});