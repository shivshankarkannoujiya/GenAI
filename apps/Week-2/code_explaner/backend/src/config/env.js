import dotenv from "dotenv"

dotenv.config({
    path: "./.env"
})

const ENV = {
    PORT: process.env.PORT ?? 8000,
    FRONTEND_URL: process.env.FRONTEND_URL,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
};

export { ENV }