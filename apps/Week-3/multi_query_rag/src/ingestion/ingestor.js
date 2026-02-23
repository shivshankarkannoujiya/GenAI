import pdfQueue from './queue.js';

const ingestPDF = async (filePath, fileName, metadata = {}) => {
    if (!filePath) throw new Error('filePath is required');

    const job = await pdfQueue.add(
        'process-pdf',
        JSON.stringify({
            path: filePath,
            fileName,
            metadata,
            uploadedAt: new Date().toISOString(),
        })
    );

    console.log(`[Ingestor] Job ${job.id} added for file: ${fileName}`);
    return job.id;
};

export default ingestPDF;
