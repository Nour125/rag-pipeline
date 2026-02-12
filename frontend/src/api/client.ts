import axios from "axios";
// Create an Axios instance with the base URL of the backend API
export const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
});
