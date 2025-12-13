import { readFileSync } from 'fs';
import { parse } from 'papaparse';

interface ClinicalNote {
    id: string;
    text: string;
}

export function loadClinicalNotes(filePath: string): ClinicalNote[] {
    const fileContent = readFileSync(filePath, 'utf-8');
    const parsedData = parse(fileContent, { header: true });
    return parsedData.data as ClinicalNote[];
}

export function preprocessClinicalNotes(notes: ClinicalNote[]): string[] {
    return notes.map(note => {
        // Basic preprocessing: lowercasing and trimming
        return note.text.toLowerCase().trim();
    });
}

export function filterEmptyNotes(notes: string[]): string[] {
    return notes.filter(note => note.length > 0);
}