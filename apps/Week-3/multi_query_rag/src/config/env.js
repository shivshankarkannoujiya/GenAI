import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({
    path: path.resolve(__dirname, '../../.env'),
});

if (!process.env.OPENAI_API_KEY) {
    throw new Error('OPENAI_API_KEY not found in .env');
}

export const ENV = {
    PORT: process.env.PORT,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    QDRANT_URL: process.env.QDRANT_URL,
    VALKEY_HOST: process.env.VALKEY_HOST,
    VALKEY_PORT: process.env.VALKEY_PORT,
};

if (!ENV.OPENAI_API_KEY) throw new Error('Missing OPENAI_API_KEY');
if (!ENV.QDRANT_URL) throw new Error('Missing QDRANT_URL');

