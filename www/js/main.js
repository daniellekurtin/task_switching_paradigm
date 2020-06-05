/**
 * Functions supporting the running of the task switching game
 */

/**
 * Update status in the loading screen.
 */
function message(s) {
    document.getElementById("LoadingStatus").innerHTML = s;
}

/**
 * Register an error in the loading screen and console.
 */
function error(s, e) {
    message(s);
    console.error(e);
}

function loadTrialList(bp = null) {
    message('Fetching experiment details from server...');
    if(bp) {
        if(!/\.json$/i.test(bp))
            return error("Could not load experiment.", `Bad blueprint path: ${bp}`);
        return fetch(`./blueprints/${bp}`)
            .then(async r => {return {
                blueprint_id: bp,
                blueprint: {trials: JSON.stringify(await r.json())} // Match php blueprint formatting
            }})
            .catch(e => error(`Could not load experiment.`, e));
    }
    return fetch('./handle-blueprints.php', {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    })
        .then(r => r.json())
        .catch(e => error("Could not load experiment.", e));
}

/**
 * Create a jsPsych experiment timeline by adding participant details gathering stuff to the sequence defined in trialTypes
 * @param trials {object[]} Trial specifications
 * @return {object[]} jsPsych plugin trials
 */
function createTimeline(json) {
    let out;
    try {
        jsPsych.data.addProperties({blueprint_id: json.blueprint_id});
        const trials = JSON.parse(json.blueprint.trials);
        if(typeof trials.trials != "undefined")
            out = JSON.parse(trials.trials).map(t => parseTrial(t));
        else
            out = trials.map(t => parseTrial(t));
    } catch(e) {
        error("Error preparing experiment.", e);
    }
    return out;
}

function parseTrial(trial) {
    const t = {};
    const tt = trial["py/object"];
    if(/Component/.test(tt)) {
        if(/ComponentStart$/.test(tt)) {
            return {
                type: "ts-intro",
                trial_duration: trial.duration * 1000
            }
        } else if(/ComponentTrialGap$/.test(tt)) {
            return {
                type: "ts-trial-gap",
                trial_duration: trial.break_duration * 1000
            }
        } else if(/ComponentInfoCard$/.test(tt)) {
            return {
                type: "ts-info-card",
                trial_duration: trial.break_duration * 1000,
                next_task_type: trial.next_task
            }
        } else if(/ComponentRest$/.test(tt)) {
            const d = typeof trial.duration === "Object"?
                trial.duration["py/reduce"][1]["py/tuple"][0] : trial.duration;
            return {
                type: "ts-block-break",
                trial_duration: d * 1000
            }
        }
    } else if(/Trial/.test(tt)) {
        t.type = "ts-trial";
        t.max_response_time = trial.max_response_time * 1000;
        t.stimulus = trial.stimulus;
        t.stimulus_duration = trial.stimulus_duration * 1000;
        t.delay_before_response = trial.delay_before_response * 1000;
        t.answers = trial.answers;
        t.answer_index = trial.answer_index;

        if(/TrialDigitSpan$/.test(tt))
            return {trial_type: "ts-trial-digit-span", ...t};
        else if(/TrialSpatialSpan$/.test(tt))
            return {trial_type: "ts-trial-spatial-span", ...t};
        else if(/TrialSpatialRotation$/.test(tt))
            return {trial_type: "ts-trial-spatial-rotation", ...t};
    }
    throw `No matching type conditions found for trial type ${tt}`;
}


function addInstructionsToTimeline(timeline, demoInstructions = false) {
    if(demoInstructions) {
        timeline = [...timeline, demo_thanks];
        // Support skipping intro if they've seen it before
        if(jsPsych.data.getURLVariable('skipIntro') !== "true")
            timeline = [demo_instructions, ...timeline];
    } else
        timeline = [welcome, consent, participant_info, instructions, ...timeline, end_thankyou];

    return timeline;
}

function begin(timeline, isDemo = false) {
    // Remove initial 2-minute countdown
    timeline.shift();

    timeline = addInstructionsToTimeline(timeline, isDemo);

    // Add data saving onto each of the timeline trials
    if(!isDemo) {
        // Add a unique participant Id to track this participant even before we have had them give us their id
        jsPsych.data.addProperties({
            auto_participant_id: performance.now().toString() + '_' + Math.round(Math.random() * 100000).toString(),
            participant_age: NaN,
            participant_gender: null,
            participant_id: null
        });
        // Add automatic saving of data
        timeline.forEach(x => {
            if(!x.on_finish)
                x.on_finish = saveLastTrialData;
        });
    }

    jsPsych.init({
        timeline: timeline
    });
}

/**
 * Insert participant demographic data fields into the jsPsych data
 * @param data {Object} trial data from demographics form
 */
function recordDemographics(data) {
    try {
        const answers = JSON.parse(data.responses);

        jsPsych.data.addProperties({
            participant_age: answers.Q0,
            participant_gender: answers.Q1,
            participant_id: answers.Q2
        });

        saveLastTrialData(data);
    } catch(e) {
        error("Could not save demographic responses!", e);
    }
}

function saveLastTrialData() {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'write-data.php');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if(xhr.status == 200){
            var response = JSON.parse(xhr.responseText);
            if(response.success !== true) {
                if(!window.ignoreSaveErrors) {
                    saveErrorPopup(response.message);
                }
            }
        }
    };
    xhr.send(jsPsych.data.getLastTrialData().json());
    console.log('Saving data:');
    console.log(jsPsych.data.getLastTrialData().json());
}

/**
 * Display a modal which informs the participant of an error and allows them to reload the experiment or ignore and continue.
 */
function saveErrorPopup(err) {
    console.log({dataSaveError: err});
    document.body.innerHTML += `
    <div id="errorModal" class="showError">
        <div>
            <h1>Error saving data!</h1>
            <p>We ran into an error while trying to save the data.</p>
            <p>If this has happened early in the experiment, we recommend you try <a href="main-task.html">refreshing the page</a>.</p>
            <p>If you're further in, or do not want to start over, you can <span onclick="ignoreError()" class="link">ignore the error and continue</span>. If you do this, however, we won't be able to use your data.</p>
        </div>
    </div>
    `;
}

function ignoreError() {
    window.ignoreSaveErrors = true;
    document.getElementById('errorModal').classList.remove('showError');
}