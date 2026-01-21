import axios from "axios";

// In production, this should be an env var. For MVP local dev:
const API_URL = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

export interface DashboardData {
  daily_focus: any;
  incoming: any[];
  sentiment: any[];
  top_project: any;
}

export const fetchDashboardData = async (): Promise<DashboardData> => {
  const response = await api.get("/dashboard");
  return response.data;
};

export const uploadMeeting = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};
