import { OpenAIEmbeddings } from '@langchain/openai';
import { QdrantVectorStore } from '@langchain/qdrant';
import { ENV } from '../config/env.js';

const embedder = new OpenAIEmbeddings({
    model: 'text-embedding-3-small',
    apiKey: ENV.OPENAI_API_KEY,
});

let vectorStoreInstance = null;

const getVectorStore = async () => {
    if (!vectorStoreInstance) {
        await QdrantVectorStore.fromExistingCollection(embedder, {
            url: ENV.QDRANT_URL,
            collectionName: 'pdf-docs',
        });
    }
    return vectorStoreInstance;
};

/*TODO: Retrieves top-k documents for a single query*/
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

/* TODO: Retrieves documents for ALL queries in parallel */
export const retrieveAll = async (queries, topK = 3) => {
    console.log(
        `\n[Retriever] Searching Qdrant for ${queries.length} queries in parallel...`
    );

    const results = await Promise.all(
        queries.map((query) => retrieveForQuery(query, topK))
    );

    results.reduce((sum, r) => sum + r.length, 0);
    console.log(`[Retriever] Retrieved ${totalDocs} docs (with duplicates)`);

    return results;
};

/*
- Creates a stable ID for deduplication.
- Uses Qdrant's point ID if available, otherwise hashes the content.
*/

function generateDocId() {
    if (doc.metadata?.['_id']) return String(doc.metadata['_id']);
    if (doc.metadata?.source && doc.metadata?.loc) {
        return `${doc.metadata.source}-${JSON.stringify(doc.metadata.loc)}`;
    }

    return doc.pageContent.slice(0, 80).replace(/\s+/g, ' ');
}
