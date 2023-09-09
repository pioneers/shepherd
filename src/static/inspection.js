//GOOGLE SHEETS CODE for static page 
function gapiLoaded() {
  const API_KEY = 'AIzaSyCtdsxq4_TWBoQU-gZEiA6YVQZUaweN6C8'; //CHANGE
  const DISCOVERY_DOC = 'https://sheets.googleapis.com/$discovery/rest?version=v4';
  gapi.load('client', async () => {
      await gapi.client.init({
          apiKey: API_KEY,
          discoveryDocs: [DISCOVERY_DOC],
      });
      get_teams();
  });
}

async function get_teams() {
  try {
    // fetching the 1 line 
    response = await gapi.client.sheets.spreadsheets.values.get({
      spreadsheetId: '1c9NUoB1prQdrBfAAkaSKJCnIGrAQV8kx5GZKEeIAmWs',
      range: 'Inspection!A2:C7',
    });
    console.log('t', response) //prints shows the spreadsheet values 
  } catch (err) {
    console.log("NOT WORKING")
    document.getElementById('content').innerText = err.message;
    return;
  }

  game_data = response.result.values
  console.log('here is the array', game_data) //printing the range 
  console.log('index show', game_data.at(0)) //printing the first one 




  for (let i = 0; i < game_data.length; i++) {
    //we are printing for each row 
    row = game_data.at(i); //this is the first row 
    document.getElementById('que'+ String(i)).innerHTML = row.at(0); //this places the game_data into the first input
    document.getElementById('insp'+ String(i)).innerHTML = row.at(1);
    document.getElementById('play'+ String(i)).innerHTML = row.at(2);
}
}

//function to keep refreshing for google sheets 
setInterval('get_teams()', 1000);




/* Dynamic website - with the dragging 
function allowDrop(ev) {
  ev.preventDefault();
  console.log("allowDrop");
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
  console.log("drag");

}

function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text");
  ev.target.appendChild(document.getElementById(data));
  console.log("drop");
} */
