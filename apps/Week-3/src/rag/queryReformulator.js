import OpenAI from 'openai';
import { ENV } from '../config/env.js';

const AI = new OpenAI({ apiKey: ENV.OPENAI_API_KEY });

/*
TODO:
 1. Generates n alternative queries from the original question.
 > Uses three strategies: paraphrase, perspective shift, decomposition.
 */

export const generateQueries = async (question, n = 4) => {
    if (!question || typeof question != 'string') {
        throw new Error('Question must be a non-empty string');
    }

    const SYSTEM_PROMPT = `
    You are an expert in query reformulation for document retrieval.

    Given a question, generate ${n} alternative queries using these strategies.
    1. Rephrase with different vocabulary.
    2. Approach from different perspective.
    3. Break into sub-question if the query is complex.
    
    Rules:
    - Output only the querues, one per line.
    - No numbring, no explanation, no "None".
    - Do not repeat the same idea twice.
    - Keep each query concise and focused
    `;

    try {
        const response = await AI.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: SYSTEM_PROMPT },
                { role: 'user', content: question },
            ],
            temperature: 0.7,
            max_completion_tokens: 300,
        });

        const raw = response.choices[0].message.content.trim();

        const alternativeQueries = raw
            .split('\n')
            .map((line) => line.trim())
            .filter(
                (line) =>
                    line &&
                    line.toLocaleLowerCase() != 'none' &&
                    line.length > 5
            );

        // debugging
        const allQueries = [question, ...alternativeQueries];

        console.log(
            `\n[QueryReformulator] Generated ${allQueries.length} queries:`
        );
        allQueries.forEach((q, i) => console.log(`  ${i + 1}. ${q}`));

        return allQueries;
    } catch (error) {
        console.error(
            '[QueryReformulator] Failed to generate queries:',
            error.message
        );

        return [question];
    }
};


