var socket = io('http://192.168.128.129:5500'); // io('http://127.0.0.1:5500')
var stageTimer = true;
var timerA = true;

socket.on('connect', function(data) {
    socket.emit('join', 'scoreboard');
  });

socket.on('team', function(match_info) {
  team_name = JSON.parse(match_info).team_name
  team_num = JSON.parse(match_info).team_num
  nextTeam(team_name, team_num)
})

socket.on('stage_timer_start', function(secondsInStage) {
    time = JSON.parse(secondsInStage).time
    stageTimerStart(time)
})

// STAGE{stage, start_time}
socket.on('stage', function(stage_details) {
  stage = JSON.parse(stage_details).stage
  start_time = JSON.parse(stage_details).start_time
  console.log("got stage header")
  console.log(stage)
  setStageName(stage)
  setStartTime(start_time)
})

socket.on("reset_timers", function() {
  resetTimers();
})


// SCORES{time, penalty, stamp_time, total}
socket.on("score", function(scores) {
  time = JSON.parse(scores).time;

  total = JSON.parse(scores).total;           //displayed?
  penalty = JSON.parse(scores).penalty;
  stamp_time = JSON.parse(scores).stamp_time;

  setStamp(stamp_time);
  setPenalty(penalty);
})

function setStamp(stamp_time) {
  $('#stamp_time').html(stamp_time);
}

function setPenalty(penalty) {
  $('#penalty').html(penalty);
}

function setTotal(total) {
  $('#total').html(total);
}

function testScore(score) {
  $('#score').html(score);
}

function resetTimers(){
  stageTimer = false;
  timerA = false;
}

SETUP = "setup"
AUTO_WAIT = "auto_wait"
AUTO = "auto"
WAIT = "wait"
TELEOP = "teleop"
END = "end"

stage_names = {"setup": "Setup",
               "auto_wait": "Autonomous Wait", "auto": "Autonomous Period",
               "teleop": "Teleop Period", "end": "Post-Match"}

function setStageName(stage) {
  $('#stage').html(stage_names[stage])
}

function nextTeam(team_name, team_num){
  //set the name and numbers of the school and the match number jk
  $('#team-name').html(team_name)
  $('#team-num').html("Team " + team_num)

  // TODO: Figure out how to reset main timer
}

function stageTimerStart(currTime) {
  stageTimer = true;
  runStageTimer(currTime);
}

function runStageTimer(currTime) {
  var maxStageTime = 300;
  if(currTime <= maxStageTime){
    setTimeout(function() {
      $('#stage-timer').html(Math.floor(currTime/60) + ":"+ pad(currTime%60))
      if(stageTimer) {
        stageTimerStart(currTime + 1);
      } else {
        stageTimerStart(0)
        $('#stage-timer').html("0:00")
      }
  }, 1000);
  }
}

function pad(number) {
  return (number < 10 ? '0' : '') + number
}

function setImageVisible(id, visible) {
  $(id).css("visibility", (visible ? 'visible' : 'hidden'));
}

function progress(timeleft, timetotal, $element) {
    var progressBarWidth = timeleft * $element.width() / timetotal;
    if (timeleft == timetotal) {
        $element.find('div').animate({ width: progressBarWidth }, 0, 'linear').html(Math.floor(timeleft/60) + ":"+ pad(timeleft%60));
    } else {
        $element.find('div').animate({ width: progressBarWidth }, 1000, 'linear').html(Math.floor(timeleft/60) + ":"+ pad(timeleft%60));
    }
    if (timeleft > 0) {
        setTimeout(function() {
            if(overTimer) {
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
  var r = ( a * pi / 180 )
    , x = Math.sin( r ) * 15000
  , y = Math.cos( r ) * - 15000
  , mid = ( a > 180 ) ? 1 : 0
    , anim =
        'M 0 0 v -15000 A 15000 15000 1 '
           + mid + ' 1 '
           +  x  + ' '
           +  y  + ' z';
  //[x,y].forEach(function( d ){
  //  d = Math.round( d * 1e3 ) / 1e3;
  //});
  $("#loader").attr( 'd', anim );
  console.log(counter);

  // time left should be calculated using a timer that runs separately
  if (a % (360 / t) == 0){
    counter -= 1;
    if (counter <= 9) {
      $("#textbox").css("left = '85px';")
    }
    $("#textbox").html(counter);
  }
  if (a == 0){
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
  /* how long the timer will run (seconds) */

  var time = 30;
  var initialOffset = '440';
  var i = 1;

  /* Need initial run as interval hasn't yet occured... */
  $('.circle_animation1').css('stroke-dashoffset', initialOffset-(1*(initialOffset/time)));

  var interval = setInterval(function() {
      $('.timer1').text(time - i);
      if (i == time||!timerA) {  	
        clearInterval(interval);
        $('.timer1').text(30);
        $('.circle_animation1').css('stroke-dashoffset', '0')
        return;
      }
      $('.circle_animation1').css('stroke-dashoffset', initialOffset-((i+1)*(initialOffset/time)));
      i++;
  }, 1000);

}

function setStartTime(start_time) {
  // A function that takes in the starting time of the stage as sent by Shepherd. We calculate
  // the difference between the current time and the sent timestamp, and set the starting time 
  // to be the amount of time given in the round minus the offset.
  //
  // Args:
  // start_time = timestamp sent by Shepherd of when the stage began in seconds
  var curr_time = new Date().getTime() / 1000;

  stageTimerStart(curr_time - start_time)
}

/* FOR TESTING: */
// var jq = document.createElement('script');
// jq.src = "https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js";
// document.getElementsByTagName('head')[0].appendChild(jq);
// // ... give time for script to load, then type (or see below for non wait option)
// jQuery.noConflict();