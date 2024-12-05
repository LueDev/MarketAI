// src/components/UserProfile.tsx
import React from 'react';

const UserProfile: React.FC = () => {
    return (
        <div>
            <h2>User Profile</h2>
            <p><strong>Name:</strong> John Doe</p>
            <p><strong>Email:</strong> johndoe@example.com</p>
            <h3>Preferences</h3>
            <p>Favorite Stock: AAPL</p>
            {/* Add other user settings here */}
        </div>
    );
};

export default UserProfile;
