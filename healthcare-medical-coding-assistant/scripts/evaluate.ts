import fs from 'fs';
import path from 'path';
import { evaluateModel } from '../src/services/codingEngine';
import { loadEvaluationData } from '../src/pipelines/preprocessing';
import { logResults } from '../src/utils/logger';

const evaluate = async () => {
    try {
        const evaluationDataPath = path.join(__dirname, '../data/processed/evaluation.tsv');
        const evaluationData = await loadEvaluationData(evaluationDataPath);
        
        const results = await evaluateModel(evaluationData);
        
        logResults(results);
        
        console.log('Evaluation completed successfully.');
    } catch (error) {
        console.error('Error during evaluation:', error);
    }
};

evaluate();