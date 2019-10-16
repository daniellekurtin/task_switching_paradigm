# oxbridge_brainhack_2019
Task Switching Paradigm Construction

Hello! This aim of this project is to construct a task-switching paradigm. This paradigm will switch between three discrete, psychometrically opposed tasks- the digit span, spatial rotation, and either the spatial span or self-ordered search tasks. Participants will perform this task whilst we acquire both fMRI and high-density EEG imaging. The functional neuroimaging data, combined with structural data from a DWI scan, will then be used to model the brain during a task switch. But I’m getting ahead of myself. Let’s focus on some questions and rationale, written below, for this project. _If you have questions or comments on any of the jargon, rationale, or content below, please reach out to me at danielle.kurtin18@imperial.ac.uk_

## Why do we need to construct a new paradigm?
	
Most task-switching literature focuses on switching between tasks that rely on the same cognitive processes/ psychometric principals. While many cognitive processes recruit a “multiple demand cortex", there is evidence that the brain’s task activity and connectivity profiles are discrete and dissociable for separate tasks. Furthermore, the more psychometrically opposed the tasks are, the easier it is to separate the neuroimaging correlates of the task (Eyal et al, in press). I want to understand how brain reconfigures in task switching paradigms; specifically, whether the brain reorganizes in a top-down or bottom-up manner. To do this I need discrete, dissociable networks- like the ones generated from three psychometrically opposed tasks. 
 
 ## What are the paradigm parameters?
The task will be coded in Psychopy. More to come here. For information on how we can avoid display, motor, and other confounds, see the section at the very bottom titled _Confound Considerations_

## What do we have already?
We have bits of code for the tasks that are (1) programmed in MatLab using PsyToolbox (2) result in different display and motor responses. I will add to this in the appropriate brances in the weeks to come.

## Where do we need to go?
        1.	Change MatLab to Psychopy
        2.	Change the task code to fit the display and motor parameters for this task
        3.	Add lines for EEG and fMRI compatibility 
        4.	Pilot test to ensure
                 a.	It works
                 b.	There are no floor/ ceiling effects
                 c.	There is a switch cost
                 d.	All tasks are the same difficulty
                 e.	It works

## What can you do?
You can help SO MUCH! We don’t even need to wait until OxBridge to start! Take a look at the project branches. If you have any thoughts, ideas, comments, concerns, please write them in or reach out to me. I would love to help you with your project as well, so if you need any fMRI analysis using FSL or noninvasive brain stimulation advice, please reach out! 

Thank you for taking the time to read this. I look forward to your pulls and commits! 

Cheers,

Danielle



_Confound Considerations:_ 
1.	Switch cost will be measured in behavioral performance through reaction time and accuracy, and through functional neural  correlates as measured by EEG and fMRI
2.	To minimize bottom-up interference we will control for display confounds.  Color and luminosity can be processed using the MATLAB script rgb2gray for extracting luminance values, and mean2 for extracting contrast values. We can extract these values per stimuli per set and do an ANOVA between group (the tasks), luminance, and contrast to make sure there is no interaction or effect of the stimuli (Nikolla et al 2018; rdb2gray, 2016; mean2, 2016). 
3.	Further display confound will look at the presentation of the task, as the digit span relies on the flashing of multiple stimuli (numbers) in succession followed by a single choice, whereas the spatial rotation task presents a single stimulus that is followed by a single choice. The TACP of the digit span will be different from that of the spatial rotation not solely due to the unique cognitive demands of each, but partially due to the flashing of multiple stimuli in the digit span as opposed to only one in the spatial rotation. 
4.	To minimize reward history interference, we are not providing feedback for task performance. At the end of piloting sessions, we can ask if participants enjoyed or felt more successful during one task vs the others, and see if this is related to their performance. For example, if a participant feels like they performed better on one task than another, it may change their perception/ preparation for the task and potentially exhibited a lower switch cost at the beginning of the preferred task. Another means of addressing this is, during piloting, to ensure task difficulty and switch costs are relative to one another (measured in MRT and accuracy). 
5.	To minimize selection history interference and motor confounds, we will (1) counterbalance the amount of motor responses within and between tasks; ie, try to evenly distribute the number of clicks per task 

