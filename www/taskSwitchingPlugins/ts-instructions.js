var participant_info = {
    type: 'survey-text',
    questions: [
      {prompt: "How old are you?"}, 
      {prompt: "What gender are you?", placeholder: "Male/Female/Other"},
      {prompt: "What is your participant id?", placeholder: "001"}
    ],
  };




var instructions = {
    type: 'instructions',
    pages: [

        'Hello! Thank you for playing the task-switching game.',

        'I will go over the rules for the task. Then, you will play a demo of the task to get familiar with it. Finally, we will begin the task!',

        'This game switches between three tasks: the digit span, the spatial span, and the spatial rotation.',

        'You will play each task for about 10 minutes, then a grey screen with a white cross and a countdown will appear. This signifies a two minute break. Feel free to stretch, get water, but be sure to be ready when the task restarts! You will encounter two breaks during the task.',

        'All tasks have a similar format- a grid 6 boxes long and 6 boxes wide will appear.: <img src="img/blank_stimgrid.png"></img>',
        
        'The first grid will disappear and be replaced with three answer grids. You will have three seconds to answer, and the next trial will begin. Answer grids 1, 2, and 3 map to "b", "n", and "m" on your keyboard.',

        'During one task, The "Digit Span", six numbers will flash on the grid, one after the other.: <img src="img/DS_cuecard.png"></img>',
        
        'Your job is to remember the six numbers in order, and select the answer grid that has the 6 numbers from left to right. The other two answer grids will show the same numbers, except for one.: <img src="img/DS_answr_exmpl.png"></img>',

        'During the "Spatial Span" the grid will highlight 6 boxes, one after another. Your job is to remember which spaces have been occupied by boxes, and select the answer grid that shows all the boxes that were highlighted. The other two grids will show the same pattern, except for one.: <img src="img/SS_cuecard.png"></img>',

        'The "Spatial Rotation" is our last task.: <img src="img/SR_cuecard.png"></img>',
        
        'During the "Spatial Rotation" boxes will become highlighted, though instead of disappearing, they add one after another. The grid will then be rotated 90, 180, or 270 degrees.: <img src="img/SR_stim_exmpl.png"></img>',
        
        'Your job is to pick the answer grid that has the same pattern. The other two grids will show the same pattern as the answer grid, except for one box.: <img src="img/SR_answr_exmpl.png"></img>',

        'After you play each task for a few minutes, you will be shown a card announcing what the next task will be. The next task will start immediately.',  

        'Next is a demo of the task, so you can get used to the tasks.'

    ],
    show_clickable_nav: true
}