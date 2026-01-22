"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { Loader2, Trash2, Edit2, User, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Task {
  id: string;
  description: string;
  assignee?: string;
  status: "todo" | "done";
  due_date?: string;
}

export function TaskList() {
  const queryClient = useQueryClient();
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const { data: tasks, isLoading } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: async () => {
      const res = await api.get("/tasks/");
      return res.data;
    },
  });

  const toggleMutation = useMutation({
    mutationFn: async (taskId: string) => {
      await api.patch(`/tasks/${taskId}/toggle`);
    },
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previousTasks = queryClient.getQueryData<Task[]>(["tasks"]);
      queryClient.setQueryData<Task[]>(["tasks"], (old) =>
        old?.map(t => t.id === taskId ? { ...t, status: t.status === "todo" ? "done" : "todo" } : t)
      );
      return { previousTasks };
    },
    onError: (err, newTodo, context) => {
      queryClient.setQueryData(["tasks"], context?.previousTasks);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const updateMutation = useMutation({
      mutationFn: async (vars: {id: string, data: Partial<Task>}) => {
          await api.patch(`/tasks/${vars.id}`, vars.data);
      },
      onSuccess: () => {
          setEditingTask(null);
          queryClient.invalidateQueries({ queryKey: ["tasks"] });
      }
  });

  const deleteMutation = useMutation({
      mutationFn: async (id: string) => {
          await api.delete(`/tasks/${id}`);
      },
      onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["tasks"] });
      }
  });

  if (isLoading) return <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>;

  if (!tasks || tasks.length === 0) {
      return <div className="text-sm text-neutral-500 p-4 text-center">No action items found. Upload meetings to generate them.</div>;
  }

  return (
    <div className="flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-2">
      {tasks.map((task) => (
        <div key={task.id} className="group flex items-start space-x-2 p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-900 transition-colors">
          <Checkbox
            id={task.id}
            checked={task.status === "done"}
            onCheckedChange={() => toggleMutation.mutate(task.id)}
            className="mt-1"
          />
          <div className="flex-1 min-w-0">
            <label
              htmlFor={task.id}
              className={cn(
                "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer block break-words",
                task.status === "done" && "line-through text-muted-foreground"
              )}
            >
              {task.description}
            </label>
            <div className="flex gap-4 mt-1">
                {(task.assignee || task.due_date) && (
                    <p className="text-xs text-muted-foreground flex gap-3">
                        {task.assignee && <span className="flex items-center gap-1"><User className="w-3 h-3" /> {task.assignee}</span>}
                        {task.due_date && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(task.due_date).toLocaleDateString()}</span>}
                    </p>
                )}
            </div>
          </div>
          <div className="flex opacity-0 group-hover:opacity-100 transition-opacity gap-1">
              <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => setEditingTask(task)}>
                  <Edit2 className="h-3 w-3" />
              </Button>
              <Button size="icon" variant="ghost" className="h-6 w-6 text-red-500 hover:text-red-600" onClick={() => deleteMutation.mutate(task.id)}>
                  <Trash2 className="h-3 w-3" />
              </Button>
          </div>
        </div>
      ))}

      <Dialog open={!!editingTask} onOpenChange={(open) => !open && setEditingTask(null)}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Edit Task</DialogTitle>
            </DialogHeader>
            {editingTask && (
                <form className="space-y-4" onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.currentTarget);
                    updateMutation.mutate({
                        id: editingTask.id,
                        data: {
                            description: formData.get("description") as string,
                            assignee: formData.get("assignee") as string
                        }
                    });
                }}>
                    <div>
                        <Label>Description</Label>
                        <Input name="description" defaultValue={editingTask.description} />
                    </div>
                    <div>
                        <Label>Assignee</Label>
                        <Input name="assignee" defaultValue={editingTask.assignee || ""} />
                    </div>
                    <DialogFooter>
                        <Button type="submit">Save</Button>
                    </DialogFooter>
                </form>
            )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
