"use client";
import React, { useRef, useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FileUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export const FileUpload = ({ onUpload, isUploading }: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onUpload(file);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center p-4 border-2 border-dashed border-neutral-200 dark:border-neutral-800 rounded-lg">
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
            "Drop transcript (VTT) or summary (JSON) here"
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
  );
};
