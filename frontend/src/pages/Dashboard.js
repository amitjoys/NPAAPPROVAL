import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import MainLayout from '../components/layout/MainLayout';
import StatCard from '../components/common/StatCard';
import StatusBadge from '../components/common/StatusBadge';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { 
  FileText, 
  CheckCircle, 
  Clock, 
  Plus, 
  TrendingUp,
  Users,
  ShoppingBag,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const Dashboard = () => {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [nfas, setNfas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const requests = [
        api.get('/reports/dashboard'),
        api.get('/nfa/my-nfas?limit=5')
      ];

      if (hasRole('superadmin')) {
        requests.push(api.get('/reports/nfa-analytics?days=30'));
      }

      const responses = await Promise.all(requests);
      setStats(responses[0].data);
      setNfas(responses[1].data);
      if (responses[2]) {
        setAnalytics(responses[2].data);
      }
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="Dashboard" fullWidth>
      <div data-testid="dashboard-page">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-600">Here's what's happening with your NFAs today</p>
        </div>

        {/* Stats Cards - Requestor */}
        {(hasRole('requestor') || hasRole('superadmin')) && stats?.requestor && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total NFAs"
              value={stats.requestor.total}
              icon={FileText}
              color="indigo"
              description="All time"
              onClick={() => navigate('/my-nfas')}
            />
            <StatCard
              title="Pending"
              value={stats.requestor.pending}
              icon={Clock}
              color="orange"
              description="Awaiting approval"
            />
            <StatCard
              title="Approved"
              value={stats.requestor.approved}
              icon={CheckCircle}
              color="green"
              trend="up"
              trendValue="+12%"
            />
            <StatCard
              title="This Month"
              value={stats.requestor.this_month || 0}
              icon={TrendingUp}
              color="purple"
              description="Current month"
            />
          </div>
        )}

        {/* Approver Stats */}
        {hasRole('approver') && stats?.approver && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">Your Approval Tasks</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Pending Approvals"
                value={stats.approver.pending}
                icon={Clock}
                color="orange"
                onClick={() => navigate('/approvals')}
              />
              <StatCard
                title="Approved"
                value={stats.approver.approved}
                icon={CheckCircle}
                color="green"
              />
              <StatCard
                title="Rejected"
                value={stats.approver.rejected}
                icon={FileText}
                color="red"
              />
              <StatCard
                title="Total Processed"
                value={stats.approver.total}
                icon={Activity}
                color="blue"
              />
            </div>
          </div>
        )}

        {/* Admin Stats */}
        {hasRole('superadmin') && stats?.admin && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">System Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard
                title="Total Users"
                value={stats.admin.total_users}
                icon={Users}
                color="purple"
                onClick={() => navigate('/admin/users')}
              />
              <StatCard
                title="Total NFAs"
                value={stats.admin.total_nfas}
                icon={FileText}
                color="indigo"
              />
              <StatCard
                title="Total Vendors"
                value={stats.admin.total_vendors}
                icon={ShoppingBag}
                color="blue"
                onClick={() => navigate('/admin/vendors')}
              />
            </div>
          </div>
        )}

        {/* Charts & Analytics - For SuperAdmin */}
        {hasRole('superadmin') && analytics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>NFA Status Distribution</CardTitle>
                <CardDescription>Last 30 days</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analytics.by_status}
                      dataKey="count"
                      nameKey="_id"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label
                    >
                      {analytics.by_status.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Department Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>NFAs by Department</CardTitle>
                <CardDescription>Last 30 days</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics.by_department}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="_id" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#6366f1" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Quick Actions & Recent NFAs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and operations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {(hasRole('requestor') || hasRole('superadmin')) && (
                <Button 
                  onClick={() => navigate('/nfa/create')} 
                  className="w-full justify-start h-12 bg-gradient-to-r from-indigo-600 to-blue-500 hover:from-indigo-700 hover:to-blue-600"
                  data-testid="create-nfa-button"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create New NFA Request
                </Button>
              )}
              {hasRole('approver') && (
                <Button 
                  onClick={() => navigate('/approvals')} 
                  className="w-full justify-start h-12" 
                  variant="outline"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  View Pending Approvals
                  {stats?.approver?.pending > 0 && (
                    <span className="ml-auto bg-orange-100 text-orange-800 px-2 py-0.5 rounded-full text-xs font-medium">
                      {stats.approver.pending}
                    </span>
                  )}
                </Button>
              )}
              {hasRole('coordinator') && (
                <Button 
                  onClick={() => navigate('/coordinator')} 
                  className="w-full justify-start h-12" 
                  variant="outline"
                >
                  <Activity className="w-5 h-5 mr-2" />
                  Coordinator Tasks
                </Button>
              )}
              {hasRole('superadmin') && (
                <>
                  <Button 
                    onClick={() => navigate('/admin/users')} 
                    className="w-full justify-start h-12" 
                    variant="outline"
                  >
                    <Users className="w-5 h-5 mr-2" />
                    Manage Users
                  </Button>
                  <Button 
                    onClick={() => navigate('/reports')} 
                    className="w-full justify-start h-12" 
                    variant="outline"
                  >
                    <TrendingUp className="w-5 h-5 mr-2" />
                    View Reports & Analytics
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {/* Recent NFAs */}
          <Card>
            <CardHeader>
              <CardTitle>Recent NFAs</CardTitle>
              <CardDescription>Your latest requests</CardDescription>
            </CardHeader>
            <CardContent>
              {nfas.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">No NFAs created yet</p>
                  <Button onClick={() => navigate('/nfa/create')} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First NFA
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {nfas.map((nfa) => (
                    <div 
                      key={nfa.id}
                      className="p-4 border border-gray-200 rounded-lg hover:shadow-md hover:border-indigo-200 cursor-pointer transition-all"
                      onClick={() => navigate(`/nfa/${nfa.id}`)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <span className="font-semibold text-gray-900 text-sm">
                            {nfa.nfa_number || `NFA-${nfa.id.substring(0, 8)}`}
                          </span>
                        </div>
                        <StatusBadge status={nfa.status} />
                      </div>
                      <p className="text-sm text-gray-600 truncate mb-2">
                        {nfa.section1_data?.subject_item || 'No subject'}
                      </p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{nfa.section1_data?.department || 'N/A'}</span>
                        <span>{new Date(nfa.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                  <Button 
                    onClick={() => navigate('/my-nfas')} 
                    variant="ghost" 
                    className="w-full text-indigo-600 hover:text-indigo-700"
                  >
                    View All NFAs →
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default Dashboard;
