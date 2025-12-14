import { CodingOutput } from '../types';
import { formatResponse } from '../utils/formatter';

/**
 * Postprocesses the output from the coding engine to format it for the API response.
 * 
 * @param output - The raw output from the coding engine.
 * @returns The formatted response for the API.
 */
export function postprocessOutput(output: CodingOutput): any {
    // Format the output using a utility function
    const formattedResponse = formatResponse(output);

    // Additional postprocessing can be added here if needed

    return formattedResponse;
}