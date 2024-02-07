document.addEventListener('DOMContentLoaded', function () {
    // Get the form element
    const form = document.querySelector('form');

    // Add a submit event listener to the form
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // Get the file input element
        const videoInput = document.getElementById('video');

        // Create FormData object to store form data
        const formData = new FormData();

        // Append the selected video file to the FormData object
        formData.append('video', videoInput.files[0]);

        // Use Fetch API to send the video to the backend
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display the response from the backend (e.g., success message)
            // data = JSON.parse(data)
            console.log(data);

            // Assuming the backend returns base64-encoded video data
            const videoElement = document.createElement('video');
            const subtitleDisplay = document.createElement('div');
            subtitleDisplay.setAttribute("id", "subtitle-display");

            videoElement.src = 'data:video/mp4;base64,' + data.video_data;
            videoElement.controls = true;

            // Load and display subtitles if available
            if (data.subtitle_data) {
                const track = document.createElement('track');
                track.kind = 'captions';
                track.label = 'English';
                track.srclang = 'en';
                track.src = 'data:text/vtt;charset=utf-8;base64,' + data.subtitle_data;

                // Append the track to the video element
                videoElement.appendChild(track);

                // Display subtitles
                subtitleDisplay.innerHTML = 'Subtitles: Enabled';
                videoElement.textTracks[0].mode = 'showing';
            } else {
                subtitleDisplay.innerHTML = 'Subtitles: Not Available';
            }

            // Append the video element to the "video-display" div
            const videoDisplayDiv = document.getElementById('video-display');
            videoDisplayDiv.innerHTML = ''; // Clear previous content
            videoDisplayDiv.appendChild(videoElement);
            videoDisplayDiv.appendChild(subtitleDisplay);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
