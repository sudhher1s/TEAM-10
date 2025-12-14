import { CPTCode } from '../types';

export class CPTMapper {
    private cptCodes: CPTCode[];

    constructor(cptCodes: CPTCode[]) {
        this.cptCodes = cptCodes;
    }

    public getDescription(code: string): string | null {
        const cptCode = this.cptCodes.find(c => c.code === code);
        return cptCode ? cptCode.description : null;
    }

    public getAllCodes(): CPTCode[] {
        return this.cptCodes;
    }

    public addCode(code: CPTCode): void {
        this.cptCodes.push(code);
    }

    public removeCode(code: string): void {
        this.cptCodes = this.cptCodes.filter(c => c.code !== code);
    }
}