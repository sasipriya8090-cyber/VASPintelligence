import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Investigation from './pages/Investigation';
import Transactions from './pages/Transactions';
import WalletGraph from './pages/WalletGraph';
import Reports from './pages/Reports';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="investigation" element={<Investigation />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="graph" element={<WalletGraph />} />
        <Route path="reports" element={<Reports />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
