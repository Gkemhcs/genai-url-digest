document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('add-url').addEventListener('click', () => {
        const urlInputs = document.getElementById('url-inputs');
        const newInput = document.createElement('div');
        newInput.classList.add('form-group');
        newInput.innerHTML = `
            <div class="input-group mb-2">
                <input type="url" class="form-control" name="urls" placeholder="Enter URL" required>
                <div class="input-group-append">
                    <button class="btn btn-danger delete-url" type="button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 30 30">
                            <path d="M 14.984375 2.4863281 A 1.0001 1.0001 0 0 0 14 3.5 L 14 4 L 8.5 4 A 1.0001 1.0001 0 0 0 7.4863281 5 L 6 5 A 1.0001 1.0001 0 1 0 6 7 L 24 7 A 1.0001 1.0001 0 1 0 24 5 L 22.513672 5 A 1.0001 1.0001 0 0 0 21.5 4 L 16 4 L 16 3.5 A 1.0001 1.0001 0 0 0 14.984375 2.4863281 z M 6 9 L 7.7929688 24.234375 C 7.9109687 25.241375 8.7633438 26 9.7773438 26 L 20.222656 26 C 21.236656 26 22.088031 25.241375 22.207031 24.234375 L 24 9 L 6 9 z"></path>
                        </svg>
                    </button>
                </div>
            </div>`;
        urlInputs.appendChild(newInput);
    });

    // Event delegation for dynamically added delete buttons
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-url')) {
            event.target.closest('.form-group').remove();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    darkModeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
    });
});

