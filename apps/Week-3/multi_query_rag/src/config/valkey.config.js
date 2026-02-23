import { Redis } from 'ioredis';
import { ENV } from './env.js';

const valkey = new Redis({
    host: ENV.VALKEY_HOST || 'localhost',
    port: ENV.VALKEY_PORT || '6379',
    maxRetriesPerRequest: null,
});

valkey.on('connect', () => console.log('Valkey connected'));
valkey.on('error', (err) => console.error('Valkey error:', err));

export default valkey;
