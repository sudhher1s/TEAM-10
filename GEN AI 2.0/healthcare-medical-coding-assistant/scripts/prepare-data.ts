import fs from 'fs';
import path from 'path';
import csvParser from 'csv-parser';

const rawDataDir = path.join(__dirname, '../data/raw');
const processedDataDir = path.join(__dirname, '../data/processed');

// Function to prepare claims data
const prepareClaimsData = () => {
    const claimsData = [];
    fs.createReadStream(path.join(rawDataDir, 'claims.csv'))
        .pipe(csvParser())
        .on('data', (row) => {
            claimsData.push(row);
        })
        .on('end', () => {
            // Process claims data and save to processed directory
            const processedClaimsData = claimsData.map(claim => ({
                id: claim.id,
                patientId: claim.patient_id,
                diagnosis: claim.diagnosis,
                amount: claim.amount,
            }));
            fs.writeFileSync(path.join(processedDataDir, 'claims_processed.json'), JSON.stringify(processedClaimsData, null, 2));
            console.log('Claims data processed and saved.');
        });
};

// Function to prepare encounters data
const prepareEncountersData = () => {
    const encountersData = [];
    fs.createReadStream(path.join(rawDataDir, 'encounters.csv'))
        .pipe(csvParser())
        .on('data', (row) => {
            encountersData.push(row);
        })
        .on('end', () => {
            // Process encounters data and save to processed directory
            const processedEncountersData = encountersData.map(encounter => ({
                encounterId: encounter.encounter_id,
                patientId: encounter.patient_id,
                visitDate: encounter.visit_date,
                reason: encounter.reason,
            }));
            fs.writeFileSync(path.join(processedDataDir, 'encounters_processed.json'), JSON.stringify(processedEncountersData, null, 2));
            console.log('Encounters data processed and saved.');
        });
};

// Function to prepare clinical notes data
const prepareNotesData = () => {
    const notesData = [];
    const notesFilePath = path.join(rawDataDir, 'notes.jsonl');
    const notesStream = fs.createReadStream(notesFilePath, { encoding: 'utf8' });

    notesStream.on('data', (chunk) => {
        chunk.split('\n').forEach(line => {
            if (line) {
                notesData.push(JSON.parse(line));
            }
        });
    });

    notesStream.on('end', () => {
        // Process notes data and save to processed directory
        fs.writeFileSync(path.join(processedDataDir, 'notes_processed.json'), JSON.stringify(notesData, null, 2));
        console.log('Clinical notes data processed and saved.');
    });
};

// Main function to prepare all data
const prepareData = () => {
    prepareClaimsData();
    prepareEncountersData();
    prepareNotesData();
};

// Execute the data preparation
prepareData();