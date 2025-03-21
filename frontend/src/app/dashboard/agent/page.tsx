import { Chat } from "@/components/agent/Chat";
import { DataStreamHandler } from "@/components/agent/DataStreamHandler";
import { generateId } from "ai";

export default function AgentPage() {
  const id = generateId();
  return (
    <>
      <Chat id={id} initialMessages={[]} />
      <DataStreamHandler id={id} />
    </>
  );
}
