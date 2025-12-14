export const API_BASE_URL = '/api/v1';

export const CODING_ENDPOINT = `${API_BASE_URL}/coding`;
export const AUDIT_ENDPOINT = `${API_BASE_URL}/audit`;
export const HEALTH_CHECK_ENDPOINT = `${API_BASE_URL}/health`;

export const ERROR_MESSAGES = {
    INVALID_INPUT: 'The input provided is invalid.',
    NOT_FOUND: 'The requested resource was not found.',
    UNAUTHORIZED: 'You are not authorized to access this resource.',
    INTERNAL_SERVER_ERROR: 'An internal server error occurred.',
};

export const SUCCESS_MESSAGES = {
    CODING_SUCCESS: 'Coding operation completed successfully.',
    AUDIT_SUCCESS: 'Audit operation completed successfully.',
    HEALTH_CHECK_SUCCESS: 'Service is running smoothly.',
};