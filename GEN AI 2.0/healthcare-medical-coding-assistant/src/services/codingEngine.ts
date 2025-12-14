import { ICD10Code, ClinicalNote } from '../types';
import { fetchICD10Codes } from '../models/icdMapper';
import { preprocessNote } from '../pipelines/preprocessing';
import { postprocessOutput } from '../pipelines/postprocessing';

class CodingEngine {
    private icd10Codes: ICD10Code[];

    constructor() {
        this.icd10Codes = fetchICD10Codes();
    }

    public async mapClinicalNoteToICD10(note: ClinicalNote): Promise<string[]> {
        const processedNote = preprocessNote(note);
        const mappedCodes = this.performMapping(processedNote);
        return postprocessOutput(mappedCodes);
    }

    private performMapping(note: string): string[] {
        // Logic to map the clinical note to ICD-10 codes
        const matchedCodes: string[] = [];
        
        this.icd10Codes.forEach(code => {
            if (this.isMatch(note, code.description)) {
                matchedCodes.push(code.code);
            }
        });

        return matchedCodes;
    }

    private isMatch(note: string, description: string): boolean {
        // Simple matching logic (can be improved with NLP techniques)
        return note.toLowerCase().includes(description.toLowerCase());
    }
}

export default new CodingEngine();