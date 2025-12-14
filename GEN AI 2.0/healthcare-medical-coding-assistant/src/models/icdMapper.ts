import { ICDMapping } from '../types/index';

const icdMappings: ICDMapping[] = [
    { icd9: '001', icd10: 'A00' },
    { icd9: '002', icd10: 'A01' },
    // Add more mappings as needed
];

export const mapICD9ToICD10 = (icd9Code: string): string | null => {
    const mapping = icdMappings.find(mapping => mapping.icd9 === icd9Code);
    return mapping ? mapping.icd10 : null;
};