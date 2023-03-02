document.addEventListener('DOMContentLoaded', function () {
            const formInputs = document.querySelectorAll('form input');
            for (let i = 0; i < formInputs.length; i++) {
				formInputs[i].addEventListener('change', function () {
					fetch('/', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json'
						},
						body: JSON.stringify({
							formData: getFormData()
						})
					})
						.then(response => {
							console.log(response);
						})
						.catch(error => {
							console.error(error);
						});
				});
			}
		});

		function getFormData() {
            const formData = {};
            const formInputs = document.querySelectorAll('form input');
            for (let i = 0; i < formInputs.length; i++) {
				formData[formInputs[i].name] = formInputs[i].value;
			}
			return formData;
		}