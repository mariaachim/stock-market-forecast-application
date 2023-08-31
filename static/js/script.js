'use strict'

async function sendRequest(companyID, userID) {
  // for debugging
  console.log("company " + companyID);
  console.log("user " + userID);
  // javascript object for JSON.stringify() function
  let obj = {};
  obj.companyID = companyID;
  obj.userID = userID;
  let resp = await fetch("/stockfavourites", { // returns response to /stocks
    credentials: "same-origin",
    mode: "same-origin",
    method: "post",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(obj) // parses data to JSON
  })
  await resp.json().then(result => {
    console.log(result);
    document.getElementById('msg').innerHTML = result.msg;
  })
}