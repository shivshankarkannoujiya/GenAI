import { Queue } from "bullmq";
import valkey from "../config/valkey.config.js";

const pdfQueue = new Queue('pdf-processing', {
    connection: valkey,
    defaultJobOptions: {
        attempts: 3,
        backoff: {
            type: "exponential",
            delay: 2000
        },
        removeOnComplete: 10,
        removeOnFail: 20
    },
});

export default pdfQueue