import type { RagTurn } from "../../types/rag";
import RagTurnCard from "../cards/RagTurnCard";

type Props = {
  turns: RagTurn[];
};

export default function ConversationTimeline({ turns }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {turns.map((t) => (
        <RagTurnCard key={t.id} turn={t} />
      ))}
    </div>
  );
}
