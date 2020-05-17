/* ts-consent.js
 * Matt Jaquiery
 *
 * This plugin displays consent info with checkboxes to acknowledge each section
 *
 */

jsPsych.plugins.consent = (function() {

  var plugin = {};

  plugin.info = {
    name: 'consent',
    description: '',
    parameters: {
      items: {
        type: jsPsych.plugins.parameterType.HTML_STRING,
        pretty_name: 'Checkboxes',
        default: undefined,
        array: true,
        description: 'Each element of the array is the content for a single checkbox.'
      },
      button_label: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Button label okay',
        default: 'Okay',
        description: 'The text that appears on the button to go forwards.'
      }
    }
  }

  plugin.trial = function(display_element, trial) {

    var start_time = performance.now();
    var check_times = [];

    var html = "";

    for(var i = 0; i < trial.items.length; i++) {
        check_times.push(0);
        html += '<div class="item"><input type="checkbox" name="agree" data-nth="' + i + '"/>' + trial.items[i] + '</div>';
    }

    html += "<div class='jspsych-instructions-nav' style='padding: 10px 0px;'>";
    html += "<button id='jspsych-consent-okay' class='jspsych-btn' style='margin-right: 5px;'>" + trial.button_label+"</button>";
    html += "</div>";

    display_element.innerHTML = html;

    var boxes = display_element.querySelectorAll('input[type="checkbox"][name="agree"]');
    boxes.forEach(b => b.addEventListener('change', updateCheckTime));
    document.getElementById('jspsych-consent-okay').addEventListener('click', checkBoxes);

    function updateCheckTime(evt) {
        evt = evt || window.event;
        var box = evt.currentTarget;
        if(!box.checked)
            return;
        check_times[parseInt(box.dataset.nth)] = performance.now();
        box.parentElement.classList.remove('bad');
    }

    function checkBoxes() {
        var boxes = display_element.querySelectorAll('input[type="checkbox"][name="agree"]');
        var okay = true;
        boxes.forEach(b => {
            if(b.checked)
                b.parentElement.classList.remove('bad');
            else {
                b.parentElement.classList.add('bad');
                okay = false;
            }
        });

        if(okay)
            endTrial();
    }

    function endTrial() {

      display_element.innerHTML = '';

      var trial_data = {
        "check_times": JSON.stringify(check_times),
        "rt": performance.now() - start_time
      };

      jsPsych.finishTrial(trial_data);
    }
  };

  return plugin;
})();
