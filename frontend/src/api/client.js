import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "";

const api = axios.create({ baseURL: BASE, timeout: 120_000 });

export const fetchHospitals  = ()      => api.get("/api/hospitals").then(r => r.data);
export const fetchGraphInfo   = ()      => api.get("/api/graph").then(r => r.data);
export const findRoute = (payload)      => api.post("/api/route", payload).then(r => r.data);
