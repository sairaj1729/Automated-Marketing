import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Generate from "./pages/Generate";
import Analytics from "./pages/Analytics";
import Schedule from "./pages/Schedule";
import SettingsPage from "./pages/SettingsPage";
import LinkedInCallback from "./pages/LinkedInCallback";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";

// Simple authentication check component
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  const location = useLocation();
  
  if (!isAuthenticated) {
    // Redirect to login with return URL
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  
  return children;
};

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route path="/" element={
            localStorage.getItem('token') ? 
            <Layout><Dashboard /></Layout> : 
            <Navigate to="/login" replace />
          } />
          <Route path="/generate" element={
            localStorage.getItem('token') ? 
            <Layout><Generate /></Layout> : 
            <Navigate to="/login" replace />
          } />
          <Route path="/analytics" element={
            localStorage.getItem('token') ? 
            <Layout><Analytics /></Layout> : 
            <Navigate to="/login" replace />
          } />
          <Route path="/schedule" element={
            localStorage.getItem('token') ? 
            <Layout><Schedule /></Layout> : 
            <Navigate to="/login" replace />
          } />
          <Route path="/settings" element={
            localStorage.getItem('token') ? 
            <Layout><SettingsPage /></Layout> : 
            <Navigate to="/login" replace />
          } />
          <Route path="/callback" element={
            localStorage.getItem('token') ? 
            <Layout><LinkedInCallback /></Layout> : 
            <Navigate to="/login" replace />
          } />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;