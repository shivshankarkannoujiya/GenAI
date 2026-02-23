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

    const SYSTEM_PROMPT = `You are an expert in query reformulation for document retrieval.

    Given a user question generate ${n} alternative queries, one per strategy:
    1. A simple rephrase with different vocabulary
    2. A technical deep-dive (implementation/internals focused)
    3. A practical use-case question (how would someone use this?)
    4. A specific sub-question (break down one concrete aspect)

    Output only the queries, one per line, no numbering, no explanation, no "None".`;

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
