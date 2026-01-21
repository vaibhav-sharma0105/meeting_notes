"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface Task {
  id: string;
  description: string;
  assignee?: string;
  status: "todo" | "done";
  due_date?: string;
}

export function TaskList() {
  const queryClient = useQueryClient();

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
      // Optimistic update
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

  if (isLoading) return <div className="flex justify-center p-4"><Loader2 className="animate-spin" /></div>;

  if (!tasks || tasks.length === 0) {
      return <div className="text-sm text-neutral-500 p-4 text-center">No action items found.</div>;
  }

  return (
    <div className="flex flex-col gap-2 max-h-[300px] overflow-y-auto">
      {tasks.map((task) => (
        <div key={task.id} className="flex items-start space-x-2 p-2 rounded hover:bg-neutral-100 dark:hover:bg-neutral-900">
          <Checkbox
            id={task.id}
            checked={task.status === "done"}
            onCheckedChange={() => toggleMutation.mutate(task.id)}
          />
          <div className="grid gap-1.5 leading-none">
            <label
              htmlFor={task.id}
              className={cn(
                "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer",
                task.status === "done" && "line-through text-muted-foreground"
              )}
            >
              {task.description}
            </label>
            {(task.assignee || task.due_date) && (
                <p className="text-xs text-muted-foreground">
                    {task.assignee && <span className="mr-2">👤 {task.assignee}</span>}
                    {task.due_date && <span>📅 {new Date(task.due_date).toLocaleDateString()}</span>}
                </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
