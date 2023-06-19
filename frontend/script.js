document.getElementById("computationForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent form submission

  // Get input values
  var stiffness = document.getElementById("stiffness").value;
  var displacement = document.getElementById("displacement").value;
  var transformationId = null

  // Send form data to backend
  fetch('/transformations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ stiffness: stiffness, displacement: displacement })
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
      document.getElementById("result").innerText = "Result: " + result.result;
    });
});
