import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export const generateCodingSuggestions = async (clinicalNote: string): Promise<string[]> => {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'user',
          content: `Based on the following clinical note, suggest appropriate ICD-10 codes: ${clinicalNote}`,
        },
      ],
      max_tokens: 150,
    });

    const suggestions = response.choices[0].message.content.split('\n').filter(Boolean);
    return suggestions;
  } catch (error) {
    console.error('Error generating coding suggestions:', error);
    throw new Error('Failed to generate coding suggestions');
  }
};