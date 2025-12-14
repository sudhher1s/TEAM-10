import { SNOMEDCode } from '../types/index';

export class SnomedMapper {
    private snomedCodes: SNOMEDCode[];

    constructor(snomedCodes: SNOMEDCode[]) {
        this.snomedCodes = snomedCodes;
    }

    public getDescription(code: string): string | undefined {
        const codeEntry = this.snomedCodes.find(snomed => snomed.code === code);
        return codeEntry ? codeEntry.description : undefined;
    }

    public getAllCodes(): SNOMEDCode[] {
        return this.snomedCodes;
    }

    public findByDescription(description: string): SNOMEDCode[] {
        return this.snomedCodes.filter(snomed => snomed.description.toLowerCase().includes(description.toLowerCase()));
    }
}