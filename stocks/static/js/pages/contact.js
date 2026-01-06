/* ========================================
   CONTACT FORM - AJAX Submission with jQuery
   ======================================== */

$(document).ready(function () {
    const contactForm = $('#contactForm');
    const submitBtn = $('#submitBtn');
    const formAlert = $('#formAlert');

    // Form submission handler
    contactForm.on('submit', function (e) {
        e.preventDefault();

        // Clear previous errors
        clearErrors();

        // Get CSRF token from hidden input
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        // Show loading state
        setLoadingState(true);

        // Send AJAX request
        $.ajax({
            type: 'POST',
            url: contactForm.data('submit-url'),
            data: contactForm.serialize(),
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },

            success: function (response) {
                // Hide loading state
                setLoadingState(false);

                // Show success message
                showAlert('success', response.message || 'Thank you for your message!');

                // Mark all fields as success
                markFieldsAsSuccess();

                // Reset form after 2 seconds
                setTimeout(function () {
                    contactForm[0].reset();
                    $('.form-group input, .form-group textarea').removeClass('success error');
                    hideAlert();
                }, 3000);
            },
            error: function (xhr) {
                // Hide loading state
                setLoadingState(false);

                if (xhr.status === 400 && xhr.responseJSON && xhr.responseJSON.errors) {
                    // Display field-specific errors
                    const errors = xhr.responseJSON.errors;
                    displayErrors(errors);

                    // Show error alert
                    showAlert('error', xhr.responseJSON.message || 'Please correct the errors below');
                } else {
                    // Generic error message
                    showAlert('error', 'An error occurred. Please try again later.');
                }
            }
        });
    });

    // Real-time validation on blur
    $('#name, #email, #subject, #message').on('blur', function () {
        const field = $(this);
        const fieldId = field.attr('id');
        const value = field.val().trim();

        // Clear error for this field
        clearFieldError(fieldId);

        // Basic validation
        if (value === '') {
            showFieldError(fieldId, 'This field is required');
            field.addClass('error').removeClass('success');
        } else {
            // Field-specific validation
            validateField(fieldId, value);
        }
    });

    // Clear error on focus
    $('#name, #email, #subject, #message').on('focus', function () {
        const field = $(this);
        const fieldId = field.attr('id');
        clearFieldError(fieldId);
        field.removeClass('error');
    });

    /**
     * Display errors for multiple fields
     */
    function displayErrors(errors) {
        $.each(errors, function (field, messages) {
            if (field !== '__all__') {
                const errorMessage = Array.isArray(messages) ? messages[0] : messages;
                showFieldError(field, errorMessage);
                $('#' + field).addClass('error').removeClass('success');
            }
        });

        // Scroll to first error
        const firstError = $('.error-message:not(:empty)').first();
        if (firstError.length) {
            $('html, body').animate({
                scrollTop: firstError.offset().top - 100
            }, 300);
        }
    }

    /**
     * Show error message for a specific field
     */
    function showFieldError(fieldId, message) {
        $('#' + fieldId + '-error').text(message).show();
    }

    /**
     * Clear error for a specific field
     */
    function clearFieldError(fieldId) {
        $('#' + fieldId + '-error').text('').hide();
    }

    /**
     * Clear all errors
     */
    function clearErrors() {
        $('.error-message').text('').hide();
        $('.form-group input, .form-group textarea').removeClass('error success');
        hideAlert();
    }

    /**
     * Mark all fields as successful
     */
    function markFieldsAsSuccess() {
        $('.form-group input, .form-group textarea').addClass('success').removeClass('error');
    }

    /**
     * Validate individual field
     */
    function validateField(fieldId, value) {
        const field = $('#' + fieldId);

        switch (fieldId) {
            case 'name':
                if (value.length < 2) {
                    showFieldError(fieldId, 'Name must be at least 2 characters long');
                    field.addClass('error').removeClass('success');
                } else if (!/^[a-zA-Z\s\.\-']+$/.test(value)) {
                    showFieldError(fieldId, 'Name can only contain letters and basic punctuation');
                    field.addClass('error').removeClass('success');
                } else {
                    field.addClass('success').removeClass('error');
                }
                break;

            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    showFieldError(fieldId, 'Please enter a valid email address');
                    field.addClass('error').removeClass('success');
                } else {
                    field.addClass('success').removeClass('error');
                }
                break;

            case 'subject':
                if (value.length < 5) {
                    showFieldError(fieldId, 'Subject must be at least 5 characters long');
                    field.addClass('error').removeClass('success');
                } else {
                    field.addClass('success').removeClass('error');
                }
                break;

            case 'message':
                const wordCount = value.split(/\s+/).length;
                if (value.length < 10) {
                    showFieldError(fieldId, 'Message must be at least 10 characters long');
                    field.addClass('error').removeClass('success');
                } else if (wordCount < 3) {
                    showFieldError(fieldId, 'Message must contain at least 3 words');
                    field.addClass('error').removeClass('success');
                } else {
                    field.addClass('success').removeClass('error');
                }
                break;
        }
    }

    /**
     * Show alert message
     */
    function showAlert(type, message) {
        formAlert.removeClass('success error')
            .addClass(type)
            .html(getAlertIcon(type) + message)
            .fadeIn(300);
    }

    /**
     * Hide alert message
     */
    function hideAlert() {
        formAlert.fadeOut(300);
    }

    /**
     * Get icon for alert type
     */
    function getAlertIcon(type) {
        if (type === 'success') {
            return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> ';
        } else {
            return '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> ';
        }
    }

    /**
     * Set loading state on submit button
     */
    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.prop('disabled', true);
            submitBtn.find('.btn-text').hide();
            submitBtn.find('.btn-loading').show();
        } else {
            submitBtn.prop('disabled', false);
            submitBtn.find('.btn-text').show();
            submitBtn.find('.btn-loading').hide();
        }
    }
});
