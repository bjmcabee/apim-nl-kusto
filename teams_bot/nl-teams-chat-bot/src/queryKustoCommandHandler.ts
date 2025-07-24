import { Selector } from "@microsoft/teams-ai";
import { Activity, TurnContext } from "botbuilder";
import { ApplicationTurnState } from "./internal/interface";

/**
 * The `QueryKustoCommandHandler` registers patterns and responds
 * with appropriate messages if the user types general command inputs, such as "hi", "hello", and "help".
 */
export class QueryKustoCommandHandler {
  /**
   * Formats the Azure Function response according to the specified constraints.
   *
   * @param result The result object from the Azure Function
   * @returns Formatted string
   */
  private formatAzureResponse(result: any): string {
    // Format the KQL query
    const kqlBlock = result.generated_query
      ? `\n\n**Generated Query:**\n\n\`\`\`kql\n${result.generated_query.trim()}\n\`\`\`\n`
      : "";

    // Format the results as a table
    let tableBlock = "";
    if (Array.isArray(result.results) && result.results.length > 0) {
      const columns = Object.keys(result.results[0]);
      tableBlock += `\n**Results:**\n\n| ${columns.join(" | ")} |\n| ${columns.map(() => "---").join(" | ")} |\n`;
      for (const row of result.results) {
        tableBlock += `| ${columns.map(col => row[col]).join(" | ")} |\n`;
      }
    }

    const summaryBlock = result.summarized_results ? `\n**Summary:**\n\n${result.summarized_results}\n` : "";
    const promptBlock = result.prompt ? `**You asked:** ${result.prompt}\n` : "";

    return `${promptBlock}${kqlBlock}${tableBlock}${summaryBlock}`.trim();
  }
  triggerPatterns: string | RegExp | Selector | (string | RegExp | Selector)[] = new RegExp(/^.+$/);

  async handleCommandReceived(
    context: TurnContext,
    state: ApplicationTurnState
  ): Promise<string | Partial<Activity> | void> {
    console.log(`App received message: ${context.activity.text}`);

    let response = "";
    switch (context.activity.text) {
      case "hi":
      case "hello":
        response =
          "Hello! I'm your NL Kusto Bot, always ready to help you out. If you need assistance, just type 'help' to see the available commands.";
        break;
      case "help":
        response =
          "Here's a list of commands I can help you with:\n" +
          "- 'hi' or 'hello': Say hi or hello to me, and I'll greet you back.\n" +
          "- 'help': Get a list of available commands.\n\n" +
          "- Otherwise, feel free to ask me to run a kusto query for you!\n";
        break;
      default:
        try {
          const baseFunctionUrl = `${process.env.AZURE_FUNCTION_URL}/kusto_nl_query?code=${process.env.AZURE_FUNCTION_CODE}==`;
          const promptParam = encodeURIComponent(context.activity.text);
          const functionUrl = `${baseFunctionUrl}&prompt=${promptParam}`;
          const fetch = (await import("node-fetch")).default;
          const azureResponse = await fetch(functionUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
          });
          if (azureResponse.ok) {
            const result = await azureResponse.json();
            response = this.formatAzureResponse(result);
          } else {
            response = `Azure Function call failed: ${azureResponse.statusText}`;
          }
        } catch (err) {
          response = `Error calling Azure Function: ${err}`;
        }
    }

    return response;
  }
}

