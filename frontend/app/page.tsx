
"use client";

import { useState, useRef, useEffect } from "react";
import { 
  Send, 
  Calendar as CalendarIcon, 
  Bot, 
  User, 
  Loader2, 
  ChevronLeft, 
  ChevronRight,
  RefreshCw // <--- Import Refresh Icon
} from "lucide-react";
import ReactMarkdown from "react-markdown";

// --- CONFIGURATION ---
// Base URL without the random parameters
const BASE_CALENDAR_URL = "https://calendar.google.com/calendar/embed?src=ff2ab0b36339f9dba9e7b5fd13852e648885a49269c22b6826b0c569500ec6c4%40group.calendar.google.com&ctz=Europe%2FParis&showTitle=0&showPrint=0&showCalendars=0&showTz=0&mode=WEEK";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am PlanIQ. I manage the Demo Calendar. You can open the panel on the right ➡ to see your schedule live.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  
  // State to force refresh the iframe
  const [calendarUrl, setCalendarUrl] = useState(BASE_CALENDAR_URL);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Function to bust cache
  const refreshCalendar = () => {
    // We add a random timestamp to the URL to force a reload
    const newUrl = `${BASE_CALENDAR_URL}&nocache=${Date.now()}`;
    setCalendarUrl(newUrl);
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userContent = input;
    setInput("");
    setIsLoading(true);

    const newHistory: Message[] = [...messages, { role: "user", content: userContent }];
    setMessages(newHistory);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: newHistory }),
      });

      if (!response.ok) throw new Error("Network response was not ok");

      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      
      // Auto-open AND Refresh calendar if success
      if (data.response.toLowerCase().includes("done") || data.response.toLowerCase().includes("schedule") || data.response.toLowerCase().includes("book")) {
        setIsCalendarOpen(true);
        setTimeout(refreshCalendar, 1000); // Wait 1s for Google to process, then refresh
      }

    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Could not connect to PlanIQ Brain. Check port 8080." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 font-sans overflow-hidden relative">
      
      {/* --- LEFT PANEL: CHAT --- */}
      <div 
        className={`
          flex flex-col h-full transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)]
          ${isCalendarOpen ? 'w-full md:w-[50%] lg:w-[60%]' : 'w-full'}
        `}
      >
        <header className="flex items-center gap-3 border-b border-slate-800 bg-slate-900/50 p-4 backdrop-blur-md">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-500/20">
            <CalendarIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">PlanIQ</h1>
            <p className="text-xs text-slate-400">Agentic Calendar Assistant</p>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-700">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-600 mt-1 shadow-md">
                  <Bot className="h-5 w-5 text-white" />
                </div>
              )}
              <div className={`relative max-w-[85%] rounded-2xl px-5 py-3 shadow-md transition-all ${
                msg.role === "user" ? "bg-indigo-600 text-white rounded-br-none" : "bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700"
              }`}>
                <div className="prose prose-invert text-sm leading-relaxed">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start gap-4">
               <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-600">
                  <Bot className="h-5 w-5 text-white" />
                </div>
              <div className="flex items-center gap-2 rounded-2xl bg-slate-800 px-5 py-3 border border-slate-700">
                <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
                <span className="text-sm text-slate-400">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-slate-800 bg-slate-900 p-4">
          <div className="mx-auto max-w-4xl relative flex items-center gap-2 rounded-xl bg-slate-800 p-2 border border-slate-700 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all shadow-lg">
            <input
              type="text"
              placeholder="Ex: Schedule a meeting with Bob tomorrow at 2 PM..."
              className="flex-1 bg-transparent px-4 py-2 text-sm text-white placeholder-slate-400 focus:outline-none"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="rounded-lg bg-indigo-600 p-2 text-white transition hover:bg-indigo-500 disabled:opacity-50"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* --- RIGHT PANEL: CALENDAR (Collapsible) --- */}
      <div 
        className={`
          relative h-full bg-white border-l border-slate-800 shadow-2xl
          transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] overflow-hidden
          ${isCalendarOpen ? 'w-full md:w-[50%] lg:w-[40%] translate-x-0 opacity-100' : 'w-0 translate-x-full opacity-0'}
        `}
      >
         {/* REFRESH BUTTON OVERLAY */}
         <button 
           onClick={refreshCalendar}
           className="absolute top-4 right-4 z-10 bg-white/80 p-2 rounded-full shadow-md hover:bg-white transition-colors text-slate-700 border border-slate-200"
           title="Force Refresh Calendar"
         >
           <RefreshCw className="h-4 w-4" />
         </button>

        <iframe
          src={calendarUrl} // Uses the State URL
          style={{ border: 0 }}
          width="100%"
          height="100%"
          frameBorder="0"
          scrolling="no"
          title="PlanIQ Live Calendar"
          className="w-full h-full"
        ></iframe>
      </div>

      {/* --- FLOATING TOGGLE BUTTON --- */}
      <button
        onClick={() => setIsCalendarOpen(!isCalendarOpen)}
        className={`
          absolute top-1/2 -translate-y-1/2 z-50
          flex h-12 w-8 items-center justify-center 
          rounded-l-xl border-y border-l border-indigo-500/30 bg-indigo-600/90 backdrop-blur-md text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]
          transition-all duration-500 ease-in-out hover:w-10 hover:bg-indigo-500
          ${isCalendarOpen ? 'right-[50%] lg:right-[40%]' : 'right-0'}
        `}
      >
        {isCalendarOpen ? (
          <ChevronRight className="h-5 w-5" />
        ) : (
          <ChevronLeft className="h-5 w-5 animate-pulse" />
        )}
      </button>

    </div>
  );
}