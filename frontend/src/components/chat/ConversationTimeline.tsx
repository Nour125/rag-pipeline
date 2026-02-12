import type { RagTurn } from "../../types/rag";
import RagTurnCard from "../cards/RagTurnCard";

type Props = {
  // Ordered list of conversation turns shown in the timeline.
  turns: RagTurn[];
};

/**
 * Renders the full conversation timeline by mapping turns to RagTurnCard items.
 */
export default function ConversationTimeline({ turns }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {turns.map((t) => (
        <RagTurnCard key={t.id} turn={t} />
      ))}
    </div>
  );
}
