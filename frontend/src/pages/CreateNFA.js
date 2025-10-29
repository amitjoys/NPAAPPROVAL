import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { toast } from 'sonner';
import { ArrowLeft, Save, Send, Loader2, Plus, X } from 'lucide-react';

const CreateNFA = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [approvers, setApprovers] = useState([]);
  
  const [formData, setFormData] = useState({
    function_division: user?.function || '',
    department: user?.department || '',
    location: user?.location || '',
    requestor_name: user?.name || '',
    cost_code: '',
    subject_item: '',
    background_purpose: '',
    work_approval_required: true,
    proposal_description: '',
    activity_approved: false,
    proposed_work_schedule: '',
    vendor_selection_required: false,
    num_vendors_evaluated: 0,
    vendor_name_proposed: '',
    budget_status: 'Budgeted',
    budget_available_with_user: true,
    department_with_budget: '',
    currency: 'INR',
    amount_of_approval: 0,
    tax_status: 'excluded',
    more_than_budget_amount: 0,
    advance_payment_required: false,
    advance_amount: 0,
    security_for_advance: '',
    route_to: 'Finance',
    ibm_coordinator: '',
    comments: ''
  });

  useEffect(() => {
    fetchUsers();
    fetchVendors();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const fetchVendors = async () => {
    try {
      const response = await api.get('/vendors');
      setVendors(response.data);
    } catch (error) {
      console.error('Failed to fetch vendors:', error);
    }
  };

  const addApprover = (userId) => {
    const user = users.find(u => u.id === userId);
    if (user && !approvers.find(a => a.user_id === userId)) {
      setApprovers([...approvers, {
        user_id: user.id,
        name: user.name,
        designation: user.designation,
        sequence: approvers.length
      }]);
    }
  };

  const removeApprover = (userId) => {
    setApprovers(approvers.filter(a => a.user_id !== userId).map((a, idx) => ({...a, sequence: idx})));
  };

  const handleSubmit = async (submitForApproval = false) => {
    setLoading(true);
    try {
      // Create NFA
      const response = await api.post('/nfa/', {
        section1_data: {
          ...formData,
          approver_list: approvers
        }
      });

      toast.success('NFA created successfully!');
      
      if (submitForApproval && approvers.length > 0) {
        // Submit for approval
        await api.post(`/nfa/${response.data.id}/submit-section1`);
        toast.success('NFA submitted for approval!');
      }
      
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create NFA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-8 max-w-5xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Create NFA Request</h1>
          <p className="text-gray-600">Note for Approval - Work/Expense/Vendor Selection</p>
        </div>

        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <div>
                <Label>Function/Division</Label>
                <Input value={formData.function_division} onChange={(e) => setFormData({...formData, function_division: e.target.value})} />
              </div>
              <div>
                <Label>Location</Label>
                <Input value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})} />
              </div>
              <div>
                <Label>Requestor Name</Label>
                <Input value={formData.requestor_name} readOnly className="bg-gray-50" />
              </div>
              <div>
                <Label>Cost Code</Label>
                <Input value={formData.cost_code} onChange={(e) => setFormData({...formData, cost_code: e.target.value})} />
              </div>
              <div>
                <Label>Department</Label>
                <Input value={formData.department} onChange={(e) => setFormData({...formData, department: e.target.value})} />
              </div>
            </CardContent>
          </Card>

          {/* Subject & Background */}
          <Card>
            <CardHeader>
              <CardTitle>Subject & Purpose</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Subject/Item</Label>
                <Input 
                  value={formData.subject_item} 
                  onChange={(e) => setFormData({...formData, subject_item: e.target.value})}
                  placeholder="Brief description of the request"
                />
              </div>
              <div>
                <Label>Background & Purpose</Label>
                <Textarea 
                  value={formData.background_purpose}
                  onChange={(e) => setFormData({...formData, background_purpose: e.target.value})}
                  rows={4}
                  placeholder="Detailed explanation of the purpose and background"
                />
              </div>
            </CardContent>
          </Card>

          {/* Proposal Details */}
          <Card>
            <CardHeader>
              <CardTitle>Proposal Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Proposal Description</Label>
                <Textarea 
                  value={formData.proposal_description}
                  onChange={(e) => setFormData({...formData, proposal_description: e.target.value})}
                  rows={3}
                  placeholder="Work description, vendor selection process approval, etc."
                />
              </div>
              <div>
                <Label>Proposed Work Schedule</Label>
                <Input 
                  value={formData.proposed_work_schedule}
                  onChange={(e) => setFormData({...formData, proposed_work_schedule: e.target.value})}
                  placeholder="Timeline or schedule"
                />
              </div>
              <div className="flex items-center space-x-4">
                <Label>Vendor Selection Required?</Label>
                <RadioGroup 
                  value={formData.vendor_selection_required.toString()}
                  onValueChange={(val) => setFormData({...formData, vendor_selection_required: val === 'true'})}
                  className="flex space-x-4"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="true" id="vendor-yes" />
                    <Label htmlFor="vendor-yes">Yes</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="false" id="vendor-no" />
                    <Label htmlFor="vendor-no">No</Label>
                  </div>
                </RadioGroup>
              </div>
            </CardContent>
          </Card>

          {/* Financial Details */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Budget Status</Label>
                  <Select value={formData.budget_status} onValueChange={(val) => setFormData({...formData, budget_status: val})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Budgeted">Budgeted</SelectItem>
                      <SelectItem value="Unbudgeted">Unbudgeted</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Budget Available with User?</Label>
                  <RadioGroup 
                    value={formData.budget_available_with_user.toString()}
                    onValueChange={(val) => setFormData({...formData, budget_available_with_user: val === 'true'})}
                    className="flex space-x-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="true" id="budget-yes" />
                      <Label htmlFor="budget-yes">Yes</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="false" id="budget-no" />
                      <Label htmlFor="budget-no">No</Label>
                    </div>
                  </RadioGroup>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>Currency</Label>
                  <Select value={formData.currency} onValueChange={(val) => setFormData({...formData, currency: val})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR (₹)</SelectItem>
                      <SelectItem value="USD">USD ($)</SelectItem>
                      <SelectItem value="YEN">YEN (¥)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Amount of Approval</Label>
                  <Input 
                    type="number"
                    value={formData.amount_of_approval}
                    onChange={(e) => setFormData({...formData, amount_of_approval: parseFloat(e.target.value) || 0})}
                  />
                </div>
                <div>
                  <Label>Tax Status</Label>
                  <Select value={formData.tax_status} onValueChange={(val) => setFormData({...formData, tax_status: val})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="included">Tax Included</SelectItem>
                      <SelectItem value="excluded">Tax Excluded</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Label>Advance Payment Required?</Label>
                <RadioGroup 
                  value={formData.advance_payment_required.toString()}
                  onValueChange={(val) => setFormData({...formData, advance_payment_required: val === 'true'})}
                  className="flex space-x-4"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="true" id="advance-yes" />
                    <Label htmlFor="advance-yes">Yes</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="false" id="advance-no" />
                    <Label htmlFor="advance-no">No</Label>
                  </div>
                </RadioGroup>
              </div>

              {formData.advance_payment_required && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Advance Amount</Label>
                    <Input 
                      type="number"
                      value={formData.advance_amount}
                      onChange={(e) => setFormData({...formData, advance_amount: parseFloat(e.target.value) || 0})}
                    />
                  </div>
                  <div>
                    <Label>Security for Advance</Label>
                    <Input 
                      value={formData.security_for_advance}
                      onChange={(e) => setFormData({...formData, security_for_advance: e.target.value})}
                      placeholder="Bank guarantee, insurance, etc."
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Approvers */}
          <Card>
            <CardHeader>
              <CardTitle>Approval Routing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Add Approvers (Sequential Order)</Label>
                <Select onValueChange={addApprover}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select approver" />
                  </SelectTrigger>
                  <SelectContent>
                    {users.filter(u => u.roles.includes('approver') && u.id !== user.id).map(u => (
                      <SelectItem key={u.id} value={u.id}>
                        {u.name} - {u.designation}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {approvers.length > 0 && (
                <div className="space-y-2">
                  <Label className="text-sm text-gray-600">Approval Sequence:</Label>
                  {approvers.map((approver, idx) => (
                    <div key={approver.user_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center justify-center w-8 h-8 bg-indigo-600 text-white rounded-full text-sm font-bold">
                          {idx + 1}
                        </span>
                        <div>
                          <p className="font-medium">{approver.name}</p>
                          <p className="text-sm text-gray-600">{approver.designation}</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => removeApprover(approver.user_id)}>
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4">
            <Button variant="outline" onClick={() => navigate('/')}>
              Cancel
            </Button>
            <Button 
              onClick={() => handleSubmit(false)} 
              disabled={loading}
              variant="outline"
            >
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Save as Draft
            </Button>
            <Button 
              onClick={() => handleSubmit(true)} 
              disabled={loading || approvers.length === 0}
              className="bg-gradient-to-r from-indigo-600 to-blue-500"
            >
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
              Submit for Approval
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateNFA;
