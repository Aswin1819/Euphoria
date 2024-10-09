document.querySelector('form').addEventListener('submit', function(event) {
    let isValid = true; // To check if the form is valid or not

    // Fetching all fields
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirm_password').value.trim();

    // Regular expressions for validation
    const usernamePattern = /^[a-zA-Z]+$/; 
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const phonePattern = /^[0-9]{10}$/;

    // Clearing previous error messages
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    console.log("hai hello how are you");
    if (username === "") {
        console.log("inside first conditon");
        showError('username', 'User name is required');
        isValid = false;
    } 
    if (!usernamePattern.test(username)) {
        console.log("inside second conditon");
        showError('username', 'User name can only contain letters');
        isValid = false;
    }

    if (!emailPattern.test(email)) {
        showError('email', 'Please enter a valid email');
        isValid = false;
    }

    if (!phonePattern.test(phone)) {
        showError('phone', 'Please enter a valid phone number');
        isValid = false;
    }

    if (password.length < 8) {
        showError('password', 'Password must be at least 8 characters');
        isValid = false;
    }

    if (password !== confirmPassword) {
        showError('confirm_password', 'Passwords do not match');
        isValid = false;
    }

    if (!isValid) {
        event.preventDefault(); // If the form is not valid, prevent submission.
    }
});

function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

