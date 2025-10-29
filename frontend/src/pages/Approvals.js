import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { ArrowLeft, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const Approvals = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    try {
      const response = await api.get('/approvals/pending');
      setApprovals(response.data);
    } catch (error) {
      toast.error('Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (approval, action) => {
    setSelectedApproval(approval);
    setActionType(action);
    setComments('');
    setActionDialog(true);
  };

  const submitAction = async () => {
    if (!selectedApproval) return;

    if (actionType === 'reject' && !comments.trim()) {
      toast.error('Comments are required for rejection');
      return;
    }

    setSubmitting(true);
    try {
      await api.post(`/approvals/${selectedApproval.id}/action`, {
        action: actionType,
        comments: comments.trim() || null
      });

      toast.success(`NFA ${actionType}d successfully!`);
      setActionDialog(false);
      fetchPendingApprovals();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${actionType}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div data-testid="approvals-page" className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Pending Approvals</h1>
          <p className="text-gray-600">
            You have <strong>{approvals.length}</strong> pending approval{approvals.length !== 1 ? 's' : ''}
          </p>
        </div>

        {approvals.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <p className="text-xl font-medium text-gray-700 mb-2">All caught up!</p>
              <p className="text-gray-500">You have no pending approvals at the moment.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {approvals.map((approval) => {
              const nfa = approval.nfa || {};
              const s1 = nfa.section1_data || {};
              
              return (
                <Card key={approval.id} className="card-hover">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <AlertCircle className="w-5 h-5 text-orange-600" />
                        <div>
                          <CardTitle className="text-lg">
                            NFA {nfa.nfa_number || `#${nfa.id?.substring(0, 8)}`}
                          </CardTitle>
                          <p className="text-sm text-gray-600 mt-1">
                            Section {approval.section} - Position {approval.sequence + 1}
                          </p>
                        </div>
                      </div>
                      <Badge className="bg-orange-100 text-orange-800">Pending</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Requestor</p>
                        <p className="font-medium">{nfa.requestor_name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Department</p>
                        <p className="font-medium">{s1.department || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Subject</p>
                        <p className="font-medium">{s1.subject_item || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Amount</p>
                        <p className="font-medium text-lg">
                          {s1.currency || 'INR'} {(s1.amount_of_approval || 0).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    {s1.background_purpose && (
                      <div className="mb-4">
                        <p className="text-sm text-gray-600 mb-1">Background & Purpose</p>
                        <p className="text-sm p-3 bg-gray-50 rounded">{s1.background_purpose}</p>
                      </div>
                    )}

                    <div className="flex space-x-3">
                      <Button
                        onClick={() => navigate(`/nfa/${nfa.id}`)}
                        variant="outline"
                        className="flex-1"
                      >
                        View Details
                      </Button>
                      <Button
                        onClick={() => handleAction(approval, 'approve')}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                        data-testid="approve-button"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Approve
                      </Button>
                      <Button
                        onClick={() => handleAction(approval, 'send_back')}
                        variant="outline"
                        className="flex-1"
                      >
                        <AlertCircle className="w-4 h-4 mr-2" />
                        Send Back
                      </Button>
                      <Button
                        onClick={() => handleAction(approval, 'reject')}
                        variant="destructive"
                        className="flex-1"
                        data-testid="reject-button"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Reject
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Action Dialog */}
      <Dialog open={actionDialog} onOpenChange={setActionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' && 'Approve NFA'}
              {actionType === 'reject' && 'Reject NFA'}
              {actionType === 'send_back' && 'Send Back NFA'}
            </DialogTitle>
            <DialogDescription>
              {actionType === 'approve' && 'Are you sure you want to approve this NFA request?'}
              {actionType === 'reject' && 'Please provide a reason for rejection.'}
              {actionType === 'send_back' && 'Please provide clarification needed.'}
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Label htmlFor="comments">Comments {actionType === 'reject' && <span className="text-red-600">*</span>}</Label>
            <Textarea
              id="comments"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder={actionType === 'approve' ? 'Optional comments' : 'Required comments'}
              rows={4}
              className="mt-2"
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setActionDialog(false)} disabled={submitting}>
              Cancel
            </Button>
            <Button 
              onClick={submitAction} 
              disabled={submitting || (actionType === 'reject' && !comments.trim())}
              className={actionType === 'approve' ? 'bg-green-600 hover:bg-green-700' : actionType === 'reject' ? 'bg-red-600 hover:bg-red-700' : ''}
            >
              {submitting ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</>
              ) : (
                <>{actionType === 'approve' && 'Approve'}{actionType === 'reject' && 'Reject'}{actionType === 'send_back' && 'Send Back'}</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Approvals;
