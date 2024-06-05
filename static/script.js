document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const submitButton = document.querySelector('form input[type="submit"]');
    const feedbackContainer = document.createElement('div');
    feedbackContainer.id = 'feedback';
    passwordInput.insertAdjacentElement('afterend', feedbackContainer);

    const criteria = {
        length: {
            test: password => password.length >= 14,
            message: 'At least 14 characters'
        },
        specialChar: {
            test: password => /[!@#$%^&*(),.?":{}|<>]/.test(password),
            message: 'At least one special character'
        },
        number: {
            test: password => /\d/.test(password),
            message: 'At least one number'
        },
        uppercase: {
            test: password => /[A-Z]/.test(password),
            message: 'At least one uppercase letter'
        }
    };

    function validatePassword() {
        const password = passwordInput.value;
        feedbackContainer.innerHTML = '';
        let allValid = true;

        for (const key in criteria) {
            const criterion = criteria[key];
            const isValid = criterion.test(password);
            const feedback = document.createElement('div');
            feedback.textContent = criterion.message;
            feedback.className = isValid ? 'valid' : 'invalid';
            feedbackContainer.appendChild(feedback);
            if (!isValid) {
                allValid = false;
            }
        }

        submitButton.disabled = !allValid;
    }

    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', () => {
        if (confirmPasswordInput.value !== passwordInput.value) {
            confirmPasswordInput.setCustomValidity("Passwords don't match");
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    });

    validatePassword();
});