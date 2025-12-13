export interface Claim {
    id: string;
    patientId: string;
    providerId: string;
    diagnosisCodes: string[];
    procedureCodes: string[];
    dateOfService: string;
    amountBilled: number;
    amountPaid: number;
}

export interface Encounter {
    id: string;
    patientId: string;
    providerId: string;
    encounterDate: string;
    diagnosis: string;
    notes: string;
}

export interface MedicalCode {
    code: string;
    description: string;
    category: string;
}

export interface ICD10Code extends MedicalCode {
    chapter: string;
}

export interface CPTCode extends MedicalCode {
    section: string;
}

export interface SNOMEDCode extends MedicalCode {
    hierarchy: string;
}

export interface HealthCheckResponse {
    status: string;
    timestamp: string;
}

export interface ErrorResponse {
    message: string;
    code: number;
}