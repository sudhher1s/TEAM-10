import fs from 'fs';
import path from 'path';
import { preprocessData } from '../pipelines/preprocessing';
import { trainModel } from '../services/codingEngine';
import { evaluateModel } from '../scripts/evaluate';

const trainingDataPath = path.join(__dirname, '../data/processed/training.tsv');
const evaluationDataPath = path.join(__dirname, '../data/processed/evaluation.tsv');

async function main() {
    try {
        console.log('Starting data preprocessing...');
        await preprocessData(trainingDataPath);
        
        console.log('Training the model...');
        const model = await trainModel(trainingDataPath);
        
        console.log('Evaluating the model...');
        const evaluationResults = await evaluateModel(model, evaluationDataPath);
        
        console.log('Training and evaluation completed successfully.');
        console.log('Evaluation Results:', evaluationResults);
    } catch (error) {
        console.error('An error occurred during training:', error);
    }
}

main();