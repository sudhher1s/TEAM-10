import { readFileSync } from 'fs';
import { join } from 'path';

const ICD10_FILE_PATH = join(__dirname, '../data/reference/icd10cm.csv');
const CPT_FILE_PATH = join(__dirname, '../data/reference/cpt.csv');
const SNOMED_FILE_PATH = join(__dirname, '../data/reference/snomed.csv');

interface Terminology {
    code: string;
    description: string;
    category: string;
}

class TerminologyService {
    private icd10Terms: Terminology[];
    private cptTerms: Terminology[];
    private snomedTerms: Terminology[];

    constructor() {
        this.icd10Terms = this.loadTerminology(ICD10_FILE_PATH);
        this.cptTerms = this.loadTerminology(CPT_FILE_PATH);
        this.snomedTerms = this.loadTerminology(SNOMED_FILE_PATH);
    }

    private loadTerminology(filePath: string): Terminology[] {
        const data = readFileSync(filePath, 'utf-8');
        const lines = data.split('\n').slice(1); // Skip header
        return lines.map(line => {
            const [code, description, category] = line.split(',');
            return { code, description, category };
        }).filter(term => term.code && term.description);
    }

    public getICD10Terms(): Terminology[] {
        return this.icd10Terms;
    }

    public getCPTTerms(): Terminology[] {
        return this.cptTerms;
    }

    public getSNOMEDTerms(): Terminology[] {
        return this.snomedTerms;
    }

    public findTermByCode(code: string): Terminology | undefined {
        return [...this.icd10Terms, ...this.cptTerms, ...this.snomedTerms].find(term => term.code === code);
    }
}

export default new TerminologyService();