import app from "./app.js";
import dotenv from "dotenv"

dotenv.config({
    path:"./.env"
})

const PORT = process.env.PORT ?? 8000

app.listen(PORT, () => {
    console.log(`Serving at http://localhost:${PORT}`)
})
