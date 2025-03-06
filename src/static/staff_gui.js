</script>
{% endblock %} {% block html_content %}

<a
  href=""
  onclick="event.preventDefault(); instructionsText.hidden = !instructionsText.hidden"
  >Toggle instructions</a
>
<div
  id="instructionsText"
  class="bottom-padding"
  style="white-space: pre-wrap"
  hidden
>
  1) Fill in the current match #, then click "populate". This should fill in
  most of the information needed to create the match (you might need to wait for
  a few seconds). Alternatively, you can click the "+" button to increment the
  match # by 1 and populate. 2) Check the robot IPs, then click "connect" on all
  of them. Wait for the corresponding heatbeats to all turn green. 3) Correct
  any incorrect team info, then click "create round". This will move Shepherd
  into the setup state. If you need to correct any info while in setup, click
  "create round" again to save it. 4) Click "start round" to begin the game. If
  something goes wrong, click "reset round" to move Shepherd back into the setup
  state.
</div>

<div class="row">
  <div class="col">
    <div class="input-group bottom-padding">
      <div class="input-group-prepend">
        <span class="input-group-text" id="match-num">Match #</span>
      </div>
      <input type="number" class="form-control" id="select-match-number" />
      <div class="input-group-btn">
        <button type="button" class="btn btn-success" id="next-round">+</button>
        <button type="button" class="btn btn-success" id="select-round">
          Populate
        </button>
      </div>
    </div>
  </div>
</div>

<div class="row">
  <div class="col" style="border: 1px solid black; background: #f0f0ff">
    <h3>Blue Team 1</h3>
    <div class="input-group mb-1">
      Team #: <input type="number" class="form-control team-num-input" />
    </div>
    <div class="input-group mb-1">
      Team Name: <input type="text" class="form-control team-name-input" />
    </div>
    <div class="input-group mb-1">
      Starting Position:
      <input type="number" class="form-control team-starting-position-input" />
    </div>
    <div class="input-group mb-1">
      IP:
      <input
        type="text"
        class="form-control robot-ip-input"
        placeholder="0.0.0.0"
      />
      <button class="btn btn-success robot-connect-button" type="button">
        Connect
      </button>
    </div>
    <div class="input-group mb-1">
      <span style="margin-right: 5px">Heartbeat:</span>
      <div class="heartbeat-light"></div>
      <span class="heartbeat-message"></span>
    </div>
  </div>
  <div class="col" style="border: 1px solid black; background: #f0f0ff">
    <h3>Blue Team 2</h3>
    <div class="input-group mb-1">
      Team #: <input type="number" class="form-control team-num-input" />
    </div>
    <div class="input-group mb-1">
      Team Name: <input type="text" class="form-control team-name-input" />
    </div>
    <div class="input-group mb-1">
      Starting Position:
      <input type="number" class="form-control team-starting-position-input" />
    </div>
    <div class="input-group mb-1">
      IP:
      <input
        type="text"
        class="form-control robot-ip-input"
        placeholder="0.0.0.0"
      />
      <button class="btn btn-success robot-connect-button" type="button">
        Connect
      </button>
    </div>
    <div class="input-group mb-1">
      <span style="margin-right: 5px">Heartbeat:</span>
      <div class="heartbeat-light"></div>
      <span class="heartbeat-message"></span>
    </div>
  </div>
</div>
<div class="row">
  <div class="col" style="border: 1px solid black; background: #fffff0">
    <h3>Gold Team 1</h3>
    <div class="input-group mb-1">
      Team #: <input type="number" class="form-control team-num-input" />
    </div>
    <div class="input-group mb-1">
      Team Name: <input type="text" class="form-control team-name-input" />
    </div>
    <div class="input-group mb-1">
      Starting Position:
      <input type="number" class="form-control team-starting-position-input" />
    </div>
    <div class="input-group mb-1">
      IP:
      <input
        type="text"
        class="form-control robot-ip-input"
        placeholder="0.0.0.0"
      />
      <button class="btn btn-success robot-connect-button" type="button">
        Connect
      </button>
    </div>
    <div class="input-group mb-1">
      <span style="margin-right: 5px">Heartbeat:</span>
      <div class="heartbeat-light"></div>
      <span class="heartbeat-message"></span>
    </div>
  </div>
  <div class="col" style="border: 1px solid black; background: #fffff0">
    <h3>Gold Team 2</h3>
    <div class="input-group mb-1">
      Team #: <input type="number" class="form-control team-num-input" />
    </div>
    <div class="input-group mb-1">
      Team Name: <input type="text" class="form-control team-name-input" />
    </div>
    <div class="input-group mb-1">
      Starting Position:
      <input type="number" class="form-control team-starting-position-input" />
    </div>
    <div class="input-group mb-1">
      IP:
      <input
        type="text"
        class="form-control robot-ip-input"
        placeholder="0.0.0.0"
      />
      <button class="btn btn-success robot-connect-button" type="button">
        Connect
      </button>
    </div>
    <div class="input-group mb-1">
      <span style="margin-right: 5px">Heartbeat:</span>
      <div class="heartbeat-light"></div>
      <span class="heartbeat-message"></span>
    </div>
  </div>
</div>

<div class="row bottom-padding">
  <div class="col" style="border: 1px solid black">
    <h3>Meta</h3>
    <div class="input-group">
      <span>State: <span id="state-msg">None</span></span>
    </div>
  </div>
</div>

<div class="row bottom-padding">
  <div class="btn-group" role="group" aria-label="...">
    <button type="button" class="btn btn-success spaced" id="create-match">
      <span class="glyphicon glyphicon-play" aria-hidden="true"></span>Create
      Match
    </button>
    <button type="button" class="btn btn-success spaced" id="match-start">
      <span class="glyphicon glyphicon-play" aria-hidden="true"></span>Start
      Match
    </button>
    <button type="button" class="btn btn-danger spaced" id="match-reset">
      <span class="glyphicon glyphicon-fast-backward" aria-hidden="true"></span
      >Reset Match
    </button>
    <button type="button" class="btn btn-danger spaced" id="pause-timers">
      <span class="glyphicon glyphicon-fast-backward" aria-hidden="true"></span
      >Pause Timers
    </button>
    <button type="button" class="btn btn-danger spaced" id="resume-timers">
      <span class="glyphicon glyphicon-fast-backward" aria-hidden="true"></span
      >Resume Timers
    </button>
  </div>
</div>

{% endblock %}
