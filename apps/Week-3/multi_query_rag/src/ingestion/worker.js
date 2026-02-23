import path from 'path';
import fs from 'fs';
import valkey from '../config/valkey.config.js';
import qdrantClient from '../config/qdrant.config.js';
import { Worker } from 'bullmq';
import { ENV } from '../config/env.js';
import { OpenAIEmbeddings } from '@langchain/openai';
import { QdrantVectorStore } from '@langchain/qdrant';
import { PDFLoader } from '@langchain/community/document_loaders/fs/pdf';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';

const COLLECTION_NAME = 'rag-multi-query-test';

const embedder = new OpenAIEmbeddings({
    model: 'text-embedding-3-small',
    apiKey: ENV.OPENAI_API_KEY,
});

// ─── Helpers ─────────────────────────────────────────────────────────────────

const loadPDF = async (relativePath) => {
    const safeRelativePath = relativePath.replace(/\\/g, '/');
    const absolutePath = path.join(process.cwd(), safeRelativePath);

    console.log(`[Worker] Reading file: ${absolutePath}`);

    if (!fs.existsSync(absolutePath)) {
        throw new Error(`PDF file not found at path: ${absolutePath}`);
    }

    const loader = new PDFLoader(absolutePath);
    const docs = await loader.load();

    console.log(`[Worker] Pages loaded: ${docs.length}`);
    return docs;
};

const chunkDocuments = async (docs) => {
    const splitter = new RecursiveCharacterTextSplitter({
        chunkSize: 500,
        chunkOverlap: 100,
        separators: ['\n\n', '\n', '. ', ' ', ''],
    });

    const chunks = await splitter.splitDocuments(docs);
    console.log(`[Worker] Chunks created: ${chunks.length}`);
    return chunks;
};

/*
 Enriches each chunk with consistent metadata
*/

const enrichMetadata = (chunks, jobData) => {
    return chunks.map((chunk, index) => ({
        ...chunk,
        metadata: {
            ...chunk.metadata,
            fileName: jobData.fileName,
            chunkIndex: index,
            totalChunks: chunks.length,
            uploadedAt: jobData.uploadedAt,
            ...jobData.metadata,
        },
    }));
};

// Stores enriched chunks into Qdrant
const storeInQdrant = async (chunks) => {

    const response = await qdrantClient.getCollections();
    const exists = response.collections.some((c) => c.name === COLLECTION_NAME);

    if (!exists) {
        await qdrantClient.createCollection(COLLECTION_NAME, {
            vectors: {
                size: 1536, // text-embedding-3-small dimension
                distance: 'Cosine',
            },
        });
        console.log(`[Worker] Collection '${COLLECTION_NAME}' created`);
    } else {
        console.log(
            `[Worker] Collection '${COLLECTION_NAME}' already exists — skipping creation`
        );
    }

    const vectorStore = await QdrantVectorStore.fromExistingCollection(
        embedder,
        {
            url: ENV.QDRANT_URL,
            collectionName: COLLECTION_NAME,
        }
    );

    console.log(`Storing into vector DB...`);
    await vectorStore.addDocuments(chunks);
    console.log(`[Worker] Stored ${chunks.length} chunks into Qdrant`);
};

// ─── Worker ──────────────────────────────────────────────────────────────────

const pdfWorker = new Worker(
    'pdf-processing',
    async (job) => {
        console.log(`\n[Worker] Processing job ${job.id}`);

        const data = JSON.parse(job.data);

        // 1. load pdf
        const docs = await loadPDF(data.path);

        // 2. Chunk
        const chunks = await chunkDocuments(docs);

        // 3. Enrich Metadata
        const enrichedChunks = enrichMetadata(chunks, data);

        // 4. Embed + Store in Qdrant
        console.log('[Worker] Embedding and storing into Qdrant...');

        await storeInQdrant(enrichedChunks);

        console.log(`[Worker] Job ${job.id} completed successfully`);

        return {
            fileName: data.fileName,
            totalChunks: chunks.length,
        };
    },
    {
        concurrency: 5,
        connection: valkey,
    }
);

pdfWorker.on('completed', (job, result) => {
    console.log(
        `[Worker] ✅ Job ${job.id} done — ${result.totalChunks} chunks stored for "${result.fileName}"`
    );
});

pdfWorker.on('failed', (job, err) => {
    console.error(`[Worker] ❌ Job ${job?.id} failed:`, err.message);
});

pdfWorker.on('progress', (job, progress) => {
    console.log(`[Worker] Job ${job.id} progress: ${progress}%`);
});

export default pdfWorker;
