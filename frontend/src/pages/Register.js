import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    designation: '',
    department: '',
    location: '',
    function: ''
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await register({ ...formData, roles: ['requestor'] });
    setLoading(false);
    
    if (result.success) {
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } else {
      toast.error(result.error || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8">
        <h1 className="text-3xl font-bold gradient-text mb-6">Create Account</h1>
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div>
            <Label>Username</Label>
            <Input value={formData.username} onChange={(e) => setFormData({...formData, username: e.target.value})} required />
          </div>
          <div>
            <Label>Email</Label>
            <Input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} required />
          </div>
          <div>
            <Label>Name</Label>
            <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
          </div>
          <div>
            <Label>Password</Label>
            <Input type="password" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} required />
          </div>
          <div>
            <Label>Designation</Label>
            <Input value={formData.designation} onChange={(e) => setFormData({...formData, designation: e.target.value})} />
          </div>
          <div>
            <Label>Department</Label>
            <Input value={formData.department} onChange={(e) => setFormData({...formData, department: e.target.value})} />
          </div>
          <div>
            <Label>Location</Label>
            <Input value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})} />
          </div>
          <div>
            <Label>Function/Division</Label>
            <Input value={formData.function} onChange={(e) => setFormData({...formData, function: e.target.value})} />
          </div>
          <div className="col-span-2">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Registering...</> : 'Register'}
            </Button>
          </div>
        </form>
        <p className="text-center mt-4 text-sm">
          Already have an account? <Link to="/login" className="text-indigo-600 font-medium">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
