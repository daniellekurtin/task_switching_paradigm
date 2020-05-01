/**
 * Display a warning that there will be a new kind of task
 **/

jsPsych.plugins["ts-info-card"] = (function() {

  const plugin = {};

  plugin.info = {
    name: 'ts-info-card',
    description: '',
    parameters: {
      next_task_type: {
        type: jsPsych.plugins.parameterType.HTML_STRING,
        pretty_name: 'Next task type',
        default: undefined,
        description: 'The name of the next task type'
      },
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
    <p>New task type:</p>
    <h1>${trial.next_task_type}</h1>  
</div>`;
    display_element.innerHTML = html;

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
