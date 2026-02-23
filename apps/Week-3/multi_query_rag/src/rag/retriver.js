import { OpenAIEmbeddings } from '@langchain/openai';
import { QdrantVectorStore } from '@langchain/qdrant';
import { ENV } from '../config/env.js';

const embedder = new OpenAIEmbeddings({
    model: 'text-embedding-3-small',
    apiKey: ENV.OPENAI_API_KEY,
});

const COLLECTION_NAME = 'rag-multi-query-test';

let vectorStoreInstance = null;

const getVectorStore = async () => {
    if (!vectorStoreInstance) {
        vectorStoreInstance = await QdrantVectorStore.fromExistingCollection(
            embedder,
            {
                url: ENV.QDRANT_URL,
                collectionName: COLLECTION_NAME,
            }
        );
        console.log('[Retriever] Connected to Qdrant successfully');
    }
    return vectorStoreInstance;
};

function generateDocId(doc) {
    if (doc.metadata?.['_id']) return String(doc.metadata['_id']);
    if (doc.metadata?.source && doc.metadata?.loc) {
        return `${doc.metadata.source}-${JSON.stringify(doc.metadata.loc)}-${doc.pageContent.slice(0, 20)}`;
    }
    return doc.pageContent.slice(0, 80).replace(/\s+/g, ' ');
}

const retrieveForQuery = async (query, topK = 3) => {
    const vectorStore = await getVectorStore();
    const result = await vectorStore.similaritySearchWithScore(query, topK);

    return result.map(([doc, score]) => ({
        id: generateDocId(doc),
        content: doc.pageContent,
        score: parseFloat(score.toFixed(4)),
        metadata: doc.metadata,
        retrievedBy: query,
    }));
};

export const retrieveAll = async (queries, topK = 3) => {
    console.log(
        `\n[Retriever] Searching Qdrant for ${queries.length} queries in parallel...`
    );

    await getVectorStore();

    const settled = await Promise.allSettled(
        queries.map((query) => retrieveForQuery(query, topK))
    );

    const results = settled.map((result, i) => {
        if (result.status === 'fulfilled') return result.value;
        console.warn(
            `[Retriever] Query failed: "${queries[i]}" —`,
            result.reason.message
        );
        return [];
    });

    const totalDocs = results.reduce((sum, r) => sum + r.length, 0);
    console.log(`[Retriever] Retrieved ${totalDocs} docs (with duplicates)`);

    return results;
};
