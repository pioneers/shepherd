$(document).ready(function () {
    //logg: logs messages to an html element at the bottom of the page

    // let counter = 1;
    // function logg(str) {
    //   let log = document.getElementById("events-log");
    //   let m = log.innerHTML.split("\n");
    //   if (m.length >= 30) m.shift();
    //   log.innerHTML = m.join("\n") + `\n[${counter++}] ` + str;
    // }

    // $("#log-toggle").click(function (e) {
    //   e.preventDefault();
    //   let log = document.getElementById("events-log");
    //   log.hidden = !log.hidden;
    //   localStorage.setItem("log-toggle", !log.hidden);
    // });

    // if (localStorage.getItem("log-toggle") === "true")
    //   document.getElementById("events-log").hidden = false;

    // //In the navbar, adds an "active" tag to current page
    // for (let a of $(".nav-link")) {
    //   if (
    //     a.pathname.replace(/\/+$/, "") ==
    //     location.pathname.replace(/\/+$/, "")
    //   ) {
    //     a.parentElement.classList.add("active");
    //   }
    // }

    // gets a cookie. Pretty much only used for password
    // use localStorage rather than cookies for other cases
    function getCookie(cname) {
      cname += "=";
      let ca = decodeURIComponent(document.cookie).split(";");
      let co = ca.filter((c) => c.indexOf(cname) >= 0);
      if (co.length > 0)
        return co[0].substring(co[0].indexOf(cname) + cname.length);
      else return "";
    }

    //socket: websocket to server.py, gets messages to/from shepherd
    // loggs both incoming and outgoing messages

    var socket = io("/");
    var pass = getCookie("password");
    // socket.onAny((h, m) => logg("← " + h + " " + m));
    function send() {
      socket.emit("ui-to-server", pass, ...arguments);
      let logstr = "";
      try {
        for (let a = 0; a < arguments.length; a++) logstr += arguments[a];
      } catch (err) {
        console.log(err);
        logstr = "[logging error]";
      }
    //   logg(logstr);
    }

    main_js_content(socket, send);
});


// const start_game = $(".start-game");
// const start_game = document.getElementById("start-game");
// const submit_name = $("#submit-name");

// socket.on('connect', (data) => {
//   console.log("Inside function: connect");
//   socket.emit('join', 'whackamole_js');
// });

// socket.on('update_player_score', (score_info) => {
//     console.log(`received update_player_score header with info ${score_info}`);
//     score_info = JSON.parse(score_info);
//     score = score_info.score;
//     $('#total').html(score);
// })

// start_game.click(() => {
//     console.log("Inside onClick function: start_game");
//     start_game.disabled = true;
//     // send("start_whackamole", JSON.stringify({  }));
//   });

// document.getElementById("start-game").onclick = function() {myFunction()};

// function start_game() {
// //   console.log("Inside onClick function: start_game");
// //   document.getElementById("start-game").innerHTML = "YOU CLICKED ME!";
//     console.log("Inside onClick function: start_game");
//     document.getElementById("start-game").disabled = true;
//     send("start_whackamole", JSON.stringify({  }));

// }


function main_js_content(socket, send) {
    //add socket listeners and javascript stuff here
    console.log("Inside function: main_js_content");
    
    const start_game = $("#start-game");
    const submit_name = $("#submit-name");
    const ranking_table = $("#ranking-table");

    var all_player_score = [["Baaa", 0]];

    // function individual(jq_obj) {
    //   console.log("Inside function: individual");
    //   let res = Array(jq_obj.length);
    //   for (let a = 0; a < jq_obj.length; a++) {
    //     res[a] = $(jq_obj[a]);
    //   }
    //   return res;
    // }

    socket.on('connect', (data) => {
        console.log("Inside function: connect");
        socket.emit('join', 'whackamole_js');
    });

    socket.on('update_player_score', (score_info) => {
        console.log(`received update_player_score header with info ${score_info}`);
        score_info = JSON.parse(score_info);
        score = score_info.score;
        document.getElementById("total").innerHTML = score;
    })

    socket.on('whack_a_mole_game_over', () => {
        console.log("received whack_a_mole_game_over header");
        document.getElementById("start-game").style.backgroundColor = "var(--blue500)";
        document.getElementById("start-game").disabled = false;
        document.getElementById("submit-name").style.backgroundColor = "var(--blue500)";
        document.getElementById("submit-name").disabled = false;
        document.getElementById("your-score-game-over").innerHTML = "Game Over!";

        final_score = document.getElementById("total").innerHTML;
        all_player_score.sort(function(a, b) {
            return b[1] - a[1];
        });
        if (parseInt(final_score) > all_player_score[0][1]) {
            document.getElementById("totalinfobackground").style.backgroundColor = "rgba(0, 255, 0, 0.5)";
        }
        else {
            document.getElementById("totalinfobackground").style.backgroundColor = "rgba(255, 0, 0, 0.5)";

        }
    })

    // function start_game() {
    //     //   console.log("Inside onClick function: start_game");
    //     //   document.getElementById("start-game").innerHTML = "YOU CLICKED ME!";
    //     console.log("Inside onClick function: start_game");
    //     document.getElementById("start-game").disabled = true;

    //     send("start_whackamole", JSON.stringify({  }));
        
    // }

    start_game.click(() => {
        console.log("Inside onClick function: start_game");
        document.getElementById("start-game").style.backgroundColor = "gray";
        document.getElementById("start-game").disabled = true;
        document.getElementById("submit-name").style.backgroundColor = "gray";
        document.getElementById("submit-name").disabled = true;
        document.getElementById("your-score-game-over").innerHTML = "Your Score";
        document.getElementById("totalinfobackground").style.backgroundColor = "white";

        send("start_whackamole", JSON.stringify({  }));
    })

    submit_name.click(() => {
        // fruits = [["cscscscs", 70]];
        // fruits.push(["dsdsdsds", 100]);
        // console.log(fruits[1][1]);

        final_score = document.getElementById("total").innerHTML;
        player_name = document.getElementById("player-name").value;
        document.getElementById("player-name").value = "";
        if (player_name == "") {
            return;
        }
        
        // console.log("" + player_name);
        // console.log("" + parseInt(final_score));
        
        all_player_score.push([player_name, parseInt(final_score)]);
        all_player_score.sort(function(a, b) {
            return b[1] - a[1];
        });

        document.getElementById("ranking-table").innerHTML = "";
        ranking_table.append("<tr><th>Name</th><th>Score</th></tr>");
        for (let i = 0; i < all_player_score.length; i++) {
            ranking_table.append("<tr><th>" + all_player_score[i][0] + "</th><th>" + all_player_score[i][1] + "</th></tr>");
        }

        document.getElementById("high-score-banner").innerHTML = "High Score: " + all_player_score[0][0] + " with a score of " + all_player_score[0][1];

    })
    


  }