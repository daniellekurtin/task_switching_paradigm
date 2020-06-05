/**
 * JSPsych instructions objects and similar for the demo and main tasks
 */

/**
 * Build the JSPsych instructions plugin for welcoming people to the demo.
 * @type {{}}
 */
const demo_instructions = {
    type: 'instructions',
    pages: [
        'Welcome to the <strong>Task Switching Game</strong>!',
        'This game switches between three tasks: the <strong>Digit Span</strong>, the <strong>Spatial Span</strong>, and the <strong>Spatial Rotation</strong>.',
        'You will see some instructions on how to play each task in the game. You will then get a little bit of practice with each task which you can play until you are comfortable with how to play each one. If you want to stop playing at any point you are free to do so, and we will ask you for your explicit consent before we begin to record data on your performance.',
        'All tasks have a similar format - a grid 6 boxes long and 6 boxes wide will appear: <img src="img/blank_stimgrid.png"></img>',
        'The first grid will disappear and be replaced with three answer grids. You will have <strong>three seconds</strong> to answer by clicking on your grid of choice, and the next trial will begin.',
        '<p>During the <strong>Digit Span</strong> task, six numbers will flash on the grid, one after the other:</p><img src="img/DS_cuecard.png"></img><p>Your job is to <strong>remember the six numbers in order</strong>, and click on the answer grid that has those 6 numbers from left to right. The other two answer grids will show similar numbers, except that one of them will be different</p>',
        '<p>During the <strong>Spatial Span</strong> the grid will highlight 6 boxes, one after another. Your job is to <strong>remember which spaces have been occupied by boxes</strong>, and select the answer grid that shows all the boxes that were highlighted.</p><img src="img/SS_cuecard.png"></img><p>Once again, the other two grids will show the same pattern, except for one box.</p>',
        '<p>During the <strong>Spatial Rotation</strong> boxes will become highlighted. The boxes will add one after another instead of disappearing.</p><img src="img/SR_cuecard.png"></img><p>You job is to <strong>pick the answer which shows the pattern of highlighted boxes <em>rotated through 90, 180, or 270 degrees</em></strong>. Once again, the other answers will be similar, but with a single box changed.</p>',
        'After you play each task for a few rounds, you will be shown a card announcing what the next task will be. The next task will start <strong>immediately</strong>.',
        'Now you can begin a demo of the task, so you can get used to the tasks. Most people feel as though the tasks are difficult, and <em>they are meant to be challenging</em>. However, <strong>people often perform much better than they feel they did</strong>. We encourage you to answer as quickly and as accurately as you can, and hope you have some fun!',
    ],
    show_clickable_nav: true
};

/**
 * Build JSPsych instructions plugin for redirecting participants to the main task or to replay the demo.
 * @type {{}}
 */
const demo_thanks = {
    type: 'instructions',
    pages: [
        `
<p>You have completed the task switching game demo!</p>
<p>You can now:</p>
<p><a href="main-task.html">go to the main experiment</a></p>
<p>or</p>
<p><a href="index.html?skipIntro=true">replay the demo</a></p>
`
    ],
    show_clickable_nav: false
};

var welcome = {
    type: 'instructions',
    pages: [
        'Welcome to the main <strong>Task Switching Game</strong> experiment!',
        'Now that you are familiar with how the tasks work from the demo, we will ask you to read and approve our <strong>informed consent</strong> pages. We will then ask you to provide some very <strong>basic demographic information</strong>, and then you can proceed with the <strong>main experiment</strong>. We expect the whole process to take around <strong>20 minutes</strong>.'
    ],
    show_clickable_nav: true
};

var consent = {
    type:'consent',
    bodyText: `
    <p>This game is used to investigate working memory. In this task, you will be required to remember a sample stimulus and, after a delay, identify whether which answer presented is correct.</p>
    <p>Before starting the experiment, please make sure: You have understood the basic information about this experiment. You are aware of what your participation involves. You confirm you <strong>do not have a history of migraine or epilepsy</strong> or any other neurological or psychiatric conditions. You understand that by taking part you are consenting to your data being used to assist in research into neuroscience and cognition. The <strong>data we collect will be analysed anonymously</strong> and we do not store any personally identifiable information (such as IP address location name or contact details). <strong>You may withdraw at any time</strong> without penalty or consequences of any kind. Anonymised data collected up to the point of withdrawal will be kept (data from tests and answers to the demographic questions). Your participation in this research is completely <strong>VOLUNTARY</strong>.</p>
    `,
    items: [
        'I have <strong>read and understood</strong> the study description.',
        'I am <strong>at least 18</strong> years old.',
        'I <strong>agree to participate</strong> in this study.'
    ],
    button_label: "Begin experiment!"
};

var participant_info = {
    type: 'survey-text',
    questions: [
      {prompt: "How old are you?"}, 
      {prompt: "What gender are you?", placeholder: "Male/Female/Other"},
      {prompt: "What is your participant id?", placeholder: "001"}
    ],
    on_finish: (data) => recordDemographics(data)
  };

var instructions = {
    type: 'instructions',
    pages: [

        '<p><strong>Thank you!</strong></p><p>You are now ready to begin.</p><p>We advise you to answer as <strong>quickly</strong> and as <strong>accurately</strong> as you can, and hopefully have some <strong>fun</strong>!</p>',

    ],
    show_clickable_nav: true
}

var end_thankyou = {
  type: 'instructions',
  pages: [
      'Thank you for completing the Task Switching Paradigm! Be sure to notify the researchers you have completed the task to recieve SONA credits!'
  ],
  show_clickable_nav: false
}