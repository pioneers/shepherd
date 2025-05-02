var socket = io("/");
var stageTimer = false;
var myStageTimeout;
var state_time;
var state;
var is_timer_paused = null;
var prev_curr_time;
var total_game_time;
var minigames;
var progression_bar;
var start_audio;
var match_audio;
var end_audio; 
var audio_started;

document.addEventListener('DOMContentLoaded', () => {
// Calculate progress bar position

start_audio = new Audio("../static/pirate_noises/pirate_cannon_short.wav");
match_audio = new Audio("../static/pirate_noises/pirate_music.wav");
end_audio = new Audio("../static/boxing_bell.wav");
audio_started = false;

const teamScores = document.querySelectorAll('.challenge-count');
const progressFill = document.querySelector('.progress-fill');

function updateProgressBar() {
    const team1Score = parseInt(teamScores[0].dataset.score);
    const team2Score = parseInt(teamScores[1].dataset.score);
    const total = team1Score + team2Score;
    let team1Percentage;
    if (!total) {
        team1Percentage = 50;
    } else {
        team1Percentage = ((1 - (team1Score / total)) * 100);
    }
    progressFill.style.width = `${team1Percentage}%`;
}

// Initial update
updateProgressBar();

// Update when scores change (you can call this function when scores update)
window.updateScores = (team1, team2) => {
    teamScores[0].dataset.score = team1;
    teamScores[1].dataset.score = team2;
    teamScores[0].textContent = team1;
    teamScores[1].textContent = team2;
    updateProgressBar();
}

socket.on('connect', (data) => {
console.log("Successful ydl message: connect");
socket.emit('join', 'scoreboard');

progression_bar = $(".progression-bar");
});

socket.on('teams_info', (match_info) => {
    console.log("Successful ydl message: teams_info");
    console.log(`received team header with info ${match_info}`);
    match_info = JSON.parse(match_info);
    match_num = match_info.match_num;
    team_name_b1 = match_info.teams[0]["team_name"];
    team_num_b1 = match_info.teams[0]["team_num"];
    team_name_b2 = match_info.teams[1]["team_name"];
    team_num_b2 = match_info.teams[1]["team_num"];
    team_name_g1 = match_info.teams[2]["team_name"];
    team_num_g1 = match_info.teams[2]["team_num"];
    team_name_g2 = match_info.teams[3]["team_name"];
    team_num_g2 = match_info.teams[3]["team_num"];
    updateTeam(team_name_b1, team_num_b1, team_name_b2, 
        team_num_b2, team_name_g1, team_num_g1, team_name_g2, team_num_g2);
});

// USE STATE, NOT STAGE
socket.on('state', (state_info) => {
    console.log("Successful ydl message: state");
    console.log(`received team header with info ${state_info}`);
    state_info = JSON.parse(state_info);
    state = state_info.state;
    state_time = state_info.state_time;

    setStageName(state);
    if (state === "setup") {
        setTime(0);
        stageTimer = false;
        is_timer_paused = null;
        total_game_time = 0;
    } else if (state === "end") {
        playAudio(end_audio);
        setTime(0);
        audio_started = false;
        stopAudio(match_audio);
    } else {
        if (!audio_started) {
            playAudio(start_audio);
            playAudio(match_audio);
            audio_started = true;
        }
        clearTimeout(myStageTimeout);
        prev_curr_time = new Date().getTime() / 1000;
        start_time = state_info.start_time;
        if (start_time != null) {
        setStartTime(start_time);
        }
    }
});

socket.on("scores", (scores) => {
    console.log("Successful ydl message: scores");
    console.log(`scores are ${JSON.stringify(scores)}`);
    scores = JSON.parse(scores);
    ({ blue_score, gold_score } = scores);
    setBlueScore(blue_score);
    setGoldScore(gold_score);
});

socket.on("scores_for_icons", (score_info) => {
    console.log("Successful ydl message: scores_for_icons");
    score_info = JSON.parse(score_info);
    blue_score = score_info.blue_score;
    gold_score = score_info.gold_score;
    setBlueScore(blue_score["score"]);
    setGoldScore(gold_score["score"]);
    updateScores(blue_score["live"]/10, gold_score["live"]/10);
});

socket.on("pause_timer", () => {
    console.log("Successful ydl message: pause_timer");
    if (is_timer_paused == null || !is_timer_paused) {
        is_timer_paused = true;
        clearTimeout(myStageTimeout);
        stageTimer = false;
    }
});

socket.on("resume_timer", (time) => {
    console.log("Successful ydl message: resume_timer");
    if (is_timer_paused) {
        is_timer_paused = false;
        time_info = JSON.parse(time);
        pause_end = time_info.pause_end;
        state_time = time_info.end_time - pause_end;
        stageTimer = true;
        prev_curr_time = new Date().getTime() / 1000;
        runStageTimer(pause_end);
    }
});

function individual(jq_obj) {
    console.log("Inside function: individual");
    let res = Array(jq_obj.length);
    for (let a = 0; a < jq_obj.length; a++) {
        res[a] = $(jq_obj[a]);
    }
    return res;
}

function setTime(time) {
    stageTimer = false;
    $('#timer').html(secondsToTimeString(time));
}

function setBlueScore(score) {
    $('#score-blue').html(score);
}

function setGoldScore(score) {
    $('#score-gold').html(score);
}

function playAudio(a) {
    a.play();
}

function stopAudio(a) {
    a.stop();
    a.time = 0;
}

// these are the stages for the code 
SETUP = "setup"
AUTO = "auto"
TELEOP_1 = "teleop_1"
TELEOP_2 = "teleop_2"
TELEOP_3 = "teleop_3"
END = "end"

stage_names = {
    "setup": "Setup",
    "auto": "Auto",
    "teleop_1": "Teleop",
    "end": "Post-Match"
}

function setStageName(stage) {
    $('#stage').html(stage_names[stage]);
}

function updateTeam(team_name_b1, team_num_b1, team_name_b2, team_num_b2, 
team_name_g1, team_num_g1, team_name_g2, team_num_g2) {
    console.log("Inside function: updateTeam");
    $('#team-name-b1').html(team_name_b1);
    $('#team-num-b1').html(team_num_b1);
    $('#team-name-b2').html(team_name_b2);
    $('#team-num-b2').html(team_num_b2);
    $('#team-name-g1').html(team_name_g1);
    $('#team-num-g1').html(team_num_g1);
    $('#team-name-g2').html(team_name_g2);
    $('#team-num-g2').html(team_num_g2);
}


function setStartTime(start_time) {
// A function that takes in the starting time of the stage as sent by Shepherd. We calculate
// the difference between the current time and the sent timestamp, and set the starting time 
// to be the amount of time given in the round minus the offset.
//
// Args:
// start_time = timestamp sent by Shepherd of when the stage began in seconds
    start_time = start_time / 1000; // seconds

    stageTimerStart(start_time);
}

function stageTimerStart(startTime) {
    stageTimer = true;
    runStageTimer(startTime);
}

function runStageTimer(startTime) {
if (stageTimer) {
    const currTime = new Date().getTime() / 1000;
    let time = state_time - (currTime - startTime);
    if (time < 0 || isNaN(time)) {
    time = 0;
    }
    $('#timer').html(secondsToTimeString(time));

    total_game_time += currTime - prev_curr_time;
    total_game_time = total_game_time > 190 ? 190 : total_game_time;
    prev_curr_time = currTime;

    myStageTimeout = setTimeout(runStageTimer, 200, startTime);
    } else {
        clearTimeout(myStageTimeout);
    }
}

function secondsToTimeString(seconds) {
    const time = Math.floor(Math.abs(seconds));
    return (seconds < 0 ? "-": "") 
        + Math.floor(time / 60) + ":" + ("" + (time % 60)).padStart(2, '0');
    }



function shuffleArray(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }

    return array;
}
});