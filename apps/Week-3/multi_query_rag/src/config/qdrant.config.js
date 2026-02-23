import { ENV } from './env.js';
import { QdrantClient } from '@qdrant/js-client-rest';

const qdrantClient = new QdrantClient({ url: ENV.QDRANT_URL });

export default qdrantClient;
