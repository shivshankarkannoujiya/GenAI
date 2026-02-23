import { runRAGPipeline } from './rag/pipeline.js';

const question = process.argv[2]; 

if (!question) {
    console.error('Usage: node src/query.js "your question here"');
    console.error('Example: node src/query.js "what is the fs module?"');
    process.exit(1);
}

async function main() {
    const result = await runRAGPipeline(question, 4, 3);

    console.log('\n' + '═'.repeat(60));
    console.log('FINAL ANSWER');
    console.log('═'.repeat(60));
    console.log(result.answer);
    console.log('\nQueries used:', result.queries.length);
    console.log('Docs retrieved:', result.docs.length);
    console.log('Time taken:', result.timeTaken);
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
