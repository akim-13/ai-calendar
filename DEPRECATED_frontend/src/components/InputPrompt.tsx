import { useState, useRef } from "react";
import { Check, Plus } from "lucide-react";

interface InputPromptProps {
  setIsModalOpen: (isOpen: boolean) => void;
  setModalTypeLocked: (isLocked: boolean) => void;
  newFCEvent: React.MutableRefObject<any>;
  initialExtendedProps: Record<string, any>;
  setModalType: (isTask: string) => void;
}

interface AIResponse {
  title: string;
  description: string;
  type: "Task" | "Event";
  deadline?: string;
  durationMinutes?: string;
  priority?: number;
  start?: string;
  end?: string;
}

import { API_BASE_URL } from "../api";

export default function InputPrompt({ setIsModalOpen, setModalTypeLocked, newFCEvent, initialExtendedProps, setModalType }: InputPromptProps) {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState<AIResponse | null>(null);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    try {
      const username = "joe";
      const res = await fetch(
        `${API_BASE_URL}/autofill/${username}?description=${encodeURIComponent(
          input
        )}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) {
        throw new Error("Failed to fetch data");
      }

      const data: AIResponse = await res.json();
      setResponse(data);
      console.log("AI Response:", data);

      newFCEvent.current = { extendedProps: { ...initialExtendedProps } };
      const cur = newFCEvent.current;
      cur["title"] = data.title;
      cur.extendedProps["description"] = data.description;

      if (data.type === "Task") {
        setModalType("task");
        cur["start"] = data.deadline ?? "";
        cur.extendedProps["duration"] = data.durationMinutes ?? "";
        cur.extendedProps["priority"] = data?.priority ?? 0;
      } else {
        setModalType("standalone_event");
        cur["start"] = data.start ?? "";
        cur["end"] = data.end ?? "";
      }

      setIsModalOpen(true);
      setModalTypeLocked(false);
    } catch (error) {
      console.error("Error:", error);
    }

    setInput("");
  };

  const handleCreateEventClick = () => {
    newFCEvent.current = { extendedProps: { ...initialExtendedProps } };
    setModalType("task");
    setIsModalOpen(true);
    setModalTypeLocked(false);
  };

  return (
    <div className="flex flex-col w-full">
      <div className="flex items-center border-2 border-black rounded-3xl px-6 py-3 w-full">
        <div className="relative flex-grow">
          <input
            type="text"
            className="w-full outline-none bg-transparent text-lg px-2 pr-12 py-2"
            placeholder="Type your prompt..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />
          <button
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-full hover:bg-gray-200"
            onClick={handleSubmit}
          >
            <Check className="w-6 h-6" />
          </button>
        </div>
        <button onClick={handleCreateEventClick} className="ml-2 p-3 rounded-full hover:bg-gray-200">
          <Plus className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
