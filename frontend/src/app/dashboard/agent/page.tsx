import { Chat } from "@/components/agent/Chat";
import { generateId } from "ai";

export default function AgentPage() {
  const id = generateId();
  return <Chat id={id} initialMessages={[]} />;
}
