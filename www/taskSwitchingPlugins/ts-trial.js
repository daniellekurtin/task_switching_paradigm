/**
 * Run one of the several kinds of trials
 **/

jsPsych.plugins["ts-trial"] = (function() {

  const plugin = {};

  plugin.info = {
    name: 'ts-trial',
    description: 'Run a given trial',
    parameters: {
      stimulus: {
        type: jsPsych.plugins.parameterType.OBJECT,
        pretty_name: 'Stimulus',
        default: undefined,
        description: 'The array of grid objects used for the stimulus'
      },
      stimulus_duration: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Stimulus duration',
        default: undefined,
        description: 'How long to hide the stimulus.'
      },
      answers: {
        type: jsPsych.plugins.parameterType.OBJECT,
        pretty_name: 'Answer grids',
        default: undefined,
        description: 'The array of grid objects used for the answers'
      },
      answer_index: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Correct answer index',
        default: undefined,
        description: 'Index of the correct answer.'
      },
      max_response_time: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Max response time',
        default: undefined,
        description: 'How long to show the trial.'
      },
      delay_before_response: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Delay before response',
        default: undefined,
        description: 'Delay before a response can be submitted after stimulus has been displayed.'
      },
      trial_type: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: "Trial task type",
        default: undefined,
        description: "The task type of the trial"
      }
    }
  };

  plugin.trial = function(display_element, trial) {

    const data = {
      stimulus_on: performance.now(),
      stimulus_off: [],
      response_enabled_time: null,
      response_time: null,
      response_answer: null,
      answer_index: trial.answer_index,
      response_correct: null
    };

    function clearDisplay() {
      // clear the display
      display_element.innerHTML = '';
      display_element.classList.remove(
          'awaiting-response',
          'received-response'
      );
    }

    function drawGrid(g, blank = false) {
      const grid = document.createElement('div');
      grid.classList.add('grid', blank? "blank" : "stimulus");
      for(let r = 0; r < g.length; r++) {
        const row = g[r];
        for(let c = 0; c < row.length; c++) {
          const cell = document.createElement('div');
          cell.innerHTML = row[c] !== null && !blank? row[c] : "";
          cell.classList.add(
              'grid-cell',
              `grid-row-${r}`,
              `grid-col-${c}`,
              `grid-cell-${r}-${c}`,
              cell.innerHTML === ""? 'grid-cell-blank' : 'grid-cell-filled'
          );
          grid.appendChild(cell);
        }

      }
      return grid;
    }

    function showStimulus() {
      // display stimulus
      const stim = document.createElement('div');
      stim.classList.add('stimuli');
      // Add a blank grid to show at the end of the stimulus set
      stim.appendChild(drawGrid(trial.stimulus[0], true));
      // Draw grids on top of one another with the first stimulus uppermost and tell them to remove themselves at the appropriate junctures
      for(let i = trial.stimulus.length - 1; i >= 0; i--) {
        const grid = drawGrid(trial.stimulus[i]);
        stim.appendChild(grid);
        jsPsych.pluginAPI.setTimeout(() => {
          data.stimulus_off.push(performance.now());
          grid.classList.add('hidden');
        }, trial.stimulus_duration * (i + 1));
      }

      display_element.innerHTML = "";
      display_element.appendChild(stim);

      const answers = display_element.appendChild(document.createElement('div'));
      answers.classList.add('answers');
      for(let i = 0; i < trial.answers.length; i++) {
        const grid = drawGrid(trial.answers[i]);
        grid.id = `Answer${i}`;
        grid.classList.add("answer");
        grid.dataset.answerId = i.toString();
        answers.appendChild(grid);
      }


      jsPsych.pluginAPI.setTimeout(
          getResponse,
          trial.stimulus_duration * trial.stimulus.length +
          trial.delay_before_response
      );
    }

    function getResponse() {
      display_element.classList.add('awaiting-response');

      data.response_enabled_time = performance.now();
      document.querySelectorAll('.answer')
          .forEach(elm => elm.addEventListener('click', answer));

      jsPsych.pluginAPI.setTimeout(end_trial, trial.max_response_time);
    }

    /**
     * Register an answer
     * @param e {Event}
     */
    function answer(e) {
      if(!data.response_answer) {
        data.response_answer = e.currentTarget.dataset.answerId;
        data.response_time = performance.now();
        data.response_correct = data.response_answer == data.answer_index;

        console.log(data)

        e.currentTarget.classList.add('chosen');
        display_element.classList.add('received-response');
      }
    }

    // function to end trial when it is time
    function end_trial() {
      // kill any remaining setTimeout handlers
      jsPsych.pluginAPI.clearAllTimeouts();
      clearDisplay();

      // move on to the next trial
      jsPsych.finishTrial(data);
    }

    clearDisplay();
    showStimulus();
  };

  return plugin;
})();
