var socket = io('/');
var stageTimer = false;
// var timerA = true;
// var globaltime = 0;
// var startTime = 0;
var myStageTimeout;
var state_time;
var state;
var prevStateBlizzard = false;
var prev_start_time;
var campsite_resource;
var campsite_satellite_icon;
var campsite_pioneer_icon;
var endgame_pioneer_icon;
var campsite_pioneer_icon_background;

socket.on('connect', (data) => {
  console.log("Successful ydl message: connect");
  socket.emit('join', 'scoreboard');

  campsite_resource = individual($(".campsite-resource-icon, .campsite-resource-middle-icon"));
  campsite_satellite_icon = individual($(".campsite-satellite-icon-circle-border"));
  campsite_pioneer_icon = individual($(".campsite-pioneer-icon"));
  endgame_pioneer_icon = individual($(".endgame-pioneer-blue-container, .endgame-pioneer-gold-container"));
  campsite_pioneer_icon_background = individual($(".campsite-pioneer-icon-background"));
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

// USE STATE, NOT STAGE
socket.on('state', (state_info) => {
  console.log("Successful ydl message: state");
  console.log(`received team header with info ${state_info}`);
  state_info = JSON.parse(state_info);
  state = state_info.state;
  state_time = state_info.state_time;

  if (prevStateBlizzard && !(state === "blizzard")) {
    prevStateBlizzard = false;
    setSpaceBackground();
  }

  if (state === "setup") {
    setStageName(state);
    setTime(0);
  } else if (state === "end") {
    setStageName(state);
    stageTimer = false;
  } else {
    if (state === "blizzard") {
      prevStateBlizzard = true;
      setBlizzardBackground();
    }
    setStageName(state);
    clearTimeout(myStageTimeout);
    start_time = state_info.start_time;
    if (start_time != null) {
      prev_start_time = start_time;
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

socket.on("pause_timer", () => {
  console.log("Successful ydl message: pause_timer");
  clearTimeout(myStageTimeout);
  stageTimer = false;
});

socket.on("resume_timer", (start_time) => {
  console.log("Successful ydl message: resume_timer");
  start_time_info = JSON.parse(start_time);

  stageTimer = true;
  runStageTimer((new Date().getTime() / 1000) - (start_time_info.start_time - prev_start_time / 1000));
});

socket.on("scores_for_icons", (score_info) => {
  score_info = JSON.parse(score_info);
  blue_score = score_info.blue_score;
  gold_score = score_info.gold_score;

  setBlueScore(blue_score["score"]);
  setGoldScore(gold_score["score"]);

  const blue_resource = [
    blue_score["campsite-resource-top-left-leftside"],
    blue_score["campsite-resource-bottom-left-leftside"],
    blue_score["campsite-resource-top-middle-leftside"],
    blue_score["campsite-resource-bottom-middle-leftside"],
    blue_score["campsite-resource-top-right-leftside"],
    blue_score["campsite-resource-bottom-right-leftside"]
  ];
  const blue_satellite = [
    blue_score["campsite-satellite-top-left"],
    blue_score["campsite-satellite-bottom-left"],
    blue_score["campsite-satellite-top-middle"],
    blue_score["campsite-satellite-bottom-middle"],
    blue_score["campsite-satellite-top-right"],
    blue_score["campsite-satellite-bottom-right"]
  ];
  const blue_pioneer = [
    blue_score["campsite-pioneer-top-left"],
    blue_score["campsite-pioneer-bottom-left"],
    blue_score["campsite-pioneer-top-middle"],
    blue_score["campsite-pioneer-bottom-middle"],
    blue_score["campsite-pioneer-top-right"],
    blue_score["campsite-pioneer-bottom-right"]
  ];
  
  const gold_resource = [
    gold_score["campsite-resource-top-left-rightside"],
    gold_score["campsite-resource-bottom-left-rightside"],
    gold_score["campsite-resource-top-middle-rightside"],
    gold_score["campsite-resource-bottom-middle-rightside"],
    gold_score["campsite-resource-top-right-rightside"],
    gold_score["campsite-resource-bottom-right-rightside"]    
  ];
  const gold_satellite = [
    gold_score["campsite-satellite-top-left"],
    gold_score["campsite-satellite-bottom-left"],
    gold_score["campsite-satellite-top-middle"],
    gold_score["campsite-satellite-bottom-middle"],
    gold_score["campsite-satellite-top-right"],
    gold_score["campsite-satellite-bottom-right"]
  ];
  const gold_pioneer = [
    gold_score["campsite-pioneer-top-left"],
    gold_score["campsite-pioneer-bottom-left"],
    gold_score["campsite-pioneer-top-middle"],
    gold_score["campsite-pioneer-bottom-middle"],
    gold_score["campsite-pioneer-top-right"],
    gold_score["campsite-pioneer-bottom-right"]
  ];

  const blue_endgame_pioneer = blue_score["endgame-pioneer-blue"];
  const gold_endgame_pioneer = gold_score["endgame-pioneer-gold"];

  for (let a = 0; a < blue_resource.length; a++) {
    for (let b = 0, c = blue_resource[a] > 3 ? 3 : blue_resource[a]; b < c ; b++) {
      campsite_resource[a * 6 + b].css("background-color", "var(--blue500)");
    }
    for (let b = blue_resource[a] > 3 ? 3 : blue_resource[a]; b < 3 ; b++) {
      campsite_resource[a * 6 + b].css("background-color", "white");
    }
  }
  for (let a = 0; a < gold_resource.length; a++) {
    for (let b = 0, c = gold_resource[a] > 3 ? 3 : gold_resource[a]; b < c ; b++) {
      campsite_resource[a * 6 + 3 + b].css("background-color", "var(--gold500)");
    }
    for (let b = gold_resource[a] > 3 ? 3 : gold_resource[a]; b < 3 ; b++) {
      campsite_resource[a * 6 + 3 + b].css("background-color", "white");
    }
  }

  for (let a = 0; a < blue_satellite.length && a < gold_satellite.length; a++) {
    if (blue_satellite[a] == true && gold_satellite[a] == true) {
      console.log("ERROR: Both Blue and Gold teams cannot control the same satellite!");
      campsite_satellite_icon[a].css("background-color", "black");
      continue;
    }
    if (blue_satellite[a]) {
      campsite_satellite_icon[a].css("background-color", "var(--blue500)");
    }
    else if (gold_satellite[a]) {
      campsite_satellite_icon[a].css("background-color", "var(--gold500)");
    }
    else {
      campsite_satellite_icon[a].css("background-color", "black");
    }
  }

  for (let a = 0; a < blue_pioneer.length && a < gold_pioneer.length; a++) {
    if (blue_pioneer[a] == true && gold_pioneer[a] == true) {
      campsite_pioneer_icon[a].css("background-color", "rgba(0, 0, 0, 0)");
      campsite_pioneer_icon_background[a].css("background", "linear-gradient(to right, var(--blue500) 0%, var(--blue500) 50%, var(--gold500) 50%, var(--gold500) 100%)")
    }
    else if (blue_pioneer[a]) {
      campsite_pioneer_icon_background[a].css("background", "transparent")
      campsite_pioneer_icon[a].css("background-color", "var(--blue500)");
    }
    else if (gold_pioneer[a]) {
      campsite_pioneer_icon_background[a].css("background", "transparent")
      campsite_pioneer_icon[a].css("background-color", "var(--gold500)");
    }
    else {
      campsite_pioneer_icon_background[a].css("background", "transparent")
      campsite_pioneer_icon[a].css("background-color", "black");
    }
  }

  if ((blue_endgame_pioneer > 0 || gold_endgame_pioneer > 0) && state !== "endgame") {
    console.log("ERROR: Cannot set endgame pioneer scores until endgame has started!");
  }
  else {
    for (let a = 0; a < blue_endgame_pioneer; a++) {
      endgame_pioneer_icon[a].show();
    }
    for (let a = blue_endgame_pioneer; a < 4; a++) {
      endgame_pioneer_icon[a].hide();
    }
    for (let a = 0; a < gold_endgame_pioneer; a++) {
      endgame_pioneer_icon[a + 4].show();
    }
    for (let a = gold_endgame_pioneer; a < 4; a++) {
      endgame_pioneer_icon[a + 4].hide();
    }  
  }
});

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
  $('#stage-timer').html(secondsToTimeString(time));
}

function setBlueScore(score) {
  $('#score-blue').html(score);
}

function setGoldScore(score) {
  $('#score-gold').html(score);
}

function setBlizzardBackground() {
  $('body').css('background-image', 'url(../static/test-blizzard-background-2.jpg)');
}

function setSpaceBackground() {
  $('body').css('background-image', 'url(../static/space-background.png)');
}

// these are the stages for the code 
SETUP = "setup"
AUTO_WAIT = "auto_wait"
AUTO = "auto"
WAIT = "wait"
TELEOP = "teleop"
END = "end"

stage_names = {
  "setup": "Setup",
  "auto_wait": "Autonomous Wait", 
  "auto": "Autonomous Period",
  "teleop_1": "Teleop (Pre-Blizzard)",
  "blizzard": "Blizzard",
  "teleop_2": "Teleop (Post-Blizzard)", 
  "endgame": "Endgame Period",
  "end": "Post-Match"
}

function setStageName(stage) {
  $('#stage').html(stage_names[stage]);
}

function updateTeam(team_name_b1, team_num_b1, team_name_b2, team_num_b2, 
  team_name_g1, team_num_g1, team_name_g2, team_num_g2) {
  console.log("Inside function: updateTeam");
  $('#team-name-b1').html(team_name_b1);
  $('#team-num-b1').html("Team " + team_num_b1);
  $('#team-name-b2').html(team_name_b2);
  $('#team-num-b2').html("Team " + team_num_b2);
  $('#team-name-g1').html(team_name_g1);
  $('#team-num-g1').html("Team " + team_num_g1);
  $('#team-name-g2').html(team_name_g2);
  $('#team-num-g2').html("Team " + team_num_g2);
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
    $('#stage-timer').html(secondsToTimeString(time));
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

// not used???
function setImageVisible(id, visible) {
  console.log("Set visible/invisible");
  $(id).css("visibility", (visible ? 'visible' : 'hidden'));
}

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
