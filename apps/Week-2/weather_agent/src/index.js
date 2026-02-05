import dotenv from "dotenv"
import OpenAI from "openai"
import readlineSync from "readline-sync"

dotenv.config({
    path:"./.env"
})

const OPENAI_API_KEY = process.env.OPENAI_API_KEY

const AI = new OpenAI({
    apiKey: OPENAI_API_KEY
})


async function getWeatherDetails(city = "") {
    const location = `${city},India`;
    const url = `https://wttr.in/${encodeURIComponent(location)}?format=j1`;

    try {
        const response = await fetch(url, {
             headers: {
                "User-Agent": "curl/7.88.1"
            }
        })

        if (!response.ok) {
            throw new Error("Failed to fetch weather");
        }

        const data = await response.text()
        return data.trim()
    } catch (error) {
         return "Weather unavailable";
    }
}

const availableTools = {
    "getWeatherDetails": getWeatherDetails
}

const SYSTEM_PROMPT = `
You are an AI Assistant with START, PLAN, ACTION, OBSERVATION and OUTPUT state.

Wait for the user prompt and first PLAN using available tools.
After planning, take ACTION with the appropriate tool and wait for OBSERVATION.

Once you get the observation, return the OUTPUT.

STRICTLY FOLLOW JSON FORMAT.

AVAILABLE TOOLS
- getWeatherDetails(city: string): string

EXAMPLE:
START
{"type":"user","content":"what is the sum of weather of Patiala and Mohali"}
{"type":"plan","plan":"I will call getWeatherDetails for Patiala"}
{"type":"action","function":"getWeatherDetails","input":"Patiala"}
{"type":"observation","observation":"10°C"}
{"type":"plan","plan":"I will call getWeatherDetails for Mohali"}
{"type":"action","function":"getWeatherDetails","input":"Mohali"}
{"type":"observation","observation":"14°C"}
{"type":"output","output":"The sum of weather of Patiala and Mohali is 24°C"}
`;

const messages = [{ role: "system", content: SYSTEM_PROMPT }];

(async () => {

    while (true) {
        const user_query = readlineSync.question("Ask: ")

        const query = {
            type: "user",
            content: user_query
        }

        messages.push({
            role: "user",
            content: JSON.stringify(query)
        })

        while (true) {
            const chat = await AI.chat.completions.create({
                model: "gpt-4o-mini",
                messages,
                response_format: { type: "json_object" }
            })

            const result = chat.choices[0].message.content
            messages.push({ role: "assistant", content: result })

            console.log(`________ AI _________`);
            console.log(result);
            console.log(`________ AI _________`);
            

            const call = JSON.parse(result)

            if (call.type === "output") {
                console.log(`🤖 ${call.output}`)
                break
            }

            if (call.type === "action") {
                const fn = availableTools[call.function]
                const observation = await fn(call.input)

                const obs = {
                    type: "observation",
                    observation
                }

                messages.push({
                    role: "user",
                    content: JSON.stringify(obs)
                })
            }
        }
    }

})();