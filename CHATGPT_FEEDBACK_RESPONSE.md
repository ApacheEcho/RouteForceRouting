<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Playbook Constraint Editor</title>
  <script src="https://unpkg.com/htmx.org@1.9.2"></script>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 p-6">
  <div class="max-w-2xl mx-auto bg-white p-6 rounded shadow">
    <h2 class="text-xl font-bold mb-4">Upload Playbook File</h2>
    <form
      hx-post="/api/v1/validate_playbook"
      hx-target="#error-output"
      hx-encoding="multipart/form-data"
      hx-on::after-request="if (event.detail.xhr.status === 200) {
    try {
      const json = JSON.parse(event.detail.xhr.responseText);
      const errorOutput = document.getElementById('error-output');
      errorOutput.innerHTML = '';
      if (json.valid) {
        const formData = new FormData();
        formData.append('file', document.querySelector('input[name=file]').files[0]);

        fetch('/api/v1/preview_playbook', {
          method: 'POST',
          body: formData
        })
        .then(response => response.text())
        .then(html => {
          document.getElementById('preview-output').innerHTML = html;
        })
        .catch(error => {
          console.error('Error loading playbook preview:', error);
        });
      } else if (json.errors) {
        const ul = document.createElement('ul');
        ul.classList.add('list-disc', 'pl-5');
        json.errors.forEach(error => {
          const li = document.createElement('li');
          li.textContent = error;
          ul.appendChild(li);
        });
        errorOutput.appendChild(ul);
      }
    } catch (e) {
      console.error('Failed to parse JSON from validate_playbook response', e);
    }
  }"
      class="space-y-4"
    >
      <input type="file" name="file" class="block w-full text-sm text-gray-700" />
      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Validate Constraints
      </button>
      <button type="button" onclick="location.reload()" class="text-blue-600 underline text-sm">
        Clear & Upload New
      </button>
    </form>
    <div id="error-output" class="mt-6 text-sm text-red-700 space-y-2">
      <template id="error-template">
        <ul class="list-disc pl-5">
          <!-- Dynamically injected error messages -->
        </ul>
      </template>
    </div>
    <div id="preview-output" class="mt-6 text-sm text-green-700 space-y-2">
      <!-- Valid playbook preview will appear here -->
      <!-- Example format to match incoming HTML preview:
      <div class="bg-white shadow rounded p-4">
        <h3 class="text-lg font-bold">Chain A</h3>
        <ul class="list-disc ml-6">
          <li>priority: 1</li>
          <li>skip_sundays: true</li>
          <li>visit_hours: 8am - 5pm</li>
        </ul>
      </div>
      -->
    </div>
  </div>
</body>
</html>
