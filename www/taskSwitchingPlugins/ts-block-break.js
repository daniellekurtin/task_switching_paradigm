/**
 * Display a warning that there will be a new kind of task
 **/

jsPsych.plugins["ts-block-break"] = (function() {

  const plugin = {};

  plugin.info = {
    name: 'ts-block-break',
    description: '',
    parameters: {
      trial_duration: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Trial duration',
        default: null,
        description: 'How long to show the trial.'
      },
    }
  };

  plugin.trial = function(display_element, trial) {
    const trial_data = {
      start_time: performance.now(),
      end_time: null
    };

    // display stimulus
    const html = `
<div id="jspsych-html-button-response-stimulus">
    <h1>Break time</h1>
    <p>Resuming in <span id="counter"></span>s</p> 
</div>`;
    display_element.innerHTML = html;

    function updateCounter(x) {
      const gap = 1000;
      x -= gap;
      document.getElementById('counter')
          .innerText = Math.round(x / 1000).toString();
      jsPsych.pluginAPI.setTimeout(() => updateCounter(x), gap);
    }

    updateCounter(trial.trial_duration);

    // function to end trial when it is time
    function end_trial() {
      trial_data.end_time = performance.now();
      // kill any remaining setTimeout handlers
      jsPsych.pluginAPI.clearAllTimeouts();
      // clear the display
      display_element.innerHTML = '';
      // move on to the next trial
      jsPsych.finishTrial(trial_data);
    }

    // end trial if time limit is set
    if (trial.trial_duration !== null) {
      jsPsych.pluginAPI.setTimeout(function() {
        end_trial();
      }, trial.trial_duration);
    }
  };

  return plugin;
})();
