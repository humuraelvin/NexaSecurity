"use client";

import type { UIMessage } from "ai";
import { AnimatePresence, motion } from "framer-motion";
import { memo } from "react";
import { Markdown } from "./Markdown";
import equal from "fast-deep-equal";
import { cn } from "@/lib/utils";
import { UseChatHelpers } from "@ai-sdk/react";
import {
  Activity,
  AlertCircle,
  Cloud,
  Globe,
  Lock,
  Shield,
  SparklesIcon,
  Wifi,
} from "lucide-react";

const PurePreviewMessage = ({
  message,
}: {
  chatId: string;
  message: UIMessage;
  isLoading: boolean;
  setMessages: UseChatHelpers["setMessages"];
  reload: UseChatHelpers["reload"];
  isReadonly: boolean;
}) => {
  return (
    <AnimatePresence>
      <motion.div
        data-testid={`message-${message.role}`}
        className="w-full mx-auto max-w-3xl px-4 group/message"
        initial={{ y: 5, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        data-role={message.role}
      >
        <div
          className={cn(
            "flex gap-4 w-full group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-2xl",
            "group-data-[role=user]/message:w-fit"
          )}
        >
          {message.role === "assistant" && (
            <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-gray-700 bg-gray-900">
              <div className="translate-y-px">
                <SparklesIcon size={14} />
              </div>
            </div>
          )}

          <div className="flex flex-col gap-4 w-full">
            {message.parts?.map((part, index) => {
              const { type } = part;
              const key = `message-${message.id}-part-${index}`;

              if (type === "text") {
                return (
                  <div key={key} className="flex flex-row gap-2 items-start">
                    <div
                      data-testid="message-content"
                      className={cn("flex flex-col gap-4", {
                        "text-gray-200 px-3 py-2 rounded-xl bg-gray-800/80":
                          message.role === "user",
                      })}
                    >
                      <Markdown>{part.text}</Markdown>
                    </div>
                  </div>
                );
              }

              if (type === "tool-invocation") {
                const { toolInvocation } = part;
                const { toolName, toolCallId, state } = toolInvocation;

                // Tool icon mapping
                const getToolIcon = (tool: string) => {
                  switch (tool) {
                    case "scanNetwork":
                      return <Wifi className="h-5 w-5" />;
                    case "vulnerabilityScan":
                      return <Shield className="h-5 w-5" />;
                    case "analyzeTraffic":
                      return <Activity className="h-5 w-5" />;
                    case "passwordCheck":
                      return <Lock className="h-5 w-5" />;
                    case "runPentest":
                      return <Shield className="h-5 w-5 text-amber-400" />;
                    case "getWeather":
                      return <Cloud className="h-5 w-5" />;
                    default:
                      return <Globe className="h-5 w-5" />;
                  }
                };

                // Loading state design
                if (state === "call") {
                  return (
                    <div
                      key={toolCallId}
                      className="flex flex-col gap-2 p-3 bg-gray-800/50 border border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center gap-2 text-gray-300">
                        {getToolIcon(toolName)}
                        <span className="font-medium capitalize">
                          {toolName.replace(/([A-Z])/g, " $1").trim()}
                        </span>
                        <span className="ml-auto flex items-center gap-2 text-amber-400">
                          <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-amber-400"></span>
                          Processing...
                        </span>
                      </div>
                      {toolName === "scanNetwork" && (
                        <div className="text-sm text-gray-400">
                          Initiating network scan. This may take a moment...
                        </div>
                      )}
                      {toolName === "vulnerabilityScan" && (
                        <div className="text-sm text-gray-400">
                          Running vulnerability scan. Please wait...
                        </div>
                      )}
                      {toolName === "analyzeTraffic" && (
                        <div className="text-sm text-gray-400">
                          Capturing and analyzing network traffic...
                        </div>
                      )}
                      {toolName === "passwordCheck" && (
                        <div className="text-sm text-gray-400">
                          Analyzing password strength...
                        </div>
                      )}
                      {toolName === "getWeather" && (
                        <div className="text-sm text-gray-400">
                          Fetching weather data...
                        </div>
                      )}
                      {toolName === "runPentest" && (
                        <div className="text-sm text-gray-400">
                          Initiating penetration test. This may take several
                          minutes...
                        </div>
                      )}
                    </div>
                  );
                }

                if (state === "result") {
                  const { result } = toolInvocation;

                  // Result rendering
                  return (
                    <div
                      key={toolCallId}
                      className="flex flex-col gap-3 p-3 bg-gray-800/50 border border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center gap-2 text-gray-300">
                        {getToolIcon(toolName)}
                        <span className="font-medium capitalize">
                          {toolName.replace(/([A-Z])/g, " $1").trim()}
                        </span>
                        <span className="ml-auto flex items-center gap-2 text-green-400">
                          <span className="inline-block h-2 w-2 rounded-full bg-green-400"></span>
                          Complete
                        </span>
                      </div>

                      {/* Network scan result */}
                      {toolName === "scanNetwork" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Target:</div>
                            <div className="text-gray-200">{result.target}</div>
                            <div className="text-gray-400">Scan ID:</div>
                            <div className="text-gray-200">{result.scanId}</div>
                            <div className="text-gray-400">Estimated time:</div>
                            <div className="text-gray-200">
                              {result.estimatedTime}
                            </div>
                          </div>
                          <div className="mt-2 flex items-center gap-2 text-amber-400">
                            <AlertCircle className="h-4 w-4" />
                            <span>{result.message}</span>
                          </div>
                        </div>
                      )}

                      {/* Vulnerability scan result */}
                      {toolName === "vulnerabilityScan" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Target:</div>
                            <div className="text-gray-200">{result.target}</div>
                            <div className="text-gray-400">Scan type:</div>
                            <div className="text-gray-200">
                              {result.scanType}
                            </div>
                            <div className="text-gray-400">Scan ID:</div>
                            <div className="text-gray-200">{result.scanId}</div>
                          </div>
                          <div className="mt-2 flex items-center gap-2 text-amber-400">
                            <AlertCircle className="h-4 w-4" />
                            <span>{result.message}</span>
                          </div>
                        </div>
                      )}

                      {/* Traffic analysis result */}
                      {toolName === "analyzeTraffic" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Interface:</div>
                            <div className="text-gray-200">
                              {result.interface}
                            </div>
                            <div className="text-gray-400">Duration:</div>
                            <div className="text-gray-200">
                              {result.duration} seconds
                            </div>
                            <div className="text-gray-400">Filter:</div>
                            <div className="text-gray-200">{result.filter}</div>
                          </div>
                          <div className="mt-2 flex items-center gap-2 text-amber-400">
                            <AlertCircle className="h-4 w-4" />
                            <span>{result.message}</span>
                          </div>
                        </div>
                      )}

                      {/* Password check result */}
                      {toolName === "passwordCheck" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Strength:</div>
                            <div
                              className={cn(
                                "text-gray-200",
                                result.strength === "strong" &&
                                  "text-green-400",
                                result.strength === "medium" &&
                                  "text-amber-400",
                                result.strength === "weak" && "text-red-400"
                              )}
                            >
                              {result.strength}
                            </div>
                            <div className="text-gray-400">Special chars:</div>
                            <div
                              className={
                                result.hasSpecial
                                  ? "text-green-400"
                                  : "text-red-400"
                              }
                            >
                              {result.hasSpecial ? "Yes" : "No"}
                            </div>
                            <div className="text-gray-400">Numbers:</div>
                            <div
                              className={
                                result.hasNumbers
                                  ? "text-green-400"
                                  : "text-red-400"
                              }
                            >
                              {result.hasNumbers ? "Yes" : "No"}
                            </div>
                            <div className="text-gray-400">Uppercase:</div>
                            <div
                              className={
                                result.hasUppercase
                                  ? "text-green-400"
                                  : "text-red-400"
                              }
                            >
                              {result.hasUppercase ? "Yes" : "No"}
                            </div>
                          </div>
                          {result.recommendations &&
                            result.recommendations.length > 0 && (
                              <div className="mt-2">
                                <div className="text-gray-400 mb-1">
                                  Recommendations:
                                </div>
                                <ul className="list-disc list-inside text-amber-400 space-y-1">
                                  {result.recommendations.map(
                                    (rec: string, i: number) => (
                                      <li key={i}>{rec}</li>
                                    )
                                  )}
                                </ul>
                              </div>
                            )}
                        </div>
                      )}

                      {/* Weather result */}
                      {toolName === "getWeather" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Temperature:</div>
                            <div className="text-gray-200">
                              {result.current?.temperature_2m || "N/A"}°C
                            </div>
                            <div className="text-gray-400">Timezone:</div>
                            <div className="text-gray-200">
                              {result.timezone || "N/A"}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Pentest result */}
                      {toolName === "runPentest" && result && (
                        <div className="flex flex-col gap-2 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            <div className="text-gray-400">Target:</div>
                            <div className="text-gray-200">{result.target}</div>
                            <div className="text-gray-400">Test ID:</div>
                            <div className="text-gray-200">{result.testId}</div>
                            <div className="text-gray-400">Test type:</div>
                            <div className="text-gray-200 capitalize">
                              {result.testType}
                            </div>
                            <div className="text-gray-400">Intensity:</div>
                            <div className="text-gray-200 capitalize">
                              {result.depth}
                            </div>
                            <div className="text-gray-400">Status:</div>
                            <div className="text-amber-400 capitalize">
                              {result.status}
                            </div>
                            <div className="text-gray-400">Est. duration:</div>
                            <div className="text-gray-200">
                              {result.estimatedDuration}
                            </div>
                          </div>
                          <div className="mt-2 p-2 bg-gray-900 rounded">
                            <div className="text-gray-300 mb-1 font-medium">
                              Details:
                            </div>
                            <div className="text-gray-400">
                              {result.detailsMessage}
                            </div>
                          </div>
                          {result.note && (
                            <div className="mt-1 text-amber-400 text-xs">
                              Note: {result.note}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Fallback for other tools */}
                      {![
                        "scanNetwork",
                        "vulnerabilityScan",
                        "analyzeTraffic",
                        "passwordCheck",
                        "getWeather",
                        "runPentest",
                      ].includes(toolName) && (
                        <pre className="bg-gray-900 p-2 rounded text-xs overflow-auto">
                          {JSON.stringify(result, null, 2)}
                        </pre>
                      )}
                    </div>
                  );
                }
              }
            })}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export const PreviewMessage = memo(
  PurePreviewMessage,
  (prevProps, nextProps) => {
    if (prevProps.isLoading !== nextProps.isLoading) return false;
    if (prevProps.message.id !== nextProps.message.id) return false;
    if (!equal(prevProps.message.parts, nextProps.message.parts)) return false;

    return true;
  }
);

export const ThinkingMessage = () => {
  const role = "assistant";

  return (
    <motion.div
      data-testid="message-assistant-loading"
      className="w-full mx-auto max-w-3xl px-4 group/message "
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1, transition: { delay: 1 } }}
      data-role={role}
    >
      <div
        className={cn(
          "flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-2xl group-data-[role=user]/message:py-2 rounded-xl"
        )}
      >
        <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-gray-700">
          <SparklesIcon size={14} />
        </div>

        <div className="flex flex-col gap-2 w-full">
          <div className="flex flex-col gap-4 text-muted-foreground">
            Hmm...
          </div>
        </div>
      </div>
    </motion.div>
  );
};
