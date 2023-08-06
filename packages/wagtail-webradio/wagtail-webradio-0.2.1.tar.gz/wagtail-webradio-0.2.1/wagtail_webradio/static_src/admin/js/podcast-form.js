import $ from 'jquery';

const debounce = (callback, wait) => {
  let timeoutId = null;

  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      callback(...args);
    }, wait);
  };
};

/**
 * Format the time from seconds to HH:MM:SS.
 * @param {Number} seconds
 * @return {String}
 */
const formatDuration = (seconds) => {
  return new Date(1000 * seconds).toISOString().substr(11, 8);
};

$(function () {
  const urlInput = document.querySelector('input#id_sound_url');
  const durationInput = document.querySelector('input#id_duration');
  const isValidInput = document.querySelector('input#id_is_sound_url_valid');

  // Create a new Audio object with the current sound_url value to validate it
  // and set the duration value with the audio duration
  const retrieve = debounce(() => {
    isValidInput.value = '0';

    if (!urlInput.value) {
      durationInput.value = '';
      return;
    }

    const audio = new Audio();
    audio.preload = 'metadata';

    audio.addEventListener('error', () => {
      durationInput.value = '';
    });
    audio.addEventListener('loadedmetadata', () => {
      isValidInput.value = '1';
      durationInput.value =
        audio.duration === Infinity ? '' : formatDuration(audio.duration);
    });

    audio.src = urlInput.value;
  }, 500);

  urlInput.addEventListener('input', retrieve);

  // Check the current sound URL on page load
  retrieve();
});
