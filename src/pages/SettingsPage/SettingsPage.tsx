/**
 * 설정 페이지 컴포넌트
 * 
 * 사용자 설정 및 프로필 관리를 위한 페이지를 제공합니다.
 */

import React, { useState } from 'react';
import { MainLayout } from '../../components/layout';
import { Card, Button, Input } from '../../components/ui';
import { useAuth } from '../../features/auth';
import { useTheme } from '../../core/contexts';
import './SettingsPage.css';

/**
 * 설정 페이지 컴포넌트
 */
const SettingsPage: React.FC = () => {
  const { user, updateProfile, changePassword } = useAuth();
  const { theme, setTheme } = useTheme();
  
  // 프로필 상태
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [profileError, setProfileError] = useState('');
  
  // 비밀번호 상태
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  // 프로필 수정 핸들러
  const handleEditProfile = () => {
    setIsEditingProfile(true);
    setProfileSuccess(false);
    setProfileError('');
  };

  // 프로필 저장 핸들러
  const handleSaveProfile = async () => {
    try {
      setProfileError('');
      const success = await updateProfile({ name, email });
      
      if (success) {
        setProfileSuccess(true);
        setIsEditingProfile(false);
      } else {
        setProfileError('프로필 업데이트에 실패했습니다.');
      }
    } catch (error) {
      setProfileError('프로필 업데이트 중 오류가 발생했습니다.');
    }
  };

  // 프로필 취소 핸들러
  const handleCancelProfile = () => {
    setName(user?.name || '');
    setEmail(user?.email || '');
    setIsEditingProfile(false);
    setProfileError('');
  };

  // 비밀번호 변경 핸들러
  const handleChangePassword = async () => {
    // 유효성 검사
    if (newPassword !== confirmPassword) {
      setPasswordError('새 비밀번호와 확인 비밀번호가 일치하지 않습니다.');
      return;
    }
    
    if (newPassword.length < 8) {
      setPasswordError('비밀번호는 최소 8자 이상이어야 합니다.');
      return;
    }
    
    try {
      setPasswordError('');
      setIsChangingPassword(true);
      
      const success = await changePassword(currentPassword, newPassword);
      
      if (success) {
        setPasswordSuccess(true);
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        setPasswordError('비밀번호 변경에 실패했습니다.');
      }
    } catch (error) {
      setPasswordError('비밀번호 변경 중 오류가 발생했습니다.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  // 테마 변경 핸들러
  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
  };

  return (
    <MainLayout>
      <div className="settings-page">
        <div className="settings-header">
          <h1 className="settings-title">설정</h1>
          <p className="settings-description">
            계정 설정 및 애플리케이션 환경을 관리하세요.
          </p>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h2 className="settings-section-title">프로필 설정</h2>
            
            <Card className="settings-card">
              <div className="settings-card-header">
                <h3 className="settings-card-title">사용자 정보</h3>
                {!isEditingProfile && (
                  <Button variant="text" onClick={handleEditProfile}>
                    수정
                  </Button>
                )}
              </div>
              
              {profileSuccess && (
                <div className="settings-success">
                  프로필이 성공적으로 업데이트되었습니다.
                </div>
              )}
              
              {profileError && (
                <div className="settings-error">{profileError}</div>
              )}
              
              <div className="settings-form">
                <div className="settings-form-group">
                  <Input
                    label="이름"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={!isEditingProfile}
                    fullWidth
                  />
                </div>
                
                <div className="settings-form-group">
                  <Input
                    label="이메일"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={!isEditingProfile}
                    fullWidth
                  />
                </div>
                
                {isEditingProfile && (
                  <div className="settings-form-actions">
                    <Button variant="outline" onClick={handleCancelProfile}>
                      취소
                    </Button>
                    <Button onClick={handleSaveProfile}>저장</Button>
                  </div>
                )}
              </div>
            </Card>
            
            <Card className="settings-card">
              <div className="settings-card-header">
                <h3 className="settings-card-title">비밀번호 변경</h3>
              </div>
              
              {passwordSuccess && (
                <div className="settings-success">
                  비밀번호가 성공적으로 변경되었습니다.
                </div>
              )}
              
              {passwordError && (
                <div className="settings-error">{passwordError}</div>
              )}
              
              <div className="settings-form">
                <div className="settings-form-group">
                  <Input
                    label="현재 비밀번호"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    fullWidth
                  />
                </div>
                
                <div className="settings-form-group">
                  <Input
                    label="새 비밀번호"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    fullWidth
                  />
                </div>
                
                <div className="settings-form-group">
                  <Input
                    label="새 비밀번호 확인"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    fullWidth
                  />
                </div>
                
                <div className="settings-form-actions">
                  <Button
                    onClick={handleChangePassword}
                    disabled={
                      !currentPassword ||
                      !newPassword ||
                      !confirmPassword ||
                      isChangingPassword
                    }
                    isLoading={isChangingPassword}
                  >
                    비밀번호 변경
                  </Button>
                </div>
              </div>
            </Card>
          </div>
          
          <div className="settings-section">
            <h2 className="settings-section-title">애플리케이션 설정</h2>
            
            <Card className="settings-card">
              <div className="settings-card-header">
                <h3 className="settings-card-title">테마 설정</h3>
              </div>
              
              <div className="settings-theme">
                <div
                  className={`theme-option ${theme === 'light' ? 'active' : ''}`}
                  onClick={() => handleThemeChange('light')}
                >
                  <div className="theme-preview light-theme">
                    <div className="theme-preview-header"></div>
                    <div className="theme-preview-content"></div>
                  </div>
                  <div className="theme-option-label">라이트 모드</div>
                </div>
                
                <div
                  className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
                  onClick={() => handleThemeChange('dark')}
                >
                  <div className="theme-preview dark-theme">
                    <div className="theme-preview-header"></div>
                    <div className="theme-preview-content"></div>
                  </div>
                  <div className="theme-option-label">다크 모드</div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default SettingsPage;
