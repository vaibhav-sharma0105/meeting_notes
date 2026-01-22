"use client";
import React, { useRef, useState } from "react";
import { Upload, FileText, ClipboardPaste } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export const FileUpload = ({ onUpload, isUploading }: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [pastedText, setPastedText] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onUpload(file);
    }
  };

  const handlePasteSubmit = () => {
    if (!pastedText.trim()) return;

    // Create a synthetic file object
    const blob = new Blob([pastedText], { type: "text/plain" });
    const file = new File([blob], `pasted_notes_${new Date().toISOString()}.txt`, { type: "text/plain" });
    onUpload(file);
    setPastedText(""); // Clear after submit
  };

  return (
    <div className="w-full">
        <Tabs defaultValue="file" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-2">
                <TabsTrigger value="file">File Upload</TabsTrigger>
                <TabsTrigger value="paste">Paste Text</TabsTrigger>
            </TabsList>

            <TabsContent value="file">
                <div className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-neutral-200 dark:border-neutral-800 rounded-lg h-[200px]">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        className="hidden"
                        accept=".vtt,.txt,.json"
                    />
                    <div className="flex flex-col items-center gap-2">
                        <Upload className="w-8 h-8 text-neutral-500" />
                        <p className="text-sm text-neutral-500 text-center">
                        {fileName ? (
                            <span className="font-semibold text-primary">{fileName}</span>
                        ) : (
                            "Drop VTT, JSON, or TXT here"
                        )}
                        </p>
                        <Button
                        variant="outline"
                        size="sm"
                        disabled={isUploading}
                        onClick={() => fileInputRef.current?.click()}
                        >
                        {isUploading ? "Uploading..." : "Select File"}
                        </Button>
                    </div>
                </div>
            </TabsContent>

            <TabsContent value="paste">
                <div className="flex flex-col gap-2 h-[200px]">
                    <Textarea
                        placeholder="Paste meeting notes or summary here..."
                        className="flex-1 resize-none"
                        value={pastedText}
                        onChange={(e) => setPastedText(e.target.value)}
                    />
                    <Button
                        size="sm"
                        onClick={handlePasteSubmit}
                        disabled={!pastedText.trim() || isUploading}
                    >
                        {isUploading ? "Analyzing..." : "Analyze Notes"}
                    </Button>
                </div>
            </TabsContent>
        </Tabs>
    </div>
  );
};
