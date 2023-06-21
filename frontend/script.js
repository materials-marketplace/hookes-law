document.getElementById("computationForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent form submission

  // Get input values
  var youngsModulus = document.getElementById("youngsModulus").value;
  var strain = document.getElementById("strain").value;
  var transformationId = null

  // Send form data to backend
  fetch('/transformations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ youngsModulus: youngsModulus, strain: strain })
  })
    .then(responseCreate => responseCreate.json())
    .then(transformation => {
      transformationId = transformation.id
      document.getElementById("id").innerText = transformationId;
      return fetch('/transformations/' + transformationId, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state: "RUNNING" })

      });
    })
    .then(responseUpdate => responseUpdate.json())
    .then(() => {
      return fetch('/datasets/' + transformationId, {
        method: 'GET'
      });
    })
    .then(responseResult => responseResult.json())
    .then(result => {
      document.getElementById("result").innerText = "Stress [MPa]: " + result.result;
    });
});
