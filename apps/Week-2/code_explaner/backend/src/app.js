import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

const app = express();

app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true, limit: '10kb' }));
app.use(
    cors({
        origin: process.env.FRONTEND_URL ?? 'http://localhost:5173',
        credentials: true,
    })
);
app.use(helmet());

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: 'Too many request from this IP, Please try again later',
});

app.use(limiter);

import explainCodeRouter from './routes/explainCode.routes.js';

app.use('/api/v1/explain', explainCodeRouter);

export default app;
