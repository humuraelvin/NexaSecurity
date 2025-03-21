import { convertToCoreMessages, Message, streamText } from "ai";

import { geminiProModel } from "@/ai";
import { systemPrompt } from "@/ai/prompts";
import { aiTools } from "@/ai/tools";

export async function POST(request: Request) {
  const { messages }: { id: string; messages: Array<Message> } =
    await request.json();

  const coreMessages = convertToCoreMessages(messages).filter(
    (message) => message.content.length > 0
  );

  const result = await streamText({
    model: geminiProModel,
    system: systemPrompt,
    messages: coreMessages,
    tools: aiTools,
    onFinish: async ({ finishReason }) => {
      console.log(finishReason);
    },
    experimental_telemetry: {
      isEnabled: true,
      functionId: "stream-text",
    },
  });

  return result.toDataStreamResponse({});
}
