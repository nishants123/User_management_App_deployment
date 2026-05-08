const API_URL = 'http://localhost:5000';

// Load users on page load
document.addEventListener('DOMContentLoaded', loadUsers);

async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/users`);
        const data = await response.json();
        
        const tbody = document.getElementById('usersBody');
        const noUsers = document.getElementById('noUsers');
        
        if (data.users && data.users.length > 0) {
            tbody.innerHTML = '';
            noUsers.style.display = 'none';
            
            data.users.forEach(user => {
                const row = document.createElement('tr');
                const createdAt = new Date(user.created_at).toLocaleDateString();
                
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.phone || '-'}</td>
                    <td>${createdAt}</td>
                    <td>
                        <div class="actions">
                            <button class="btn btn-edit" onclick="showEditForm(${user.id}, '${user.name}', '${user.email}', '${user.phone || ''}')">Edit</button>
                            <button class="btn btn-danger" onclick="deleteUser(${user.id})">Delete</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '';
            noUsers.style.display = 'block';
        }
    } catch (error) {
        showAlert('Error loading users: ' + error.message, 'error');
    }
}

function showAddForm() {
    document.getElementById('addUserForm').style.display = 'block';
    document.getElementById('name').focus();
}

function hideAddForm() {
    document.getElementById('addUserForm').style.display = 'none';
    document.getElementById('addUserForm').reset();
}

function showEditForm(id, name, email, phone) {
    document.getElementById('editId').value = id;
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPhone').value = phone;
    document.getElementById('editUserForm').style.display = 'block';
}

function hideEditForm() {
    document.getElementById('editUserForm').style.display = 'none';
    document.getElementById('editUserForm').reset();
}

async function addUser(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    
    try {
        const response = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, phone })
        });
        
        if (response.status === 201) {
            showAlert('User added successfully!', 'success');
            hideAddForm();
            loadUsers();
        } else {
            const error = await response.json();
            showAlert('Error: ' + error.error, 'error');
        }
    } catch (error) {
        showAlert('Error adding user: ' + error.message, 'error');
    }
}

async function updateUser(event) {
    event.preventDefault();
    
    const id = document.getElementById('editId').value;
    const name = document.getElementById('editName').value;
    const email = document.getElementById('editEmail').value;
    const phone = document.getElementById('editPhone').value;
    
    try {
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, phone })
        });
        
        if (response.status === 200) {
            showAlert('User updated successfully!', 'success');
            hideEditForm();
            loadUsers();
        } else {
            const error = await response.json();
            showAlert('Error: ' + error.error, 'error');
        }
    } catch (error) {
        showAlert('Error updating user: ' + error.message, 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users/${id}`, {
            method: 'DELETE'
        });
        
        if (response.status === 200) {
            showAlert('User deleted successfully!', 'success');
            loadUsers();
        } else {
            const error = await response.json();
            showAlert('Error: ' + error.error, 'error');
        }
    } catch (error) {
        showAlert('Error deleting user: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alert, container.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}
