import OpenAI from 'openai';
import { ENV } from '../config/env.js';

const AI = new OpenAI({ apiKey: ENV.OPENAI_API_KEY });

// cap docs to avoid context window overflow
const MAX_CONTEXT_DOCS = 8;

/*
    Generates the final answer using retrieved docs as context.
*/

export const generateAnswer = async (question, docs) => {
    if (!docs || docs.length === 0) {
        return 'I could not find relevant information in the provided documents to answer your question.';
    }

    // Take top docs by score, cap at MAX_CONTEXT_DOCS
    const topDocs = docs.slice(0, MAX_CONTEXT_DOCS);

    // Build context block
    const context = topDocs
        .map(
            (doc, i) =>
                `[Source ${i + 1}] (score: ${doc.score})\n${doc.content}`
        )
        .join('\n\n---\n\n');

    const SYSTEM_PROMPT = `
    You are a helpful assistant that answers questions based strictly on the provided context.
    
    Rules:
    - Answer ONLY from the context provided
    - If the context does not contain enough information, say: "The provided documents do not contain enough information to answer this question."
    - Be concise and accurate
    - Do not hallucinate or add information not present in the context
    
    - Cite sources as [Source 1], [Source 2] etc. when referencing specific information`;

    const USER_PROMPT = ` Context: ${context}

    Question: ${question}
    Answer: 
    `;

    console.log(
        `\n[AnswerGenerator] Generating answer using ${topDocs.length} context docs...`
    );

    try {
        const response = await AI.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: SYSTEM_PROMPT },
                { role: 'user', content: USER_PROMPT },
            ],
            temperature: 0,
        });

        return response.choices[0].message.content.trim();
    } catch (error) {
        console.error(
            '[AnswerGenerator] Failed to generate answer:',
            error.message
        );
        throw error;
    }
};
