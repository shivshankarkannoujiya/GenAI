import { generateQueries } from './queryReformulator.js';
import { retrieveAll } from './retriver.js';
import { generateAnswer } from './answerGenerator.js';
import { deduplicate } from './deduplicator.js';

export const runRAGPipeline = async (question, nQueries = 4, topK = 3) => {
    console.log('━'.repeat(60));
    console.log(`[RAG Pipeline] Starting for: "${question}"`);
    console.log('━'.repeat(60));

    const startTime = Date.now();

    try {
        // ── Step 1: Reformulate ─────────────────────────────────────
        const queries = await generateQueries(question, nQueries);

        // ── Step 2: Retrieve in Parallel ────────────────────────────
        const allResults = await retrieveAll(queries, topK);

        // ── Step 3: Deduplicate & Filter ────────────────────────────
        const uniqueDocs = deduplicate(allResults);

        if (uniqueDocs.length === 0) {
            return {
                question,
                queries,
                docs: [],
                answer: 'No relevant documents found for your question.',
                timeTaken: `${Date.now() - startTime}ms`,
            };
        }

        // ── Step 4: Generate Answer ──────────────────────────────────
        const answer = await generateAnswer(question, uniqueDocs);

        const timeTaken = `${Date.now() - startTime}ms`;

        console.log('\n[RAG Pipeline] Done in', timeTaken);
        console.log('━'.repeat(60));

        return {
            question,
            queries,
            docs: uniqueDocs,
            answer,
            timeTaken,
        };
    } catch (error) {
        console.error('[RAG Pipeline] Failed:', error.message);
        throw error;
    }
};
