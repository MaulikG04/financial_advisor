document.addEventListener('DOMContentLoaded', async function () {
    async function fetchUsers() {
        try {
            const response = await fetch('/admin/users');
            const users = await response.json();
            const usersList = document.getElementById('usersList');
            usersList.innerHTML = users.map(user => `
                <div class="user">
                    <p>ID: ${user[0]}</p>
                    <p>Name: ${user[1]}</p>
                    <p>Email: ${user[2]}</p>
                    <button onclick="deleteUser(${user[0]})">Delete User</button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error fetching users:', error);
            alert('An error occurred while fetching users.');
        }
    }

    fetchUsers();

    async function deleteUser(userId) {
        if (confirm('Are you sure you want to delete this user?')) {
            try {
                const response = await fetch(`/delete_user/${userId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const result = await response.json();
                alert(result.message);
                fetchUsers();  // Refresh the user list
            } catch (error) {
                console.error('Error deleting user:', error);
                alert('An error occurred while deleting the user.');
            }
        }
    }

    window.deleteUser = deleteUser;  // Expose deleteUser function to global scope
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('adminLoginForm').addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = {
            email: formData.get('adminEmail'),
            password: formData.get('adminPassword')
        };
        
        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                window.location.href = '/admin';
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});
