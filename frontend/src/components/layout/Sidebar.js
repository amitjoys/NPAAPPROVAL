import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  FileText,
  CheckSquare,
  Users,
  ShoppingBag,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  FileCheck,
  UserCheck,
  Shield
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { hasRole } = useAuth();

  const menuItems = [
    {
      title: 'Dashboard',
      icon: LayoutDashboard,
      path: '/',
      roles: ['requestor', 'approver', 'coordinator', 'central_reviewer', 'superadmin']
    },
    {
      title: 'My NFAs',
      icon: FileText,
      path: '/my-nfas',
      roles: ['requestor', 'approver', 'coordinator', 'central_reviewer', 'superadmin']
    },
    {
      title: 'Create NFA',
      icon: FileCheck,
      path: '/nfa/create',
      roles: ['requestor', 'superadmin']
    },
    {
      title: 'Approvals',
      icon: CheckSquare,
      path: '/approvals',
      roles: ['approver', 'central_reviewer', 'superadmin']
    },
    {
      title: 'Coordinator Tasks',
      icon: UserCheck,
      path: '/coordinator',
      roles: ['coordinator', 'superadmin']
    },
    {
      title: 'Reports',
      icon: BarChart3,
      path: '/reports',
      roles: ['approver', 'coordinator', 'central_reviewer', 'superadmin']
    },
    {
      type: 'divider',
      roles: ['superadmin']
    },
    {
      title: 'Admin',
      icon: Shield,
      path: '/admin',
      roles: ['superadmin'],
      subItems: [
        { title: 'Users', path: '/admin/users' },
        { title: 'Vendors', path: '/admin/vendors' },
        { title: 'Settings', path: '/admin/settings' }
      ]
    }
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const canAccessItem = (item) => {
    if (!item.roles) return true;
    return item.roles.some(role => hasRole(role));
  };

  return (
    <div
      className={cn(
        'fixed left-0 top-0 h-screen bg-white border-r border-gray-200 transition-all duration-300 z-40',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">H</span>
            </div>
            <span className="font-bold text-gray-800">HCIL NFA</span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className="p-2 overflow-y-auto h-[calc(100vh-4rem)]">
        {menuItems.map((item, index) => {
          if (!canAccessItem(item)) return null;

          if (item.type === 'divider') {
            return <div key={index} className="my-2 border-t border-gray-200" />;
          }

          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <div key={index}>
              <button
                onClick={() => navigate(item.path)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 mb-1',
                  active
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-500 text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100',
                  collapsed && 'justify-center'
                )}
                title={collapsed ? item.title : ''}
              >
                <Icon className={cn('w-5 h-5', active ? 'text-white' : 'text-gray-600')} />
                {!collapsed && (
                  <span className="font-medium text-sm">{item.title}</span>
                )}
              </button>

              {/* Sub-items for Admin */}
              {!collapsed && item.subItems && active && (
                <div className="ml-4 mt-1 space-y-1">
                  {item.subItems.map((subItem, subIndex) => (
                    <button
                      key={subIndex}
                      onClick={() => navigate(subItem.path)}
                      className={cn(
                        'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
                        location.pathname === subItem.path
                          ? 'bg-indigo-50 text-indigo-600 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                      )}
                    >
                      {subItem.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;
