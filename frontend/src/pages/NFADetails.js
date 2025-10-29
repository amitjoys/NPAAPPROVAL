import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Separator } from '../components/ui/separator';
import { ArrowLeft, Download, CheckCircle, XCircle, Clock, FileText } from 'lucide-react';
import { toast } from 'sonner';

const NFADetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nfa, setNfa] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNFADetails();
  }, [id]);

  const fetchNFADetails = async () => {
    try {
      const [nfaRes, historyRes] = await Promise.all([
        api.get(`/nfa/${id}`),
        api.get(`/approvals/nfa/${id}/history`)
      ]);
      setNfa(nfaRes.data);
      setHistory(historyRes.data);
    } catch (error) {
      toast.error('Failed to load NFA details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'rejected': return <XCircle className="w-5 h-5 text-red-600" />;
      case 'pending': return <Clock className="w-5 h-5 text-orange-600" />;
      default: return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusBadge = (status) => {
    const config = {
      draft: { className: 'bg-gray-100 text-gray-800', label: 'Draft' },
      section1_pending: { className: 'bg-orange-100 text-orange-800', label: 'Section 1 Pending' },
      section1_approved: { className: 'bg-blue-100 text-blue-800', label: 'Section 1 Approved' },
      section2_pending: { className: 'bg-orange-100 text-orange-800', label: 'Section 2 Pending' },
      approved: { className: 'bg-green-100 text-green-800', label: 'Approved' },
      rejected: { className: 'bg-red-100 text-red-800', label: 'Rejected' },
    };
    const c = config[status] || config.draft;
    return <Badge className={c.className}>{c.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!nfa) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">NFA not found</p>
          <Button onClick={() => navigate('/')} className="mt-4">Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const s1 = nfa.section1_data || {};
  const s2 = nfa.section2_data || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
          {nfa.pdf_url && (
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" /> Download PDF
            </Button>
          )}
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8 max-w-5xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              NFA Request {nfa.nfa_number || `#${nfa.id.substring(0, 8)}`}
            </h1>
            <p className="text-gray-600">Created on {new Date(nfa.created_at).toLocaleDateString()}</p>
          </div>
          {getStatusBadge(nfa.status)}
        </div>

        <div className="space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Requestor</p>
                  <p className="font-medium">{nfa.requestor_name}</p>
                </div>
                <div>
                  <p className="text-gray-600">Department</p>
                  <p className="font-medium">{s1.department || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Location</p>
                  <p className="font-medium">{s1.location || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Cost Code</p>
                  <p className="font-medium">{s1.cost_code || 'N/A'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Subject & Purpose */}
          <Card>
            <CardHeader>
              <CardTitle>Subject & Purpose</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Subject</p>
                  <p className="font-medium">{s1.subject_item || 'N/A'}</p>
                </div>
                <Separator />
                <div>
                  <p className="text-sm text-gray-600 mb-1">Background & Purpose</p>
                  <p className="text-sm">{s1.background_purpose || 'N/A'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Financial Details */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Budget Status</p>
                  <p className="font-medium">{s1.budget_status || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Amount</p>
                  <p className="font-medium text-lg">
                    {s1.currency || 'INR'} {(s1.amount_of_approval || 0).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Tax Status</p>
                  <p className="font-medium">{s1.tax_status || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Advance Payment</p>
                  <p className="font-medium">{s1.advance_payment_required ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Approval History */}
          <Card>
            <CardHeader>
              <CardTitle>Approval History</CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-center text-gray-500 py-4">No approval actions yet</p>
              ) : (
                <div className="space-y-4">
                  {history.map((item, idx) => (
                    <div key={item.id} className="flex items-start space-x-4">
                      <div className="flex flex-col items-center">
                        {getStatusIcon(item.status)}
                        {idx < history.length - 1 && (
                          <div className="w-0.5 h-12 bg-gray-300 my-2"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="flex items-center justify-between mb-1">
                          <p className="font-medium">{item.approver_name}</p>
                          <Badge className={item.status === 'approved' ? 'bg-green-100 text-green-800' : item.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'}>
                            {item.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600">{item.approver_designation}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Section {item.section} - Sequence {item.sequence + 1}
                        </p>
                        {item.comments && (
                          <p className="text-sm mt-2 p-2 bg-gray-50 rounded">{item.comments}</p>
                        )}
                        {item.action_timestamp && (
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(item.action_timestamp).toLocaleString()}
                          </p>
                        )}
                      </div>
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

export default NFADetails;
