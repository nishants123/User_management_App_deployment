const API_URL = 'http://127.0.0.1:55806';

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    hideLoadingScreen();
});

// Hide loading screen
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
        }, 500);
    }
}

// Load and display users
async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/users`);
        const data = await response.json();
        
        const tbody = document.getElementById('usersBody');
        const noUsers = document.getElementById('noUsers');
        const userCount = document.getElementById('userCount');
        const totalUsersEl = document.getElementById('totalUsers');
        
        if (data.users && data.users.length > 0) {
            tbody.innerHTML = '';
            noUsers.style.display = 'none';
            
            // Update statistics
            totalUsersEl.textContent = data.users.length;
            userCount.textContent = `${data.users.length} user${data.users.length !== 1 ? 's' : ''}`;
            
            data.users.forEach(user => {
                const row = document.createElement('tr');
                const createdAt = new Date(user.created_at).toLocaleDateString();
                const phoneDisplay = user.phone ? user.phone : '-';
                
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${escapeHtml(user.name)}</td>
                    <td>${escapeHtml(user.email)}</td>
                    <td>${phoneDisplay}</td>
                    <td>${createdAt}</td>
                    <td>
                        <div class="actions">
                            <button class="btn btn-edit" onclick="showEditForm(${user.id}, '${escapeHtml(user.name).replace(/'/g, "\\'")}', '${user.email}', '${phoneDisplay === '-' ? '' : phoneDisplay.replace(/'/g, "\\'")}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-danger" onclick="deleteUser(${user.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '';
            noUsers.style.display = 'block';
            totalUsersEl.textContent = '0';
            userCount.textContent = '0 users';
        }
        
        // Update other stats
        updateStats(data.users || []);
    } catch (error) {
        showAlert('Error loading users: ' + error.message, 'error');
        console.error('Load users error:', error);
    }
}

// Update statistics
function updateStats(users) {
    const activeUsers = document.getElementById('activeUsers');
    const newUsers = document.getElementById('newUsers');
    
    if (activeUsers) {
        activeUsers.textContent = users.length;
    }
    
    if (newUsers) {
        const currentMonth = new Date();
        const newThisMonth = users.filter(u => {
            const userDate = new Date(u.created_at);
            return userDate.getMonth() === currentMonth.getMonth() && 
                   userDate.getFullYear() === currentMonth.getFullYear();
        }).length;
        
        if (newUsers) {
            newUsers.textContent = newThisMonth;
        }
    }
}

// Show add form
function showAddForm() {
    document.getElementById('addUserForm').style.display = 'block';
    document.getElementById('name').focus();
}

// Hide add form
function hideAddForm() {
    document.getElementById('addUserForm').style.display = 'none';
    const addForm = document.getElementById('addForm');
    if (addForm) addForm.reset();
}

// Show edit form
function showEditForm(id, name, email, phone) {
    document.getElementById('editId').value = id;
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPhone').value = phone;
    document.getElementById('editUserForm').style.display = 'block';
}

// Hide edit form
function hideEditForm() {
    document.getElementById('editUserForm').style.display = 'none';
    const editForm = document.getElementById('editForm');
    if (editForm) editForm.reset();
}

// Add new user
async function addUser(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    
    if (!name || !email) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, phone })
        });
        
        const data = await response.json();
        
        if (response.status === 201) {
            showAlert('✓ User added successfully!', 'success');
            hideAddForm();
            loadUsers();
        } else if (response.status === 409) {
            showAlert('⚠ Email already exists', 'error');
        } else {
            showAlert('✗ Error: ' + (data.error || 'Failed to add user'), 'error');
        }
    } catch (error) {
        showAlert('✗ Error adding user: ' + error.message, 'error');
        console.error('Add user error:', error);
    }
}

// Update user
async function updateUser(event) {
    event.preventDefault();
    
    const id = document.getElementById('editId').value;
    const name = document.getElementById('editName').value.trim();
    const email = document.getElementById('editEmail').value.trim();
    const phone = document.getElementById('editPhone').value.trim();
    
    if (!name || !email) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, phone })
        });
        
        const data = await response.json();
        
        if (response.status === 200) {
            showAlert('✓ User updated successfully!', 'success');
            hideEditForm();
            loadUsers();
        } else if (response.status === 409) {
            showAlert('⚠ Email already exists', 'error');
        } else {
            showAlert('✗ Error: ' + (data.error || 'Failed to update user'), 'error');
        }
    } catch (error) {
        showAlert('✗ Error updating user: ' + error.message, 'error');
        console.error('Update user error:', error);
    }
}

// Delete user
async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.status === 200) {
            showAlert('✓ User deleted successfully!', 'success');
            loadUsers();
        } else {
            showAlert('✗ Error: ' + (data.error || 'Failed to delete user'), 'error');
        }
    } catch (error) {
        showAlert('✗ Error deleting user: ' + error.message, 'error');
        console.error('Delete user error:', error);
    }
}

// Refresh users
function refreshUsers() {
    showAlert('⟳ Refreshing data...', 'info');
    loadUsers();
}

// Show alert notification
function showAlert(message, type) {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = message;
    
    container.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Add animation for slide out
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);
