"use client";

import { Message } from "ai";
import { useChat } from "@ai-sdk/react";

import { MultimodalInput } from "./MultimodalInput";
import { Messages } from "./Messages";

export function Chat({
  id,
  initialMessages,
}: {
  id: string;
  initialMessages: Array<Message>;
}) {
  const {
    messages,
    handleSubmit,
    input,
    setInput,
    append,
    status,
    stop,
    setMessages,
    reload,
  } = useChat({
    id,
    body: { id },
    initialMessages,
    maxSteps: 10,
    onFinish: () => {
      console.log("finished");
    },
  });

  return (
    <div className="flex flex-col min-w-0 h-dvh">
      <Messages
        chatId={id}
        status={status}
        messages={messages}
        setMessages={setMessages}
        reload={reload}
        isReadonly={false}
      />
      <form className="flex mx-auto px-4 pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput
          input={input}
          setInput={setInput}
          handleSubmit={handleSubmit}
          status={status}
          stop={stop}
          messages={messages}
          append={append}
          chatId={id}
          setMessages={setMessages}
        />
      </form>
    </div>
  );
}
