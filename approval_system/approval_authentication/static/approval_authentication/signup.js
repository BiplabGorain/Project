$(document).ready(function () {
	$("#signup-form").submit(function (event) {
		event.preventDefault(); // Prevent default form submission
		var formData = {
			email: $("#email").val(),
			username: $("#username").val(),
			password: $("#password").val(),
		};

		// Send form data to API using AJAX (adjust the API endpoint URL)
		$.ajax({
			url: "/api/v1/sign_up/",
			type: "POST",
			data: formData,
			success: function (response) {
				alert("Registration successful!"); // Show success message
			},
			error: function (xhr, status, error) {
				alert("Registration failed. Please try again."); // Show error message
			},
		});
	});
});
