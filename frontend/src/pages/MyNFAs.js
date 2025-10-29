import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import StatusBadge from '../components/common/StatusBadge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  Search, 
  Filter, 
  Plus, 
  FileText,
  Calendar,
  Building,
  DollarSign
} from 'lucide-react';
import api from '../utils/api';
import { toast } from 'sonner';

const MyNFAs = () => {
  const navigate = useNavigate();
  const [nfas, setNfas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchNFAs();
  }, []);

  const fetchNFAs = async () => {
    try {
      const response = await api.get('/nfa/my-nfas');
      setNfas(response.data);
    } catch (error) {
      toast.error('Failed to load NFAs');
    } finally {
      setLoading(false);
    }
  };

  const filteredNFAs = nfas.filter(nfa => {
    const matchesSearch = 
      (nfa.nfa_number && nfa.nfa_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (nfa.section1_data?.subject_item && nfa.section1_data.subject_item.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (nfa.id && nfa.id.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || nfa.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const breadcrumbs = [
    { label: 'Dashboard', path: '/' },
    { label: 'My NFAs' }
  ];

  if (loading) {
    return (
      <MainLayout title="My NFAs" breadcrumbs={breadcrumbs}>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout title="My NFAs" breadcrumbs={breadcrumbs}>
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">My NFA Requests</h2>
          <p className="text-gray-600 mt-1">Manage and track all your NFA submissions</p>
        </div>
        <Button 
          onClick={() => navigate('/nfa/create')}
          className="bg-gradient-to-r from-indigo-600 to-blue-500 hover:from-indigo-700 hover:to-blue-600"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New NFA
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search by NFA number, subject..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="section1_pending">Section 1 Pending</SelectItem>
                <SelectItem value="section1_approved">Section 1 Approved</SelectItem>
                <SelectItem value="section2_pending">Section 2 Pending</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* NFAs List */}
      {filteredNFAs.length === 0 ? (
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {searchTerm || statusFilter !== 'all' ? 'No NFAs found' : 'No NFAs created yet'}
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Get started by creating your first NFA request'
                }
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => navigate('/nfa/create')}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create New NFA
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredNFAs.map((nfa) => (
            <Card 
              key={nfa.id}
              className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-indigo-500"
              onClick={() => navigate(`/nfa/${nfa.id}`)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* NFA Number & Status */}
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {nfa.nfa_number || `NFA-${nfa.id.substring(0, 8)}`}
                      </h3>
                      <StatusBadge status={nfa.status} />
                    </div>

                    {/* Subject */}
                    <p className="text-gray-700 mb-4 font-medium">
                      {nfa.section1_data?.subject_item || 'No subject'}
                    </p>

                    {/* Details Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Building className="w-4 h-4 text-gray-400" />
                        <span>{nfa.section1_data?.department || 'N/A'}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span>{new Date(nfa.created_at).toLocaleDateString()}</span>
                      </div>
                      {nfa.section1_data?.amount_of_approval && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <DollarSign className="w-4 h-4 text-gray-400" />
                          <span>
                            {nfa.section1_data?.currency || 'INR'} {nfa.section1_data.amount_of_approval.toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Arrow */}
                  <div className="ml-4">
                    <Button variant="ghost" size="sm">
                      View Details →
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Results Count */}
      {filteredNFAs.length > 0 && (
        <div className="mt-6 text-center text-sm text-gray-600">
          Showing {filteredNFAs.length} of {nfas.length} NFAs
        </div>
      )}
    </MainLayout>
  );
};

export default MyNFAs;
