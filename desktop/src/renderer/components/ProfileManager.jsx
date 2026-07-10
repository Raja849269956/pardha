import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProfiles, createProfile, updateProfile, deleteProfile, extractResume } from '../api';

const EMPTY_PROFILE = {
  name: '',
  role_title: '',
  target_company: '',
  resume_text: '',
  job_description: '',
  about_me: '',
  key_strengths: '',
  sample_answers: '',
  tone: 'professional',
  answer_length: 'medium',
};

function ProfileManager({ user }) {
  const [profiles, setProfiles] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(EMPTY_PROFILE);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  const loadProfiles = () => {
    getProfiles().then(setProfiles).catch(console.error);
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    if (isEditing && selected) {
      await updateProfile(selected.id, form);
    } else {
      await createProfile(form);
    }
    setForm(EMPTY_PROFILE);
    setSelected(null);
    setIsEditing(false);
    loadProfiles();
  };

  const handleEdit = (profile) => {
    setSelected(profile);
    setForm({ ...profile });
    setIsEditing(true);
  };

  const handleDelete = async (id) => {
    await deleteProfile(id);
    loadProfiles();
  };

  const handleExtractResume = async () => {
    if (!selected) return;
    try {
      const updated = await extractResume(selected.id);
      setForm({ ...updated });
      loadProfiles();
    } catch (err) {
      alert(err.message || 'Failed to extract resume facts');
    }
  };

  const handleStart = (profile) => {
    navigate('/session', { state: { profile } });
  };

  return (
    <div className="profile-manager">
      <h2>Interview Profiles</h2>
      <p>Logged in as {user?.email}</p>
      <div className="profile-list">
        {profiles.map((p) => (
          <div key={p.id} className="profile-card">
            <div className="profile-title">
              {p.name} — {p.role_title} @ {p.target_company || 'Unknown'}
            </div>
            <div className="profile-meta">
              {p.tone} · {p.answer_length}
            </div>
            <div className="profile-actions">
              <button onClick={() => handleStart(p)}>Start Session</button>
              <button onClick={() => handleEdit(p)}>Edit</button>
              <button onClick={() => handleDelete(p.id)}>Delete</button>
            </div>
          </div>
        ))}
        {profiles.length === 0 && <p>No profiles yet. Create one below.</p>}
      </div>

      <h3>{isEditing ? 'Edit Profile' : 'Create Profile'}</h3>
      <div className="profile-form">
        <input name="name" placeholder="Profile name" value={form.name} onChange={handleChange} />
        <input name="role_title" placeholder="Role title" value={form.role_title} onChange={handleChange} />
        <input name="target_company" placeholder="Target company" value={form.target_company} onChange={handleChange} />
        <select name="tone" value={form.tone} onChange={handleChange}>
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="technical">Technical</option>
          <option value="confident">Confident</option>
        </select>
        <select name="answer_length" value={form.answer_length} onChange={handleChange}>
          <option value="short">Short</option>
          <option value="medium">Medium</option>
          <option value="long">Long</option>
        </select>
        <textarea name="resume_text" placeholder="Paste your resume text here" value={form.resume_text} onChange={handleChange} />
        {isEditing && form.resume_text && (
          <button type="button" onClick={handleExtractResume}>
            Extract Resume Facts
          </button>
        )}
        {form.resume_summary && (
          <textarea
            name="resume_summary"
            placeholder="Extracted resume summary (auto-generated)"
            value={form.resume_summary}
            readOnly
          />
        )}
        <textarea name="about_me" placeholder="About me: a short bio or background" value={form.about_me} onChange={handleChange} />
        <textarea name="key_strengths" placeholder="Key strengths: e.g. Python, React, system design, team leadership" value={form.key_strengths} onChange={handleChange} />
        <textarea name="sample_answers" placeholder="Paste 1-2 example answers in your own voice so the AI matches your style" value={form.sample_answers} onChange={handleChange} />
        <textarea name="job_description" placeholder="Paste the job description here" value={form.job_description} onChange={handleChange} />
        <div className="form-actions">
          <button onClick={handleSave}>{isEditing ? 'Update' : 'Create'}</button>
          {isEditing && (
            <button onClick={() => { setForm(EMPTY_PROFILE); setSelected(null); setIsEditing(false); }}>
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfileManager;
