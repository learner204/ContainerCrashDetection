# Deployment Guide

This project is configured to be deployed with **Render** for the Python backend and **Vercel** for the React frontend.

## 1. Backend (Render)

1. Create a free account on [Render](https://render.com).
2. Connect your GitHub repository.
3. In the Render Dashboard, click **New +** > **Blueprint**.
4. Select your repository.
5. Render will automatically detect the `render.yaml` file in the root directory and set up the web service.
6. Once deployed, note your backend URL (e.g., `https://container-crash-backend.onrender.com`).

## 2. Frontend (Vercel)

1. Create a free account on [Vercel](https://vercel.com).
2. Click **Add New...** > **Project** and import your GitHub repository.
3. Vercel will automatically detect that this is a Vite project.
4. Before clicking **Deploy**, configure the following **Environment Variables**:
   - `VITE_API_URL`: Set this to your Render backend URL with `/api` appended (e.g., `https://container-crash-backend.onrender.com/api`)
   - `VITE_WS_URL`: Set this to your Render backend WebSocket URL (e.g., `wss://container-crash-backend.onrender.com/ws/stream`)
5. Click **Deploy**.

## 3. Verify

Once both are deployed, open your Vercel frontend URL. It will automatically connect to your Render backend!
