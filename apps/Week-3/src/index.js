import { runRAGPipeline } from './rag/pipeline';

const question = 'what is the fs module and how do I use it?';

const result = await runRAGPipeline(question, 4, 3);

console.log('\n' + '═'.repeat(60));
console.log('FINAL ANSWER');
console.log('═'.repeat(60));
console.log(result.answer);
console.log('\nQueries used:', result.queries);
console.log('Docs retrieved:', result.docs.length);
console.log('Time taken:', result.timeTaken);