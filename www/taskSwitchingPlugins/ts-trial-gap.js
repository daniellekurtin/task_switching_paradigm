/**
 * Force a gap between trials
 **/

jsPsych.plugins["ts-trial-gap"] = (function() {

  const plugin = {};

  plugin.info = {
    name: 'ts-trial-gap',
    description: 'Gap between taskSwitching trials',
    parameters: {
      trial_duration: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Duration',
        default: undefined,
        description: 'The duration of the gap'
      },
    }
  };

  plugin.trial = function(display_element, trial) {
    const trial_data = {
      start_time: performance.now(),
      end_time: null
    };

    function clearDisplay() {
      // clear the display
      display_element.innerHTML = '';
    }

    clearDisplay();

    // function to end trial when it is time
    function end_trial() {
      trial_data.end_time = performance.now();
      // kill any remaining setTimeout handlers
      jsPsych.pluginAPI.clearAllTimeouts();
      clearDisplay();
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
