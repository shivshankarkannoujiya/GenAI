import pdfWorker from './ingestion/worker.js';
import ingestPDF  from './ingestion/ingestor.js';

const filePath = process.argv[2];
const fileName = process.argv[3];

if (!filePath || !fileName) {
    console.error('Usage: node src/ingest.js <filePath> <fileName>');
    console.error('Example: node src/ingest.js uploads/sample.pdf sample.pdf');
    process.exit(1);
}

async function main() {
    console.log(`\nIngesting: ${fileName}`);

    const jobId = await ingestPDF(filePath, fileName);
    console.log(`Job queued: ${jobId} — waiting for worker...`);

    // Wait for this specific job to complete then exit
    await new Promise((resolve, reject) => {
        pdfWorker.on('completed', (job) => {
            if (String(job.id) === String(jobId)) {
                console.log(`\n✅ Ingestion complete for: ${fileName}`);
                resolve();
            }
        });

        pdfWorker.on('failed', (job, err) => {
            if (String(job?.id) === String(jobId)) {
                console.error(`\n❌ Ingestion failed:`, err.message);
                reject(err);
            }
        });
    });

    process.exit(0);
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
