"use client";

import { useState } from "react";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";

interface Message {
    role: "user" | "bot";
    text: string;
}

export function ChatInterface() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
      {role: "bot", text: "Hi! I'm MeetOps. Ask me anything about your projects or meetings."}
  ]);
  const [input, setInput] = useState("");

  const chatMutation = useMutation({
      mutationFn: async (query: string) => {
          const res = await api.post("/chat/", { query });
          return res.data.answer;
      },
      onSuccess: (answer) => {
          setMessages(prev => [...prev, { role: "bot", text: answer }]);
      },
      onError: () => {
          setMessages(prev => [...prev, { role: "bot", text: "Sorry, I encountered an error answering that." }]);
      }
  });

  const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim()) return;

      const query = input;
      setMessages(prev => [...prev, { role: "user", text: query }]);
      setInput("");
      chatMutation.mutate(query);
  };

  return (
    <>
      {/* Floating Trigger */}
      <Button
        className={cn(
          "fixed bottom-8 right-8 h-14 w-14 rounded-full shadow-lg transition-all duration-200 z-50",
          isOpen ? "scale-0 opacity-0" : "scale-100 opacity-100"
        )}
        onClick={() => setIsOpen(true)}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Window */}
      <div
        className={cn(
          "fixed bottom-8 right-8 w-96 h-[500px] bg-background border border-border rounded-lg shadow-xl flex flex-col z-50 transition-all duration-200 origin-bottom-right",
          isOpen ? "scale-100 opacity-100 pointer-events-auto" : "scale-90 opacity-0 pointer-events-none"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold">Chat with MeetOps</h3>
          <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, i) => (
                <div key={i} className={cn("flex w-full", m.role === "user" ? "justify-end" : "justify-start")}>
                    <div className={cn(
                        "max-w-[80%] rounded-lg px-3 py-2 text-sm",
                        m.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted text-foreground"
                    )}>
                        {m.text}
                    </div>
                </div>
            ))}
            {chatMutation.isPending && (
                <div className="flex w-full justify-start">
                    <div className="bg-muted rounded-lg px-3 py-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                    </div>
                </div>
            )}
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={chatMutation.isPending}
          />
          <Button type="submit" size="icon" disabled={chatMutation.isPending}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </>
  );
}
