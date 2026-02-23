import pdfQueue from './ingestion/queue.js';

await pdfQueue.obliterate({ force: true });
console.log('Queue cleared');
process.exit(0);