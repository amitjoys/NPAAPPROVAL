import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { FileText, CheckCircle, Clock, Plus, LogOut, BarChart3, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

const Dashboard = () => {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [nfas, setNfas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, nfasRes] = await Promise.all([
        api.get('/reports/dashboard'),
        api.get('/nfa/my-nfas?limit=5')
      ]);
      setStats(statsRes.data);
      setNfas(nfasRes.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { variant: 'secondary', label: 'Draft' },
      section1_pending: { variant: 'warning', label: 'Section 1 Pending', className: 'bg-orange-100 text-orange-800' },
      section1_approved: { variant: 'default', label: 'Section 1 Approved', className: 'bg-blue-100 text-blue-800' },
      section2_pending: { variant: 'warning', label: 'Section 2 Pending', className: 'bg-orange-100 text-orange-800' },
      approved: { variant: 'default', label: 'Approved', className: 'bg-green-100 text-green-800' },
      rejected: { variant: 'destructive', label: 'Rejected', className: 'bg-red-100 text-red-800' },
    };
    const config = statusConfig[status] || statusConfig.draft;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div data-testid="dashboard-page" className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold gradient-text">HCIL NFA System</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, <strong>{user?.name}</strong></span>
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" /> Logout
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Dashboard</h2>
          <p className="text-gray-600">Manage your NFA requests and approvals</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total NFAs</CardTitle>
              <FileText className="h-4 w-4 text-indigo-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.requestor?.total || 0}</div>
              <p className="text-xs text-gray-500">All submitted requests</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.requestor?.pending || 0}</div>
              <p className="text-xs text-gray-500">Awaiting approval</p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.requestor?.approved || 0}</div>
              <p className="text-xs text-gray-500">Completed requests</p>
            </CardContent>
          </Card>
        </div>

        {hasRole('approver') && stats?.approver && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Your Approvals</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-orange-600">{stats.approver.pending}</div>
                  <p className="text-sm text-gray-600">Pending Approvals</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-green-600">{stats.approver.approved}</div>
                  <p className="text-sm text-gray-600">Approved</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-red-600">{stats.approver.rejected}</div>
                  <p className="text-sm text-gray-600">Rejected</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-gray-600">{stats.approver.total}</div>
                  <p className="text-sm text-gray-600">Total</p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and operations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={() => navigate('/nfa/create')} 
                className="w-full justify-start h-12 bg-gradient-to-r from-indigo-600 to-blue-500 hover:from-indigo-700 hover:to-blue-600"
                data-testid="create-nfa-button"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create New NFA Request
              </Button>
              {hasRole('approver') && (
                <Button 
                  onClick={() => navigate('/approvals')} 
                  className="w-full justify-start h-12" 
                  variant="outline"
                >
                  <AlertCircle className="w-5 h-5 mr-2" />
                  View Pending Approvals {stats?.approver?.pending > 0 && (
                    <Badge className="ml-auto bg-orange-600">{stats.approver.pending}</Badge>
                  )}
                </Button>
              )}
              {hasRole('superadmin') && (
                <Button 
                  className="w-full justify-start h-12" 
                  variant="outline"
                >
                  <BarChart3 className="w-5 h-5 mr-2" />
                  View Reports & Analytics
                </Button>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent NFAs</CardTitle>
              <CardDescription>Your latest requests</CardDescription>
            </CardHeader>
            <CardContent>
              {nfas.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No NFAs created yet
                </div>
              ) : (
                <div className="space-y-3">
                  {nfas.map((nfa) => (
                    <div 
                      key={nfa.id}
                      className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/nfa/${nfa.id}`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">
                          {nfa.nfa_number || nfa.id.substring(0, 8)}
                        </span>
                        {getStatusBadge(nfa.status)}
                      </div>
                      <p className="text-sm text-gray-600 truncate">
                        {nfa.section1_data?.subject_item || 'No subject'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(nfa.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
