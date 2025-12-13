import { preprocessClinicalNotes } from '../../src/pipelines/preprocessing';
import { expect } from 'chai';

describe('Preprocessing Pipeline', () => {
    it('should preprocess clinical notes correctly', () => {
        const inputNotes = [
            { note: "Patient has a cough and fever.", patientId: 1 },
            { note: "Follow-up for diabetes management.", patientId: 2 }
        ];
        
        const expectedOutput = [
            { processedNote: "Patient has cough fever", patientId: 1 },
            { processedNote: "Follow-up diabetes management", patientId: 2 }
        ];

        const result = preprocessClinicalNotes(inputNotes);
        expect(result).to.deep.equal(expectedOutput);
    });

    it('should handle empty input', () => {
        const inputNotes = [];
        const expectedOutput = [];
        
        const result = preprocessClinicalNotes(inputNotes);
        expect(result).to.deep.equal(expectedOutput);
    });

    it('should throw an error for invalid input format', () => {
        const inputNotes = "Invalid input";

        expect(() => preprocessClinicalNotes(inputNotes)).to.throw(Error, 'Invalid input format');
    });
});