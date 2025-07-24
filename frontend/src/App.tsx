import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Dashboard from './components/Dashboard/Dashboard';
import HomePage from './components/HomePage/HomePage';
import Analytics from './components/Analytics/Analytics';
import RouteGenerator from './components/RouteGenerator/RouteGenerator';
import Auth from './components/Auth/Auth';
import NotFound from './components/NotFound/NotFound';
import PlaybookGUI from './components/PlaybookGUI/PlaybookGUI';

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
        <Route path="/auth" element={<AnimatedRoute><Auth /></AnimatedRoute>} />
        <Route path="*" element={<AnimatedRoute><NotFound /></AnimatedRoute>} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <AppRoutes />
        </div>
      </div>
    </Router>
  );
}

export default App;
