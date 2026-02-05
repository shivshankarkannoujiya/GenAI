import { exec } from "child_process";
import { promisify } from "util";
import { writeFile } from "fs/promises";

const execPromise = promisify(exec);

export async function executeCommand(command) {
  try {
    const { stdout, stderr } = await execPromise(command, {
      timeout: 30000,
      maxBuffer: 1024 * 1024,
    });

    return {
      success: true,
      output: stdout || stderr || "Command executed successfully",
      command: command,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      output: error.stderr || error.message,
      command: command,
    };
  }
}

export async function createFile(filepath, content) {
  console.log(
    `[createFile] Called with filepath: ${filepath}, content length: ${content?.length || 0}`,
  );

  try {
    await writeFile(filepath, content || "", "utf-8");
    console.log(`[createFile] Successfully created: ${filepath}`);

    return {
      success: true,
      output: `File ${filepath} created successfully`,
      filepath: filepath,
    };
  } catch (error) {
    console.error(`[createFile] Error:`, error);

    return {
      success: false,
      error: `Failed to create file: ${error.message}`,
      output: `Failed to create file: ${error.message}`,
      filepath: filepath,
    };
  }
}
