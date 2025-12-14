import { readFileSync } from 'fs';
import { parse } from 'papaparse';

interface ICDMapping {
    icd9: string;
    icd10: string;
}

const icdMapping: ICDMapping[] = [];

export function loadICDMappings(filePath: string): void {
    const fileContent = readFileSync(filePath, 'utf-8');
    const parsedData = parse(fileContent, { header: true });

    parsedData.data.forEach((row: any) => {
        icdMapping.push({
            icd9: row.icd9,
            icd10: row.icd10,
        });
    });
}

export function mapICD9ToICD10(icd9Code: string): string | null {
    const mapping = icdMapping.find(mapping => mapping.icd9 === icd9Code);
    return mapping ? mapping.icd10 : null;
}