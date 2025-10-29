import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { cn } from '../../lib/utils';

const MainLayout = ({ children, title, breadcrumbs, fullWidth = false }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-64 transition-all duration-300">
        <Header title={title} breadcrumbs={breadcrumbs} />
        <main className="pt-16">
          <div className={cn(
            'p-6',
            !fullWidth && 'max-w-7xl mx-auto'
          )}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
