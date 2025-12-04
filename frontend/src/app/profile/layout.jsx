// frontend/src/app/profile/layout.jsx
'use client';

import { useState } from 'react';
import Sidebar from '@/components/shell/Sidebar';
import RightSidebar from '@/components/shell/RightSidebar';
import BottomNav from '@/components/shell/BottomNav';
import Header from '@/components/shell/Header';
import UploadModal from '@/components/upload/UploadModal';
import UploadToast from '@/components/upload/UploadToast';

export default function ProfileLayout({ children }) {
  const [isUploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleUploadStart = (status) => {
    setUploadStatus(status);
    
    if (status === 'success' || status === 'error') {
      setTimeout(() => {
        setUploadStatus(null);
      }, 5000);
    }
  };

  const handleCloseToast = () => {
    setUploadStatus(null);
  };

  return (
    <div className="min-h-screen bg-background text-primary">
      {/* Fixed Sidebars */}
      <div className="fixed left-0 top-0 h-full z-30 hidden md:block">
        <Sidebar onUploadClick={() => setUploadModalOpen(true)} />
      </div>
      <div className="fixed right-0 top-0 h-full z-30 hidden lg:block">
        <RightSidebar />
      </div>

      {/* Main Content - CENTERED & RESPONSIVE */}
      <div className="md:ml-64 lg:mr-80">
        <Header />
        
        <main className="min-h-screen pt-20 pb-20">
          {children}
        </main>
      </div>
      
      <BottomNav />

      {/* Upload Modal */}
      {isUploadModalOpen && (
        <UploadModal 
          onClose={() => setUploadModalOpen(false)} 
          onUploadStart={handleUploadStart}
        />
      )}

      {/* Upload Toast Notification */}
      {uploadStatus && (
        <UploadToast 
          status={uploadStatus} 
          onClose={handleCloseToast}
        />
      )}
    </div>
  );
}