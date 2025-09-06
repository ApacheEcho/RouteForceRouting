import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import React from 'react';
const Dashboard = React.lazy(() => import('./components/Dashboard/Dashboard'));
const HomePage = React.lazy(() => import('./components/HomePage/HomePage'));
const Analytics = React.lazy(() => import('./components/Analytics/Analytics'));
const RouteGenerator = React.lazy(() => import('./components/RouteGenerator/RouteGenerator'));
const Auth = React.lazy(() => import('./components/Auth/Auth'));
const NotFound = React.lazy(() => import('./components/NotFound/NotFound'));
const PlaybookGUI = React.lazy(() => import('./components/PlaybookGUI/PlaybookGUI'));
const Connections = React.lazy(() => import('./components/Connections/Connections'));
import Header from './components/layout/Header';

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    x: 20,
  },
  in: {
    opacity: 1,
    x: 0,
  },
  out: {
    opacity: 0,
    x: -20,
  },
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.3,
};

// Animated Route wrapper component
const AnimatedRoute = ({ children }: { children: React.ReactNode }) => {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      className="w-full"
    >
      {children}
    </motion.div>
  );
};

// Main App routes component
function AppRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<AnimatedRoute><HomePage /></AnimatedRoute>} />
        <Route path="/dashboard" element={<AnimatedRoute><Dashboard /></AnimatedRoute>} />
        <Route path="/analytics" element={<AnimatedRoute><Analytics /></AnimatedRoute>} />
        <Route path="/generate" element={<AnimatedRoute><RouteGenerator /></AnimatedRoute>} />
        <Route path="/playbook" element={<AnimatedRoute><PlaybookGUI /></AnimatedRoute>} />
        <Route path="/connections" element={<AnimatedRoute><Connections /></AnimatedRoute>} />
        <Route path="/auth" element={<AnimatedRoute><Auth /></AnimatedRoute>} />
        <Route path="*" element={<AnimatedRoute><NotFound /></AnimatedRoute>} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <React.Suspense fallback={<div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div></div>}>
            <AppRoutes />
          </React.Suspense>
        </main>
      </div>
    </Router>
  );
}

export default App;
