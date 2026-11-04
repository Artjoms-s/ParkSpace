(function () {
  const pad = (number) => String(number).padStart(2, '0');

  function setDateMinimums() {
    document.querySelectorAll('input[type="date"]').forEach((field) => {
      const now = new Date();
      const localDate = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
      field.min = localDate;
    });
  }

  function setupClockPicker(picker) {
    const key = picker.dataset.clockPicker;
    const dateField = document.getElementById(`${key}_date`);
    const combinedField = document.getElementById(`${key}_time`);
    const clockField = document.getElementById(`${key}_clock`);
    const label = document.getElementById(`${key}_clock_label`);
    const openButton = picker.querySelector('[data-clock-open]');
    const popup = picker.querySelector('.clock-popup');
    const dial = picker.querySelector('[data-clock-dial]');
    const title = picker.querySelector('[data-clock-title]');
    const stepLabel = picker.querySelector('[data-clock-step]');
    const backButton = picker.querySelector('[data-clock-back]');
    const periodButtons = Array.from(picker.querySelectorAll('[data-hour-half]'));

    if (!dateField || !combinedField || !clockField || !label || !openButton || !popup || !dial) return;

    let selectedHour = null;
    let half = 0;
    let step = 'hour';

    function syncCombinedTime() {
      combinedField.value = dateField.value && clockField.value
        ? `${dateField.value}T${clockField.value}`
        : '';
    }

    function closePopup() {
      popup.hidden = true;
      openButton.setAttribute('aria-expanded', 'false');
    }

    function showPopup() {
      popup.hidden = false;
      openButton.setAttribute('aria-expanded', 'true');
      const value = clockField.value.match(/^(\d{2}):(\d{2})$/);
      if (value) {
        selectedHour = Number(value[1]);
        half = selectedHour >= 12 ? 1 : 0;
      } else {
        selectedHour = null;
        half = 0;
      }
      showHours();
    }

    function positionDialButtons(values, onPick, isMinute) {
      dial.replaceChildren();
      values.forEach((value, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'dial-value';
        button.textContent = pad(value);
        const angle = (index * 30 - 90) * Math.PI / 180;
        const radius = isMinute ? 39 : 39;
        button.style.left = `${50 + Math.cos(angle) * radius}%`;
        button.style.top = `${50 + Math.sin(angle) * radius}%`;
        button.setAttribute('aria-label', isMinute ? `Minūte ${pad(value)}` : `Stunda ${pad(value)}`);
        if (isMinute && clockField.value && Number(clockField.value.slice(3)) === value) button.classList.add('selected');
        if (!isMinute && selectedHour === value) button.classList.add('selected');
        button.addEventListener('click', () => onPick(value));
        dial.appendChild(button);
      });
      dial.classList.toggle('minute-dial', Boolean(isMinute));
    }

    function showHours() {
      step = 'hour';
      title.textContent = 'Izvēlies stundu';
      stepLabel.textContent = '1 no 2';
      backButton.hidden = true;
      picker.querySelector('[data-hour-periods]').hidden = false;
      periodButtons.forEach((button) => button.classList.toggle('active', Number(button.dataset.hourHalf) === half));
      const hours = Array.from({ length: 12 }, (_, index) => index + half * 12);
      positionDialButtons(hours, (hour) => {
        selectedHour = hour;
        showMinutes();
      }, false);
    }

    function showMinutes() {
      step = 'minute';
      title.textContent = `Stunda ${pad(selectedHour)} — izvēlies minūtes`;
      stepLabel.textContent = '2 no 2';
      backButton.hidden = false;
      picker.querySelector('[data-hour-periods]').hidden = true;
      const minutes = Array.from({ length: 12 }, (_, index) => index * 5);
      positionDialButtons(minutes, (minute) => {
        clockField.value = `${pad(selectedHour)}:${pad(minute)}`;
        label.textContent = clockField.value;
        label.classList.add('has-time');
        syncCombinedTime();
        closePopup();
      }, true);
    }

    openButton.addEventListener('click', () => popup.hidden ? showPopup() : closePopup());
    picker.querySelectorAll('[data-clock-close]').forEach((button) => button.addEventListener('click', closePopup));
    periodButtons.forEach((button) => button.addEventListener('click', () => {
      half = Number(button.dataset.hourHalf);
      showHours();
    }));
    backButton.addEventListener('click', showHours);
    dateField.addEventListener('change', syncCombinedTime);

    const initialTime = clockField.value || (combinedField.value.includes('T') ? combinedField.value.split('T')[1] : '');
    if (/^\d{2}:\d{2}$/.test(initialTime)) {
      clockField.value = initialTime;
      label.textContent = initialTime;
      label.classList.add('has-time');
    }
    if (!dateField.value && combinedField.value.includes('T')) dateField.value = combinedField.value.split('T')[0];
    syncCombinedTime();
  }

  document.addEventListener('DOMContentLoaded', () => {
    setDateMinimums();
    document.querySelectorAll('[data-clock-picker]').forEach(setupClockPicker);

    document.querySelectorAll('[data-reservation-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');
        const startTime = document.getElementById('start_time');
        const endTime = document.getElementById('end_time');
        if (!startDate.value || !endDate.value || !startTime.value || !endTime.value) {
          event.preventDefault();
          alert('Lūdzu, izvēlies sākuma un beigu datumu un laiku.');
        }
      });
    });
  });
})();
