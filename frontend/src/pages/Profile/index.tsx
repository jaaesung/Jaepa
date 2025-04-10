import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../types';
import './Profile.css';

const Profile: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  const [isEditing, setIsEditing] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 프로필 업데이트 로직 구현 예정
    setIsEditing(false);
  };
  
  const toggleEdit = () => {
    setIsEditing(!isEditing);
  };
  
  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>내 프로필</h1>
        <p className="description">
          개인 정보를 관리하고 계정 설정을 변경할 수 있습니다.
        </p>
      </div>
      
      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <h2>{user?.name || '사용자'}</h2>
            <p className="user-email">{user?.email || 'email@example.com'}</p>
          </div>
          
          <div className="profile-details">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>이름</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                  />
                ) : (
                  <p className="detail-value">{user?.name || '이름 정보 없음'}</p>
                )}
              </div>
              
              <div className="form-group">
                <label>이메일</label>
                <p className="detail-value">{user?.email || 'email@example.com'}</p>
              </div>
              
              {isEditing && (
                <>
                  <div className="form-group">
                    <label>현재 비밀번호</label>
                    <input
                      type="password"
                      name="currentPassword"
                      value={formData.currentPassword}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>새 비밀번호</label>
                    <input
                      type="password"
                      name="newPassword"
                      value={formData.newPassword}
                      onChange={handleChange}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>비밀번호 확인</label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                    />
                  </div>
                </>
              )}
              
              <div className="profile-actions">
                {isEditing ? (
                  <>
                    <button type="submit" className="save-button">
                      저장
                    </button>
                    <button
                      type="button"
                      className="cancel-button"
                      onClick={toggleEdit}
                    >
                      취소
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    className="edit-button"
                    onClick={toggleEdit}
                  >
                    프로필 수정
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
        
        <div className="profile-sections">
          <div className="profile-section">
            <h3>계정 설정</h3>
            <div className="section-content">
              <div className="setting-item">
                <div className="setting-info">
                  <h4>알림 설정</h4>
                  <p>이메일 및 앱 내 알림 설정을 관리합니다.</p>
                </div>
                <button className="setting-button">관리</button>
              </div>
              
              <div className="setting-item">
                <div className="setting-info">
                  <h4>보안 설정</h4>
                  <p>계정 보안 및 로그인 설정을 관리합니다.</p>
                </div>
                <button className="setting-button">관리</button>
              </div>
              
              <div className="setting-item">
                <div className="setting-info">
                  <h4>데이터 및 개인정보</h4>
                  <p>개인 데이터 및 개인정보 설정을 관리합니다.</p>
                </div>
                <button className="setting-button">관리</button>
              </div>
            </div>
          </div>
          
          <div className="profile-section">
            <h3>워치리스트 관리</h3>
            <div className="section-content">
              <p>관심 있는 주식 및 뉴스 키워드를 관리합니다.</p>
              <button className="section-button">워치리스트 관리</button>
            </div>
          </div>
          
          <div className="profile-section danger-zone">
            <h3>계정 삭제</h3>
            <div className="section-content">
              <p>계정을 삭제하면 모든 데이터가 영구적으로 삭제됩니다. 이 작업은 되돌릴 수 없습니다.</p>
              <button className="danger-button">계정 삭제</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
