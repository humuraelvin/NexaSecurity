"use client";

import { Attachment, ToolInvocation } from "ai";
import { motion } from "framer-motion";
import { ReactNode } from "react";

import { Markdown } from "./Markdown";
import { SparkleIcon, User2Icon } from "lucide-react";
import { cn } from "@/lib/utils";

export const Message = ({
  role,
  content,
  toolInvocations,
}: {
  chatId: string;
  role: string;
  content: string | ReactNode;
  toolInvocations: Array<ToolInvocation> | undefined;
  attachments?: Array<Attachment>;
}) => {
  return (
    <motion.div
      className={`flex flex-row gap-4 px-4 w-full md:max-w-2xl md:px-0 first-of-type:pt-20`}
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
    >
      <div
        className={cn(
          "size-[32px] rounded-full p-1 flex flex-col items-center shrink-0 text-zinc-500",
          role == "assistant" ? "border border-gray-700 justify-center" : ""
        )}
      >
        {role === "assistant" ? <SparkleIcon /> : <User2Icon />}
      </div>

      <div className="flex flex-col gap-2 w-full">
        {content && typeof content === "string" && (
          <div
            data-testid="message-content"
            className={cn("flex flex-col gap-4", {
              "bg-primary text-primary-foreground px-3 rounded-xl":
                role === "user",
            })}
          >
            <Markdown>{content}</Markdown>
          </div>
        )}

        {toolInvocations && (
          <div className="flex flex-col gap-4">
            {toolInvocations.map((toolInvocation) => {
              const { toolName, toolCallId, state } = toolInvocation;

              if (state === "result") {
                const { result } = toolInvocation;

                return (
                  <div key={toolCallId}>
                    {toolName === "getWeather" ? (
                      <div>
                        <p>Weather</p>
                      </div>
                    ) : (
                      <div>{JSON.stringify(result, null, 2)}</div>
                    )}
                  </div>
                );
              } else {
                return (
                  <div key={toolCallId} className="skeleton">
                    {toolName === "getWeather" ? (
                      <div>
                        <p>Weather</p>
                      </div>
                    ) : null}
                  </div>
                );
              }
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
};
