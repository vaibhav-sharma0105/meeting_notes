"use client";

import { BentoGrid, BentoGridItem } from "@/components/bento-grid";
import { FileUpload } from "@/components/file-upload";
import { CommandMenu } from "@/components/command-palette";
import { SettingsDialog } from "@/components/settings-dialog";
import { TaskList } from "@/components/task-list";
import { ChatInterface } from "@/components/chat-interface";
import { ModeToggle } from "@/components/theme-toggle";
import { ModeToggle } from "@/components/theme-toggle";
import { ModeToggle } from "@/components/theme-toggle";
import { Calendar as CalendarIcon, FileText, PieChart, Settings, CheckSquare } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchDashboardData, uploadMeeting } from "@/lib/api";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const queryClient = useQueryClient();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboardData,
    retry: 1, // Don't retry forever
  });

  const uploadMutation = useMutation({
    mutationFn: uploadMeeting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      alert("Upload successful!");
    },
    onError: (error) => {
        alert("Upload failed: " + error.message);
    }
  });

  const handleUpload = (file: File) => {
    uploadMutation.mutate(file);
  };

  if (isLoading) {
      return <div className="flex h-screen items-center justify-center text-muted-foreground animate-pulse">Loading MeetOps...</div>;
  }

  if (isError) {
      return (
          <div className="flex h-screen flex-col items-center justify-center gap-4">
              <div className="text-red-500 font-medium">Unable to connect to MeetOps Backend</div>
              <p className="text-sm text-muted-foreground">Ensure the backend server is running on port 8000.</p>
              <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
      );
  }

  // Fallback if API fails or returns empty
  const dashboard = data || {
      daily_focus: null,
      incoming: [],
      sentiment: [],
      top_project: null
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-50">
      <div className="w-full max-w-7xl mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold tracking-tight">MeetOps</h1>
        <div className="flex items-center gap-4">
          <div className="text-sm text-neutral-500 hidden md:block">
            Privacy-First Meeting Intelligence
          </div>
          <ModeToggle />
          <Button variant="ghost" size="icon" onClick={() => setIsSettingsOpen(true)}>
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <CommandMenu onOpenSettings={() => setIsSettingsOpen(true)} />
      <SettingsDialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen} />

      <ChatInterface />

      <BentoGrid className="w-full mx-auto">
        {/* Item 1: Daily Focus (Large) */}
        <BentoGridItem
          className="md:col-span-2"
          title={dashboard.daily_focus?.title || "No meetings today"}
          description={dashboard.daily_focus ? `Most critical meeting today: ${dashboard.daily_focus.title}` : "Upload a transcript to get started."}
          header={<div className="h-full w-full bg-neutral-100 dark:bg-neutral-900 rounded-lg flex items-center justify-center text-4xl">📅</div>}
          icon={<CalendarIcon className="h-4 w-4 text-neutral-500" />}
        />

        {/* Item 2: Quick Upload */}
        <div className="row-span-1 rounded-xl p-4 bg-white dark:bg-black border border-neutral-200 dark:border-neutral-800 flex flex-col space-y-4">
            <h3 className="font-bold text-neutral-600 dark:text-neutral-200">Ingest</h3>
            <FileUpload onUpload={handleUpload} isUploading={uploadMutation.isPending} />
        </div>

        {/* Item 3: Incoming (List) */}
        <BentoGridItem
          className="md:col-span-1"
          title="Incoming Transcripts"
          description={`${dashboard.incoming?.length || 0} unprocessed files`}
          header={
            <div className="h-full w-full bg-neutral-100 dark:bg-neutral-900 rounded-lg p-2 flex flex-col gap-2 overflow-y-auto">
              {dashboard.incoming?.map((m: any) => (
                   <div key={m.id} className="text-xs bg-white dark:bg-black p-2 rounded shadow-sm">{m.title}</div>
              ))}
              {(!dashboard.incoming || dashboard.incoming.length === 0) && <div className="text-xs text-neutral-400">No recent uploads</div>}
            </div>
          }
          icon={<FileText className="h-4 w-4 text-neutral-500" />}
        />

        {/* Item 4: Action Items */}
        <BentoGridItem
            className="md:col-span-2"
            title="My Action Items"
            description="Tasks extracted from your meetings."
            header={<div className="h-full w-full bg-white dark:bg-black p-2 rounded-lg border border-neutral-200 dark:border-neutral-800"><TaskList /></div>}
            icon={<CheckSquare className="h-4 w-4 text-neutral-500" />}
        />

        {/* Item 5: Knowledge Cluster */}
        <BentoGridItem
          className="md:col-span-1"
          title={`Project: ${dashboard.top_project?.name || "None"}`}
          description={dashboard.top_project ? `${dashboard.top_project.meeting_count} linked calls.` : "Not enough data."}
          header={<div className="h-full w-full bg-gradient-to-br from-neutral-200 to-neutral-100 dark:from-neutral-900 dark:to-neutral-800 rounded-lg"></div>}
          icon={<PieChart className="h-4 w-4 text-neutral-500" />}
        />

      </BentoGrid>
    </main>
  );
}
