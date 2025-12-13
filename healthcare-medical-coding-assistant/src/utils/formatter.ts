import { CodingOutput } from '../types';

// Minimal formatter to pass data through; extend with real formatting when available.
export function formatResponse(output: CodingOutput | any) {
  return output;
}
