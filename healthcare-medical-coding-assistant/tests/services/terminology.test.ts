import { getTerminology, getTerminologyById } from '../../src/services/terminology';
import { Terminology } from '../../src/types/index';

describe('Terminology Service', () => {
    it('should fetch all terminologies', async () => {
        const terminologies: Terminology[] = await getTerminology();
        expect(terminologies).toBeDefined();
        expect(Array.isArray(terminologies)).toBe(true);
    });

    it('should fetch a terminology by ID', async () => {
        const id = 'some-terminology-id';
        const terminology: Terminology | null = await getTerminologyById(id);
        expect(terminology).toBeDefined();
        expect(terminology?.id).toBe(id);
    });

    it('should return null for a non-existent terminology ID', async () => {
        const id = 'non-existent-id';
        const terminology: Terminology | null = await getTerminologyById(id);
        expect(terminology).toBeNull();
    });
});