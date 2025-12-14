import { codingEngine } from '../../src/services/codingEngine';

describe('Coding Engine Service', () => {
    it('should map clinical notes to ICD-10 codes', async () => {
        const clinicalNote = "Patient has a diagnosis of diabetes mellitus.";
        const expectedCode = "E11"; // Example expected ICD-10 code for diabetes

        const result = await codingEngine.mapToICD10(clinicalNote);
        expect(result).toEqual(expectedCode);
    });

    it('should return an error for invalid input', async () => {
        const clinicalNote = ""; // Invalid input

        await expect(codingEngine.mapToICD10(clinicalNote)).rejects.toThrow('Invalid clinical note');
    });

    it('should handle multiple diagnoses in clinical notes', async () => {
        const clinicalNote = "Patient has hypertension and diabetes mellitus.";
        const expectedCodes = ["I10", "E11"]; // Example expected ICD-10 codes

        const result = await codingEngine.mapToICD10(clinicalNote);
        expect(result).toEqual(expect.arrayContaining(expectedCodes));
    });
});