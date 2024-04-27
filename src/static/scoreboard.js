var socket = io('/');
// var timerA = true;
// var globaltime = 0;
// var startTime = 0;
var stageTimer = false;
var myStageTimeout;
var state_time;
var state;
var is_timer_paused = null;
var prev_curr_time;
var total_game_time;
var progression_bar;
var start_audio;
var end_audio;

socket.on('connect', (data) => {
  console.log("Successful ydl message: connect");
  socket.emit('join', 'scoreboard');

  // progression_bar = $(".progression-bar");
  start_audio = new Audio('/static/boxing-bell.wav');
  end_audio = new Audio('/static/trim.wav')
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
    setSetupState();
    stageTimer = false;
    is_timer_paused = null;
    total_game_time = 0;
  } else if (state === "end") {
    stageTimer = false;
    is_timer_paused = null;
  } else {
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

socket.on('scores_for_icons', (score_info) => {
  console.log("Successful ydl message: scores_for_icons");
  score_info = JSON.parse(score_info);
  blue_score = score_info.blue_score;
  gold_score = score_info.gold_score;
  setBlueScore(blue_score["score"]);
  setGoldScore(gold_score["score"]);
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

socket.on("play_start_sound", () => {
  console.log("Successful ydl message: play_start_sound");
  start_audio.play();
});

socket.on("play_end_sound", () => {
  console.log("Successful ydl message: play_end_sound");
  end_audio.play();
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
  // globaltime = time;
  $('#timer').html((time));
}

function setBlueScore(score) {
  $('#score-blue').html(score);
}

function setGoldScore(score) {
  $('#score-gold').html(score);
}

// these are the stages for the code 
SETUP = "setup"
AUTO = "auto"
TELEOP_1 = "teleop_1"
END = "end"

stage_names = {
  "setup": "Setup",
  "auto": "Period 1 (Auto)",
  "teleop_1": "Period 1 (Teleop)",
  "end": "Post-Match"
}

function setStageName(stage) {
  $('#stage').html(stage_names[stage]);
}

function updateTeam(team_name_b1, team_num_b1, team_name_b2, team_num_b2, 
  team_name_g1, team_num_g1, team_name_g2, team_num_g2) {
  console.log("Inside function: updateTeam");
  $('#team-name-b1').html(`${team_name_b1} ${team_num_b1}`);
  $('#team-name-b2').html(`${team_name_b2} ${team_num_b2}`);
  $('#team-name-g1').html(`${team_name_g1} ${team_num_g1}`);
  $('#team-name-g2').html(`${team_name_g2} ${team_num_g2}`);
  // $('#team-name-b1').html(team_name_b1);
  // $('#team-num-b1').html(team_num_b1);
  // $('#team-name-b2').html(team_name_b2);
  // $('#team-num-b2').html(team_num_b2);
  // $('#team-name-g1').html(team_name_g1);
  // $('#team-num-g1').html(team_num_g1);
  // $('#team-name-g2').html(team_name_g2);
  // $('#team-num-g2').html(team_num_g2);
}

// function setSetupState() {
//   progression_bar.css("background", "rgb(195, 195, 195)");
// }

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
    // progression_bar.css("background", "linear-gradient(to right, var(--blue500) 0%, var(--blue500) " + (100 * total_game_time / 190) + "%, var(--gold500) " + (100 * total_game_time / 190) + "%, var(--gold500) 100%)")
    prev_curr_time = currTime;

    if (state == "teleop_1") {
      $('#rain-background').css("opacity", `${100 - (100 * time / 180)}%`)
      $('#dark-alcatraz').css("opacity", `${100 - (100 * time / 180)}%`)
      $('#dark-waves').css("opacity", `${100 - (100 * time / 180)}%`)
  
      $('#match').css("color", `${time > 60 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)"}`)
      $('#timer').css("color", `${time > 60 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)"}`)
      $('#stage').css("color", `${time > 60 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)"}`)
      $("#score-blue").css("color", `${time > 60 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)"}`)
      $("#score-gold").css("color", `${time > 60 ? "rgb(0, 0, 0)" : "rgb(255, 255, 255)"}`)

      $("#cloud").css("top", `${-3 - (7 * time / 180)}rem`)
      $("#cloud").css("opacity", `${100 - (100 * time / 180)}%`)
    }


    //MATCH TIME!!! PLEASE FIX THIS!!!
    //console.log(`${100 - (100 * time / 180)}%`)



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


// function buttonHide() {
//   $('.audio-button').hide();
// }

// function shuffleArray(array) {
//   let currentIndex = array.length, randomIndex;
//   while (currentIndex !== 0) {
//     randomIndex = Math.floor(Math.random() * currentIndex);
//     currentIndex--;
//     [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
//   }

//   return array;
// }

// not used???
// function setImageVisible(id, visible) {
//   console.log("Set visible/invisible");
//   $(id).css("visibility", (visible ? 'visible' : 'hidden'));
// }


/*
socket.on('stage_timer_start', (secondsInStage) => {
  time = JSON.parse(secondsInStage).time
  stageTimerStart(time)
})
*/

// not used???
// STAGE{stage, start_time}
// socket.on('stage', (stage_details) => {
//   console.log("Successful ydl message: stage")
//   stage = JSON.parse(stage_details).stage
//   start_time = JSON.parse(stage_details).start_time
//   console.log("got stage header")
//   console.log(stage_details)
//   if (stage === "setup") {
//     setTime(0);
//     setStamp(0);
//     setPenalty(0);
//   } else if (stage === "end") {
//     stageTimer = false;
//   } else {
//     setStageName(stage);
//     if (start_time != null) {
//       setStartTime(start_time);
//     }
//   }
// })


// not used???
// i think this is not used for 2022 game?
// socket.on("reset_timers", () => {
//   console.log("Successful ydl message: reset_timers")
//   resetTimers();
// })


// not used???
// SCORES{time, penalty, stamp_time, score, start_time}
// socket.on("scores", (scores) => {
//   console.log("Successful ydl message: scores")
//   console.log("receiving score");
//   scores = JSON.parse(scores);
//   console.log(`scores are ${JSON.stringify(scores)}`);
//   ({ time, penalty, stamp_time } = scores);

//   console.log("THIS SHOULD PRINT")
//   console.log(time)
//   if (time) {
//     console.log("Setting time")
//     setTime(time);
//     setTotal(time + stamp_time + penalty)
//   }
//   setStamp(stamp_time);
//   setPenalty(penalty);
//   console.log(time)
  
//   // if (time) {
//   //   console.log("Setting total")
//   //   setTotal(time - stamp_time + penalty)
//   // }
// })

// not used???
// updates the stage 
// socket.on("sandstorm", (sandstorm) => {
//   console.log("Successful ydl message: sandstorm")
//   on = JSON.parse(sandstorm).on;
//   if (on) {
//     console.log("Setting sandstorm");
//     setSandstorm();
//   } else {
//     console.log("Removing sandstorm");
//     removeSandstorm();
//   }
// })

// not used???
// function setSandstorm() {
//   $('body').css('background-image', 'url(../static/2.png)');
// }

// not used???
// function removeSandstorm() {
//   $('body').css('background-image', 'url()');
// }


/*
function progress(timeleft, timetotal, $element) {
  var progressBarWidth = timeleft * $element.width() / timetotal;
  if (timeleft == timetotal) {
    $element.find('div').animate({ width: progressBarWidth }, 0, 'linear').html(Math.floor(timeleft / 60) + ":" + pad(timeleft % 60));
  } else {
    $element.find('div').animate({ width: progressBarWidth }, 1000, 'linear').html(Math.floor(timeleft / 60) + ":" + pad(timeleft % 60));
  }
  if (timeleft > 0) {
    setTimeout(function () {
      if (overTimer) {
        progress(timeleft - 1, timetotal, $element);
      } else {
        progress(0, 0, $element)
      }
    }, 1000);
  } else {
    $element.find('div').animate({ width: 0 }, 1000, 'linear').html("")
    $('#overdriveText').css('color', 'white');
    // $('#overdriveText').html("OVERDRIVE!!! " + block + " size!!!");
  }
};

var a = 0
  , pi = Math.PI
  , t = 30

var counter = t;

console.log($("textbox").text() + "x")
console.log(t)

function draw() {
  // a should depend on the amount of time left
  a++;
  a %= 360;
  var r = (a * pi / 180)
    , x = Math.sin(r) * 15000
    , y = Math.cos(r) * - 15000
    , mid = (a > 180) ? 1 : 0
    , anim =
      'M 0 0 v -15000 A 15000 15000 1 '
      + mid + ' 1 '
      + x + ' '
      + y + ' z';
  //[x,y].forEach(function( d ){
  //  d = Math.round( d * 1e3 ) / 1e3;
  //});
  $("#loader").attr('d', anim);
  console.log(counter);

  // time left should be calculated using a timer that runs separately
  if (a % (360 / t) == 0) {
    counter -= 1;
    if (counter <= 9) {
      $("#textbox").css("left = '85px';")
    }
    $("#textbox").html(counter);
  }
  if (a == 0) {
    return;
  }
  setTimeout(draw, 20); // Redraw
};

function runTimer1() {
  timerA = true;
  console.log("timerA set to true")
  console.log(timerA)
  //setTimeout(timer1, 0)
  launchButtonTimer('.timer1', '.circle_animation1', timerA);
}

function timer1() {
  // how long the timer will run (seconds) 

  var time = 30;
  var initialOffset = '440';
  var i = 1;

  // Need initial run as interval hasn't yet occured... 
  $('.circle_animation1').css('stroke-dashoffset', initialOffset - (1 * (initialOffset / time)));

  var interval = setInterval(function () {
    $('.timer1').text(time - i);
    if (i == time || !timerA) {
      clearInterval(interval);
      $('.timer1').text(30);
      $('.circle_animation1').css('stroke-dashoffset', '0')
      return;
    }
    $('.circle_animation1').css('stroke-dashoffset', initialOffset - ((i + 1) * (initialOffset / time)));
    i++;
  }, 1000);

}
*/


/* FOR TESTING: */
// var jq = document.createElement('script');
// jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
// document.getElementsByTagName('head')[0].appendChild(jq);
// // ... give time for script to load, then type (or see below for non wait option)
// jQuery.noConflict();

/*
// not used???
function setStamp(stamp_time) {
  $('#stamp_time').html("-" + secondsToTimeString(-1 * stamp_time));
}

// not used???
function setPenalty(penalty) {
  $('#penalty').html("+" + secondsToTimeString(penalty));
}

// not used???
function setTotal(total) {
  // Hypothetically make it visible here
  console.log("Inside setTotal")
  $('#total').html(secondsToTimeString(total));
  setImageVisible('#total', true);
  setImageVisible('.totalinfo', true);
}

// not used???
function testScore(score) {
  $('#score').html(score);
}

// not used???
function resetTimers() {
  stageTimer = false;
  // timerA = false;
}
*/