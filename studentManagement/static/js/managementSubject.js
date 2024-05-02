document.getElementById('addSubjectForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var formData = new FormData(this);

    // Perform AJAX request to submit form data
    fetch('/url/to/submit/form', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            var messageElement = document.getElementById('message');
            if (response.ok) {
                messageElement.innerText = 'Thành công!'; // Display success message
                messageElement.classList.remove('alert-danger');
                messageElement.classList.add('alert-success');
            } else {
                messageElement.innerText = 'Lỗi!'; // Display error message
                messageElement.classList.remove('alert-success');
                messageElement.classList.add('alert-danger');
            }
            messageElement.style.display = 'block'; // Show message div
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

// Get the select all checkbox
var selectAllCheckbox = document.getElementById('selectAll');

// Get all checkboxes in the table body
var tableCheckboxes = document.querySelectorAll('table tbody input[type="checkbox"]');

// Add event listener to select all checkbox
selectAllCheckbox.addEventListener('change', function() {
    // Loop through all checkboxes in the table body
    tableCheckboxes.forEach(function(checkbox) {
        // Set the checked property of each checkbox to match the select all checkbox
        checkbox.checked = selectAllCheckbox.checked;
    });
});
