"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { Loader2, RefreshCw } from "lucide-react";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface SettingsFormValues {
  api_base: string;
  api_key: string;
  selected_model: string;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const [loading, setLoading] = useState(false);
  const [fetchingModels, setFetchingModels] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);

  const { register, handleSubmit, setValue, watch, reset } = useForm<SettingsFormValues>({
      defaultValues: {
          api_base: "https://api.openai.com/v1",
          api_key: "",
          selected_model: "gpt-4o"
      }
  });

  const apiBase = watch("api_base");
  const apiKey = watch("api_key");

  // Fetch current settings on open
  useEffect(() => {
    if (open) {
      setLoading(true);
      api.get("/settings/")
        .then((res) => {
           const data = res.data;
           setValue("api_base", data.api_base);
           setValue("api_key", data.api_key); // Will be masked
           setValue("selected_model", data.selected_model);
           // Seed with current if not fetched yet
           if (availableModels.length === 0) {
               setAvailableModels([data.selected_model, "gpt-4o", "gpt-3.5-turbo"]);
           }
        })
        .catch((err) => console.error("Failed to load settings", err))
        .finally(() => setLoading(false));
    }
  }, [open, setValue]);

  const onSubmit = async (data: SettingsFormValues) => {
    setLoading(true);
    try {
      await api.post("/settings/", data);
      onOpenChange(false);
      alert("Settings saved!");
    } catch (error) {
      alert("Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  const handleFetchModels = async () => {
      setFetchingModels(true);
      try {
          const res = await api.post("/settings/fetch-models", {
              api_base: apiBase,
              api_key: apiKey
          });
          if (res.data.models && res.data.models.length > 0) {
              setAvailableModels(res.data.models);
          } else {
              alert("No models found or provider returned empty list.");
          }
      } catch (error) {
          console.error(error);
          alert("Failed to fetch models. Check URL/Key.");
      } finally {
          setFetchingModels(false);
      }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>LLM Configuration</DialogTitle>
          <DialogDescription>
            Configure your model provider. Supports OpenAI, Anthropic, Ollama, etc.
          </DialogDescription>
        </DialogHeader>

        {loading && <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>}

        {!loading && (
            <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="api_base" className="text-right">
                Base URL
                </Label>
                <Input
                id="api_base"
                className="col-span-3"
                placeholder="https://api.openai.com/v1"
                {...register("api_base")}
                />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="api_key" className="text-right">
                API Key
                </Label>
                <Input
                id="api_key"
                type="password"
                className="col-span-3"
                placeholder="sk-..."
                {...register("api_key")}
                />
            </div>

            <div className="grid grid-cols-4 items-start gap-4">
                <Label htmlFor="model" className="text-right pt-2">
                Model
                </Label>
                <div className="col-span-3 flex flex-col gap-2">
                    <div className="flex gap-2">
                         <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            {...register("selected_model")}
                         >
                            {availableModels.map(m => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                         </select>
                         <Button type="button" size="icon" variant="outline" onClick={handleFetchModels} title="Fetch Models">
                             {fetchingModels ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                         </Button>
                    </div>
                    <span className="text-xs text-muted-foreground">
                        Click refresh to auto-populate from Base URL.
                    </span>
                </div>
            </div>

            <DialogFooter>
                <Button type="submit">Save changes</Button>
            </DialogFooter>
            </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
