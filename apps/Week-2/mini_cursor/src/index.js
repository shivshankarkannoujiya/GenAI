import dotenv from "dotenv";
import OpenAI from "openai";
import readlineSync from "readline-sync";
import { SYSTEM_PROMPT } from "./sysstem_prompt.js";
import { executeCommand, createFile } from "./tools.js";

dotenv.config({
  path: "./.env",
});

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const AI_CLIENT = new OpenAI({ apiKey: OPENAI_API_KEY });

const availableTools = {
    executeCommand,
    createFile
};

const messages = [{ role: "system", content: SYSTEM_PROMPT }];
(async () => {
  while (true) {
    const user_query = readlineSync.question("Ask: ");

    const query = { type: "start", content: user_query };
    messages.push({ role: "user", content: JSON.stringify(query) });

    while (true) {
      const chat = await AI_CLIENT.chat.completions.create({
        model: "gpt-4o-mini",
        messages,
        response_format: { type: "json_object" },
      });

      const result = chat.choices[0].message.content;
      messages.push({ role: "assistant", content: result });

      console.log(`---------- AI START ----------`);
      console.log(result);
      console.log(`---------- AI END ----------`);

      const call = JSON.parse(result);

      if (call.type === "output") {
        console.log(`🤖 ${call.result}`);
        break;
      }

      // index.js - Update this section
      if (call.type === "action") {
        console.log(`\n⚡ Executing: ${call.function}\n`);

        const fn = availableTools[call.function];

        if (!fn) {
          console.error(`❌ Unknown function: ${call.function}`);
          const errorObs = {
            type: "observation",
            result: `Function ${call.function} not found`,
            status: "error",
          };
          messages.push({ role: "user", content: JSON.stringify(errorObs) });
          continue;
        }

        // Handle different input types
        let observation;
        try {
          if (call.function === "createFile") {
            // createFile expects two parameters: filepath and content
            if (
              typeof call.input === "object" &&
              call.input.filepath !== undefined
            ) {
              console.log(`Creating file: ${call.input.filepath}`);
              observation = await fn(
                call.input.filepath,
                call.input.content || "",
              );
            } else {
              // Fallback if input format is unexpected
              observation = {
                success: false,
                error: `Invalid input format for createFile. Expected {filepath, content}, got: ${JSON.stringify(call.input)}`,
              };
            }
          } else {
            observation = await fn(call.input);
          }

          console.log(`✅ Function result:`, observation);

          const obs = {
            type: "observation",
            result: observation.output || observation.error || "No output",
            status: observation.success ? "success" : "error",
          };

          console.log(`📊 Observation:`, obs);
          messages.push({ role: "user", content: JSON.stringify(obs) });
        } catch (error) {
          console.error(`❌ Error executing ${call.function}:`, error);
          const errorObs = {
            type: "observation",
            result: `Error: ${error.message}`,
            status: "error",
          };
          messages.push({ role: "user", content: JSON.stringify(errorObs) });
        }
      }

      // Handle plan state (just log and continue)
      // AI is planning, continue to next iteration
      if (call.type === "plan") {
        continue;
      }
    }
  }
})();
